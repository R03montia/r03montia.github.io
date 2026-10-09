#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""挂机锁 · 个人站「退出挂机」的本机锁定工具（仅 Windows）。

工作原理
--------
挂机页（/idle）会主动探测本机 127.0.0.1:38472 上的这个小服务：
  * 探测到 -> 点「退出挂机」时网页调用 /lock，本工具弹一块全屏锁；
    锁定期间用一个低级键盘钩子吞掉**所有**按键（含 Win / Alt+Tab / Alt+F4 /
    Ctrl+Esc 等逃生键），把密码逐个攒起来自己校验——不依赖窗口焦点，也不会
    把按键漏给别的窗口。密码正确才解锁、放行退出。
  * 探测不到（手机或别的电脑打开网页）-> 网页按正常流程直接退出，与本工具无关。

HTTP 接口（监听 127.0.0.1:38472）
  GET /ping    -> {"app":"idle-lock","ok":true,"version":1}
  GET /status  -> {"locked":bool,"buf":int,"hook":bool}
  GET /lock    -> 弹锁并挂起，直到解锁（密码正确）后返回 {"ok":true,"unlocked":true}

密码
----
从同目录 password.txt 读取（该文件已被 .gitignore 忽略，不会进仓库）。
文件缺失或为空时 /lock 直接返回失败，网页照常退出——不会把人锁死。

退出本工具
----------
锁定时唯一的出路：输入正确密码，或 Ctrl+Alt+Del 打开任务管理器结束本进程
（这是操作系统保留的安全通道，任何程序都拦不住，也是刻意的兜底）。
未锁定时：直接关掉控制台窗口即可。

注意
----
密码写在本地文件里，属于“防误触/防他人随手动电脑”的软锁，不是抗破解的安全边界；
本服务只监听 127.0.0.1，不对外网开放。
"""

import ctypes
import json
import os
import queue
import threading
import time
import tkinter as tk
from ctypes import wintypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 38472  # 若被系统保留/占用，改这里并同步改 src/pages/idle.astro 的 IDLE_LOCK_API
APP_ID = "idle-lock"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORD_FILE = os.path.join(ROOT_DIR, "password.txt")

# ---- 共享状态（跨线程） ----
lock_request: "queue.Queue[bool]" = queue.Queue()
_state = {"locked": False, "password": "", "events": []}
_guard = threading.Lock()
_app = None  # 由 LockApp 实例回填，供钩子回调改缓冲


def read_password() -> str:
    try:
        with open(PASSWORD_FILE, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return ""


# ---- Windows 低级键盘钩子 ----
# 锁定期间吞掉全部按键：正常的字母/数字攒进密码缓冲，其余（含各种逃生键）一律拦截。
# 钩子跑在专门的线程里自己泵消息——若挂在 Tk 主线程上，回调会被塞进 Tk 的 C 主循环，
# 触发 “PyEval_RestoreThread ... thread state is NULL” 致命错误。
WH_KEYBOARD_LL = 13
WM_KEYDOWN, WM_SYSKEYDOWN = 0x0100, 0x0104
WM_QUIT = 0x0012
VK_BACK, VK_RETURN = 0x08, 0x0D

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

LRESULT = ctypes.c_ssize_t
LowLevelKeyboardProc = ctypes.WINFUNCTYPE(
    LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


_hook_handle = None
_hook_proc = None
_hook_thread = None
_hook_thread_id = 0
_hook_ready = threading.Event()


def _char_for_vk(vk: int):
    # 主键盘字母（统一转小写，密码不含大写）、主键盘数字、小键盘数字
    if 0x41 <= vk <= 0x5A:
        return chr(vk).lower()
    if 0x30 <= vk <= 0x39:
        return chr(vk)
    if 0x60 <= vk <= 0x69:
        return chr(0x30 + (vk - 0x60))
    return None


def _keyboard_proc(n_code, w_param, l_param):
    if n_code != 0:
        return user32.CallNextHookEx(None, n_code, w_param, l_param)
    try:
        app = _app
        if not _state["locked"] or app is None:
            return user32.CallNextHookEx(None, n_code, w_param, l_param)
        if w_param in (WM_KEYDOWN, WM_SYSKEYDOWN):
            kb = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk = kb.vkCode
            ch = _char_for_vk(vk)
            if ch is not None:
                app.push_char(ch)
            elif vk == VK_BACK:
                app.pop_char()
            elif vk == VK_RETURN:
                app.request_submit()
            # 其余按键（Win、Alt+Tab、Escape……）什么都不做，直接吞掉
        return 1  # 锁定期间所有按键都不放行
    except Exception:
        return 1


def _hook_pump() -> None:
    global _hook_handle, _hook_proc, _hook_thread_id
    _hook_thread_id = kernel32.GetCurrentThreadId()
    _hook_proc = LowLevelKeyboardProc(_keyboard_proc)
    _hook_handle = user32.SetWindowsHookExW(WH_KEYBOARD_LL, _hook_proc, None, 0)
    if not _hook_handle:
        print(
            f"[idle-lock] 键盘钩子安装失败 (err={ctypes.get_last_error()})，"
            "锁定期间无法拦截按键。",
            flush=True,
        )
        _hook_ready.set()
        return

    _hook_ready.set()
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    # 收到 WM_QUIT：收钩子、线程退出
    if _hook_handle:
        user32.UnhookWindowsHookEx(_hook_handle)
        _hook_handle = None
    _hook_proc = None


def start_hook() -> None:
    global _hook_thread, _hook_thread_id
    if _hook_thread is not None and _hook_thread.is_alive():
        return
    _hook_ready.clear()
    _hook_thread_id = 0
    _hook_thread = threading.Thread(target=_hook_pump, daemon=True)
    _hook_thread.start()
    _hook_ready.wait(1.5)


def stop_hook() -> None:
    global _hook_thread_id
    _hook_ready.wait(1.0)
    if _hook_thread_id:
        user32.PostThreadMessageW(_hook_thread_id, WM_QUIT, 0, 0)
        _hook_thread_id = 0


class LockApp:
    """主线程里的 Tk 应用：负责弹/收全屏锁；密码缓冲由键盘钩子线程写入。"""

    def __init__(self) -> None:
        global _app
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = None
        self.clock_label = None
        self.display = None
        self.err_label = None
        self.clock_job = None
        self.buffer = ""
        self._needs_render = False
        self._submit_pending = False
        _app = self
        self.root.after(50, self._drain)

    def _drain(self) -> None:
        # 主线程每 50ms：处理 /lock 请求、刷新密码显示、处理回车提交
        try:
            while True:
                lock_request.get_nowait()
                self._show_lock()
        except queue.Empty:
            pass
        if self._needs_render:
            self._needs_render = False
            self._render()
        if self._submit_pending:
            self._submit_pending = False
            self._do_submit()
        self.root.after(50, self._drain)

    def _show_lock(self) -> None:
        if self.win is not None:
            self.win.lift()
            self.win.focus_force()
            return

        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()

        win = tk.Toplevel(self.root)
        self.win = win
        win.overrideredirect(True)
        win.geometry(f"{width}x{height}+0+0")
        win.configure(bg="#0b0d12")
        win.attributes("-topmost", True)
        try:
            win.attributes("-alpha", 0.97)
        except tk.TclError:
            pass

        box = tk.Frame(win, bg="#0b0d12")
        box.place(relx=0.5, rely=0.5, anchor="center")

        self.clock_label = tk.Label(
            box, text="", fg="#c7ccd6", bg="#0b0d12", font=("Consolas", 60)
        )
        self.clock_label.pack(pady=(0, 6))
        tk.Label(
            box,
            text="已启用挂机锁",
            fg="#8b93a1",
            bg="#0b0d12",
            font=("Microsoft YaHei UI", 12),
        ).pack(pady=(0, 20))

        # 纯展示用的密码框：内容由键盘钩子攒出来的 buffer 渲染，不接收真实输入
        self.display = tk.Label(
            box,
            text="输入密码",
            fg="#4a4f5a",
            bg="#161a22",
            font=("Consolas", 18),
            width=16,
            height=1,
            padx=8,
            pady=8,
        )
        self.display.pack()

        self.err_label = tk.Label(
            box, text="", fg="#d98b8b", bg="#0b0d12", font=("Microsoft YaHei UI", 10)
        )
        self.err_label.pack(pady=(10, 0))
        tk.Label(
            box,
            text="输入密码后按回车解锁",
            fg="#5c6270",
            bg="#0b0d12",
            font=("Microsoft YaHei UI", 10),
        ).pack(pady=(14, 0))

        self.buffer = ""
        self._needs_render = False
        self._submit_pending = False
        self._render()

        _state["locked"] = True
        start_hook()

        win.lift()
        win.focus_force()
        try:
            win.grab_set()
        except tk.TclError:
            pass
        self._tick()

    def _tick(self) -> None:
        if self.win is None:
            return
        self.clock_label.config(text=time.strftime("%H:%M:%S"))
        self.win.attributes("-topmost", True)
        self.clock_job = self.win.after(1000, self._tick)

    def _render(self) -> None:
        if self.display is None:
            return
        if self.buffer:
            self.display.config(text="●" * len(self.buffer), fg="#e6e9ef")
        else:
            self.display.config(text="输入密码", fg="#4a4f5a")

    # 下面三个方法在键盘钩子线程里被调用：只动纯 Python 状态，绝不碰 Tk。
    def push_char(self, ch: str) -> None:
        if len(self.buffer) < 64:
            self.buffer += ch
        self._needs_render = True

    def pop_char(self) -> None:
        self.buffer = self.buffer[:-1]
        self._needs_render = True

    def request_submit(self) -> None:
        self._submit_pending = True

    def _do_submit(self) -> None:
        if _state["password"] and self.buffer == _state["password"]:
            self._unlock()
            return
        self.buffer = ""
        self._render()
        if self.err_label is not None:
            self.err_label.config(text="密码错误")

    def _unlock(self) -> None:
        if self.clock_job and self.win:
            try:
                self.win.after_cancel(self.clock_job)
            except Exception:
                pass
        self.clock_job = None
        stop_hook()
        if self.win is not None:
            self.win.destroy()
            self.win = None
        self.clock_label = None
        self.display = None
        self.err_label = None
        self.buffer = ""
        with _guard:
            _state["locked"] = False
            events = _state["events"]
            _state["events"] = []
        for ev in events:
            ev.set()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_args) -> None:  # 静音默认访问日志
        pass

    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/ping":
            self._send(200, {"app": APP_ID, "ok": True, "version": 1})
        elif path == "/status":
            self._send(
                200,
                {
                    "locked": _state["locked"],
                    "buf": len(_app.buffer) if _app else -1,
                    "hook": bool(_hook_handle),
                },
            )
        elif path == "/lock":
            if not _state["password"]:
                self._send(200, {"ok": False, "error": "no-password"})
                return
            ev = threading.Event()
            with _guard:
                _state["events"].append(ev)
            lock_request.put(True)
            ev.wait()  # 一直挂起，直到主线程解锁
            self._send(200, {"ok": True, "unlocked": True})
        else:
            self._send(404, {"ok": False, "error": "not-found"})


def enable_dpi_awareness() -> None:
    # 高 DPI 下让 Tk 用物理像素，保证全屏窗口真正铺满整块屏幕
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def main() -> None:
    enable_dpi_awareness()
    _state["password"] = read_password()
    if not _state["password"]:
        print(
            f"[idle-lock] 警告：未找到 {PASSWORD_FILE} 或内容为空，/lock 将直接放行。",
            flush=True,
        )

    app = LockApp()

    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError as exc:
        print(f"[idle-lock] 端口 {PORT} 被占用，无法启动本地服务：{exc}", flush=True)
        return

    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(
        f"[idle-lock] 挂机锁已就绪：http://{HOST}:{PORT} "
        f"(密码{'已加载' if _state['password'] else '缺失'})",
        flush=True,
    )

    try:
        app.root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        stop_hook()
        server.shutdown()


if __name__ == "__main__":
    main()
