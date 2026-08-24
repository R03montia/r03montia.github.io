# 个人博客站实施计划（Astro 5 + trauma 版式）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建部署到 `https://r03montia.github.io/` 的纯中文个人博客站：首页 / 博客 / 项目 / 关于四个栏目，trauma（创伤）版式风格 + rainy 下雨氛围。

**Architecture:** Astro 5 静态站。内容集合管理博客文章（Markdown），项目数据用 JSON；全局 CSS 变量（RGB 三元组）驱动 trauma 配色与明暗模式；GitHub Actions 构建并发布到 GitHub Pages 主仓库。

**Tech Stack:** Astro 5、@astrojs/rss、@fontsource 自托管字体（Nixie One / Outfit / Atkinson Hyperlegible）、GitHub Actions。

**Spec:** `docs/superpowers/specs/2026-08-24-personal-website-design.md`

## Global Constraints

- **执行环境**：本会话在 Windows 侧，项目实际位于 WSL。所有 node/npm 命令必须通过 `wsl.exe -d Ubuntu-24.04 -- sh -c 'cd /root/code/personal-website && <命令>'` 执行；git 命令可直接在当前目录执行（已加 safe.directory）。文件读写工具直接用 Windows 路径 `\\wsl.localhost\Ubuntu-24.04\root\code\personal-website\...`。
- **代理**：npm 安装需带代理环境变量 `HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897`。
- **Node 版本**：WSL 内为 v18.19.1（满足 Astro 5 最低要求 18.17.1），不要升级。
- **站点地址**：`site: 'https://r03montia.github.io'`，根路径部署，无 base path。
- **语言**：全站界面文案为中文。
- **配色实现**：一律 RGB 三元组 CSS 变量 + `rgb(var(--x) / α)` 派生透明度；禁止散落硬编码色值。
- **中文字体不加载 webfont**（访客在国内，Google Fonts 不可靠）：中文走系统字体栈；仅拉丁装饰字体用 @fontsource 自托管。
- **验证方式**：静态站无单测框架，每个任务的验证 = `npx astro build` 通过 + 用 grep/curl 断言构建产物 `dist/` 中出现预期内容。构建命令统一为 `wsl.exe -d Ubuntu-24.04 -- sh -c 'cd /root/code/personal-website && HTTPS_PROXY=http://127.0.0.1:7897 npx astro build'`（下文简写「构建」）。
- **提交规范**：每任务结束 commit 一次，message 用 conventional commits 中文描述。
- 第一版不做：站内搜索、评论、双语、文章页独立变体版式。

---

### Task 1: Astro 项目脚手架

**Files:**
- Create: `package.json`, `astro.config.mjs`, `tsconfig.json`, `.gitignore`, `public/favicon.svg`
- Create: `src/pages/index.astro`（临时占位页）

**Interfaces:**
- Produces: 可构建的 Astro 项目；后续所有任务依赖 `src/` 目录结构与 `.gitignore`。

- [ ] **Step 1: 写入脚手架文件**

`package.json`：

```json
{
  "name": "personal-website",
  "type": "module",
  "version": "0.0.1",
  "private": true,
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "@astrojs/rss": "^4.0.12",
    "astro": "^5.12.0"
  }
}
```

`astro.config.mjs`：

```js
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://r03montia.github.io',
});
```

`tsconfig.json`：

```json
{
  "extends": "astro/tsconfigs/base",
  "include": [".astro/types.d.ts", "**/*"],
  "exclude": ["dist"]
}
```

`.gitignore`：

```
node_modules/
dist/
.astro/
```

`public/favicon.svg`（黑白方块书页图标，贴合黑白基调）：

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="4" fill="#161616"/>
  <path d="M8 9h7l1 2h8v12H8z" fill="none" stroke="#e1e1e1" stroke-width="2"/>
</svg>
```

临时占位首页 `src/pages/index.astro`：

```astro
---
---
<html lang="zh-CN">
  <head><meta charset="utf-8"><title>占位</title></head>
  <body>占位页</body>
</html>
```

- [ ] **Step 2: 安装依赖**

```bash
wsl.exe -d Ubuntu-24.04 -- sh -c 'cd /root/code/personal-website && HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 npm install'
```

预期：生成 `node_modules/` 与 `package-lock.json`，无 error。

- [ ] **Step 3: 构建**

运行：构建（见 Global Constraints 定义）
预期：`dist/index.html` 生成，包含「占位页」。

```bash
grep -q "占位页" dist/index.html && echo PASS
```

- [ ] **Step 4: Commit**

```bash
git add package.json package-lock.json astro.config.mjs tsconfig.json .gitignore public/favicon.svg src/
git commit -m "chore: Astro 5 项目脚手架"
```

---

### Task 2: 内容集合定义与示例内容

**Files:**
- Create: `src/content.config.ts`
- Create: `src/content/blog/hello-world.md`
- Create: `src/content/blog/site-launch.md`
- Create: `src/content/blog/css-silhouette-notes.md`
- Create: `src/data/projects.json`
- Create: `src/utils/posts.ts`

**Interfaces:**
- Produces: 内容集合 `blog`（schema：`title/date/tags/description`，均必填，date 为 date 类型）；`src/data/projects.json` 数组结构 `{ name, description, tech: string[], url }`；工具函数 `sortPosts(posts)` 与 `readingTime(text): number`（返回分钟数，CJK 字符按 400 字/分钟、英文词按 200 词/分钟折算，向上取整，最少 1 分钟）。

- [ ] **Step 1: 写内容集合配置**

`src/content.config.ts`：

```ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    tags: z.array(z.string()).default([]),
  }),
});

export const collections = { blog };
```

- [ ] **Step 2: 写三篇示例文章**

`src/content/blog/hello-world.md`：

```markdown
---
title: 你好，世界
description: 站点的第一篇文章，记录为什么要在 2026 年开始写博客。
date: 2026-08-24
tags: [meta, 写作]
---

这是本站的第一篇文章。

为什么要写博客？因为想法留在脑子里会发霉，写在别处会丢失，而放在自己的域名下至少看起来比较体面。

## 这里会有什么

- 技术笔记
- 一些不成体系的想法
- 偶尔的生活记录

更新频率随缘。
```

`src/content/blog/site-launch.md`：

```markdown
---
title: 站点上线小记
description: 从零搭起这个站点的过程：技术选型、版式参考与部署方案。
date: 2026-08-24
tags: [meta, 设计]
---

本站基于 Astro 构建，静态输出，部署在 GitHub Pages。

## 版式

视觉上参考了 trauma 版式的极简思路：浅灰底、白色半透明卡片、底部城市剪影，外加雨天氛围层。

## 部署

push 到 main 分支即自动构建发布，全程无服务器。
```

`src/content/blog/css-silhouette-notes.md`：

```markdown
---
title: 用纯 CSS 画城市剪影
description: 三层固定定位的剪影背景就能做出视差感，不需要任何 JavaScript。
date: 2026-08-23
tags: [CSS, 设计]
---

做氛围感背景最便宜的手段：三层 `position: fixed; bottom: 0` 的剪影，配不同透明度。

滚动时前景卡片移动而背景不动，天然形成层次。再叠一层雨丝动画，气氛就到位了。
```

- [ ] **Step 3: 写项目数据**

`src/data/projects.json`：

```json
[
  {
    "name": "personal-website",
    "description": "本站源码：Astro 静态博客，trauma 版式风格。",
    "tech": ["Astro", "CSS", "TypeScript"],
    "url": "https://github.com/R03montia/personal-website"
  },
  {
    "name": "示例项目占位",
    "description": "第二个项目的占位描述，替换成真实项目即可。",
    "tech": ["Python"],
    "url": "https://github.com/R03montia"
  }
]
```

- [ ] **Step 4: 写文章工具函数**

`src/utils/posts.ts`：

```ts
export interface PostLike {
  data: { date: Date };
}

export function sortPosts<T extends PostLike>(posts: T[]): T[] {
  return [...posts].sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

export function readingTime(text: string): number {
  const cjkChars = (text.match(/[一-鿿]/g) ?? []).length;
  const latinWords = (text.replace(/[一-鿿]/g, ' ').match(/[A-Za-z0-9]+/g) ?? []).length;
  const minutes = Math.ceil(cjkChars / 400 + latinWords / 200);
  return Math.max(1, minutes);
}
```

- [ ] **Step 5: 构建验证**

运行：构建
预期：成功，无 schema 报错。

- [ ] **Step 6: Commit**

```bash
git add src/content.config.ts src/content src/data src/utils
git commit -m "feat: 博客内容集合、项目数据与示例内容"
```

---

### Task 3: trauma 风格全局样式（含 rainy 层、剪影、明暗模式）

**Files:**
- Create: `src/styles/global.css`
- Modify: `package.json`（加三个 @fontsource 字体依赖）

**Interfaces:**
- Produces: 全局 CSS 变量体系（`:root` 亮色 / `[data-theme=dark]` 暗色 / `[data-rainy]` 雨天调色）与类名约定，后续组件直接使用：
  - 变量：`--body-bg`、`--content-bg`、`--text`、`--text-secondary`、`--line`、`--accent`（均为 RGB 三元组字符串）
  - 类：`.silhouettes > .sky-l{1,2,3}`（三层剪影）、`.rain-overlay`（雨幕层）、`.card`（白色半透明卡片）
- 字体导入方式：`@fontsource/nixie-one`、`@fontsource/outfit`、`@fontsource/atkinson-hyperlegible` 的默认 css 导入。

- [ ] **Step 1: 安装字体包**

```bash
wsl.exe -d Ubuntu-24.04 -- sh -c 'cd /root/code/personal-website && HTTPS_PROXY=http://127.0.0.1:7897 HTTP_PROXY=http://127.0.0.1:7897 npm install @fontsource/nixie-one @fontsource/outfit @fontsource/atkinson-hyperlegible'
```

- [ ] **Step 2: 写全局样式**

`src/styles/global.css`：

```css
/* ===== trauma 版式 · RGB 三元组色彩系统 ===== */
:root {
  /* 默认亮色 */
  --body-bg: 225, 225, 225;
  --content-bg: 255, 255, 255;
  --text: 35, 35, 38;
  --text-secondary: 110, 110, 115;
  --line: 160, 160, 165;
  --accent: 90, 100, 130;

  --font-deco: 'Nixie One', 'Outfit', serif;
  --font-ui: 'Outfit', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  --font-body: 'Atkinson Hyperlegible', 'Georgia',
    'Noto Serif CJK SC', 'Source Han Serif SC', 'SimSun', serif;
}

/* 暗色模式 */
[data-theme='dark'] {
  --body-bg: 24, 26, 28;
  --content-bg: 33, 36, 39;
  --text: 200, 202, 206;
  --text-secondary: 140, 142, 148;
  --line: 70, 74, 80;
  --accent: 130, 145, 185;
}

/* rainy 预设：冷灰蓝调 */
[data-rainy] {
  --body-bg: 205, 212, 220;
  --accent: 70, 90, 125;
}
[data-theme='dark'][data-rainy] {
  --body-bg: 18, 21, 26;
}

* {
  box-sizing: border-box;
}

html {
  background: rgb(var(--body-bg));
  color: rgb(var(--text));
  font-family: var(--font-body);
  line-height: 1.75;
  transition: background-color 0.4s ease, color 0.4s ease;
}

body {
  margin: 0;
  min-height: 100vh;
}

a {
  color: rgb(var(--accent));
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}

::selection {
  background: rgb(var(--accent) / 0.25);
}

/* ===== 白色半透明内容卡片（trauma 核心）===== */
.card {
  background: rgb(var(--content-bg) / 0.9);
  box-shadow: 0 0 2.5rem -1rem rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(4px);
}

/* ===== 三层城市剪影 ===== */
.silhouettes {
  position: fixed;
  inset: auto 0 0 0;
  height: 40vh;
  pointer-events: none;
  z-index: 0;
}
.silhouettes svg {
  position: absolute;
  inset: auto 0 0 0;
  width: 100%;
  height: 100%;
}
.sky-l1 { opacity: 0.15; height: 55% !important; }
.sky-l2 { opacity: 0.09; height: 75% !important; }
.sky-l3 { opacity: 0.05; }

/* ===== rainy 雨幕层 ===== */
.rain-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  opacity: 0.06;
  background-image: repeating-linear-gradient(
    105deg,
    transparent 0 11px,
    rgb(var(--text)) 11px 12px
  );
  background-size: 200% 200%;
  animation: rainfall 0.9s linear infinite;
}
@keyframes rainfall {
  from { background-position: 0 0; }
  to { background-position: -120px 240px; }
}
@media (prefers-reduced-motion: reduce) {
  .rain-overlay { animation: none; }
}

.skip-link {
  position: absolute;
  left: -999px;
  top: 0;
  background: rgb(var(--content-bg));
  color: rgb(var(--text));
  padding: 0.5rem 1rem;
  z-index: 99;
}
.skip-link:focus {
  left: 0;
}
```

- [ ] **Step 3: 构建验证**

运行：构建
预期：通过（样式尚未被引用，仅确认 CSS 无语法错误被 Vite 处理——此步若报错说明语法问题）。

- [ ] **Step 4: Commit**

```bash
git add src/styles/global.css package.json package-lock.json
git commit -m "feat: trauma 风格全局样式（RGB 三元组变量/rainy 雨幕/城市剪影/暗色模式）"
```

---

### Task 4: BaseLayout 布局骨架（侧边栏 + 移动端导航 + 明暗切换）

**Files:**
- Create: `src/layouts/BaseLayout.astro`
- Create: `src/components/Sidebar.astro`
- Create: `src/components/MobileNav.astro`

**Interfaces:**
- Consumes: Task 3 的全部 CSS 变量与类名。
- Produces: `BaseLayout` 组件，props 为 `{ title: string; description?: string }`，default slot 为页面主体。导航数据结构 `navItems = [{ href: '/', label: '首页', icon: 'home' }, { href: '/blog/', label: '博客', icon: 'pen' }, { href: '/projects/', label: '项目', icon: 'code' }, { href: '/about/', label: '关于', icon: 'user' }]` 在 Sidebar/MobileNav 中各自内联一份（两处一致，避免跨组件传参复杂化）。

- [ ] **Step 1: 写 Sidebar 组件**

`src/components/Sidebar.astro`：

```astro
---
const items = [
  { href: '/', label: '首页', icon: 'home' },
  { href: '/blog/', label: '博客', icon: 'pen' },
  { href: '/projects/', label: '项目', icon: 'code' },
  { href: '/about/', label: '关于', icon: 'user' },
];
const icons: Record<string, string> = {
  home: '<path d="M3 10.5L12 4l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-9.5z"/><path d="M9 21V13h6v8"/>',
  pen: '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>',
  code: '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
};
const current = Astro.url.pathname;
const isActive = (href: string) =>
  href === '/' ? current === '/' : current.startsWith(href);
---
<aside class="sidebar">
  <a class="brand" href="/">
    <span class="brand-name">R03montia</span>
    <span class="brand-sub">@R03montia</span>
  </a>
  <nav aria-label="主导航">
    {items.map((it) => (
      <a class:list={['side-link', { active: isActive(it.href) }]} href={it.href} aria-current={isActive(it.href) ? 'page' : undefined}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" set:html={icons[it.icon]} />
        <span>{it.label}</span>
      </a>
    ))}
  </nav>
  <div class="side-foot">
    <a class="social" href="https://github.com/R03montia" target="_blank" rel="noopener noreferrer">GitHub</a>
    <button id="theme-toggle" type="button" aria-label="切换明暗模式">明 / 暗</button>
  </div>
</aside>

<style>
  .sidebar {
    position: sticky;
    top: 0;
    height: 100vh;
    width: 14rem;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 2rem;
    padding: 2rem 1.25rem;
    border-right: 1px solid rgb(var(--line) / 0.4);
  }
  .brand { display: flex; flex-direction: column; color: inherit; }
  .brand-name { font-family: var(--font-ui); font-size: 1.15rem; letter-spacing: 0.05em; }
  .brand-sub { font-size: 0.75rem; color: rgb(var(--text-secondary)); }
  nav { display: flex; flex-direction: column; gap: 0.25rem; }
  .side-link {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.65rem;
    border-radius: 6px;
    color: rgb(var(--text));
    font-family: var(--font-ui);
    font-size: 0.92rem;
  }
  .side-link:hover { background: rgb(var(--content-bg) / 0.7); text-decoration: none; }
  .side-link.active { background: rgb(var(--content-bg) / 0.9); box-shadow: 0 1px 0 rgb(var(--line) / 0.4); }
  .side-link svg { width: 17px; height: 17px; }
  .side-foot { margin-top: auto; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
  .social { color: rgb(var(--text-secondary)); }
  #theme-toggle {
    border: 1px solid rgb(var(--line) / 0.6);
    background: rgb(var(--content-bg) / 0.6);
    color: rgb(var(--text));
    border-radius: 6px;
    padding: 0.3rem 0.6rem;
    cursor: pointer;
    font-family: var(--font-ui);
  }
</style>
```

- [ ] **Step 2: 写 MobileNav 组件**

`src/components/MobileNav.astro`：

```astro
---
const items = [
  { href: '/', label: '首页' },
  { href: '/blog/', label: '博客' },
  { href: '/projects/', label: '项目' },
  { href: '/about/', label: '关于' },
];
const current = Astro.url.pathname;
const isActive = (href: string) =>
  href === '/' ? current === '/' : current.startsWith(href);
---
<nav class="mobile-nav" aria-label="移动端导航">
  {items.map((it) => (
    <a href={it.href} class:list={[{ active: isActive(it.href) }]} aria-current={isActive(it.href) ? 'page' : undefined}>{it.label}</a>
  ))}
</nav>

<style>
  .mobile-nav { display: none; }
  @media (max-width: 48rem) {
    .mobile-nav {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      z-index: 50;
      display: flex;
      justify-content: space-around;
      padding: 0.4rem 0 max(0.4rem, env(safe-area-inset-bottom));
      background: rgb(var(--content-bg) / 0.95);
      backdrop-filter: blur(8px);
      border-top: 1px solid rgb(var(--line) / 0.4);
      font-family: var(--font-ui);
      font-size: 0.8rem;
    }
    .mobile-nav a { color: rgb(var(--text-secondary)); padding: 0.25rem 0.75rem; }
    .mobile-nav a.active { color: rgb(var(--text)); }
  }
</style>
```

- [ ] **Step 3: 写 BaseLayout**

`src/layouts/BaseLayout.astro`：

```astro
---
import '@fontsource/nixie-one';
import '@fontsource/outfit';
import '@fontsource/atkinson-hyperlegible';
import '../styles/global.css';
import Sidebar from '../components/Sidebar.astro';
import MobileNav from '../components/MobileNav.astro';

interface Props {
  title: string;
  description?: string;
}
const { title, description = 'R03montia 的个人站点。' } = Astro.props;
---
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content={description} />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <title>{title}</title>
    <script is:inline>
      (() => {
        const saved = localStorage.getItem('theme');
        const dark = saved ? saved === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.toggleAttribute('data-theme', dark);
        if (dark) document.documentElement.setAttribute('data-theme', 'dark');
      })();
    </script>
  </head>
  <body data-rainy>
    <a class="skip-link" href="#main-content">跳到主内容</a>
    <div class="app">
      <Sidebar />
      <main id="main-content" class="main-area">
        <slot />
      </main>
    </div>
    <div class="silhouettes" aria-hidden="true">
      <svg class="sky-l1" preserveAspectRatio="none" viewBox="0 0 1200 120"><path fill="rgb(var(--text))" d="M0 120V60h30V40h20v20h40V30h25v30h35V50h30v70zM260 120V45h28V25h18v20h30v25h40V35h26v85zM520 120V55h35V35h22v20h33V15h20v105zM740 120V50h30V30h20v20h35v50zM900 120V40h26V20h20v20h32v80zM1040 120V55h30V35h22v85z"/></svg>
      <svg class="sky-l2" preserveAspectRatio="none" viewBox="0 0 1200 120"><path fill="rgb(var(--text))" d="M0 120V70h50V50h30v20h45V35h28v85zM180 120V60h35V40h22v80zM300 120V45h40V25h20v95zM420 120V65h45V45h25v75zM560 120V50h30V30h24v90zM700 120V70h40V50h26v70zM840 120V40h35V20h22v100zM980 120V60h42V42h26v78zM1110 120V50h34V32h24v88z"/></svg>
      <svg class="sky-l3" preserveAspectRatio="none" viewBox="0 0 1200 120"><path fill="rgb(var(--text))" d="M0 120V85h60V65h35v20h50V55h32v65zM250 120V75h45V58h26v62zM400 120V90h55V68h30v52zM560 120V72h40V56h28v64zM720 120V82h48V64h30v56zM900 120V68h42V52h28v68zM1060 120V78h50V60h30v60z"/></svg>
    </div>
    <div class="rain-overlay" aria-hidden="true"></div>
    <slot name="after-main" />
    <MobileNav />
    <script>
      document.getElementById('theme-toggle')?.addEventListener('click', () => {
        const root = document.documentElement;
        const dark = root.getAttribute('data-theme') !== 'dark';
        if (dark) root.setAttribute('data-theme', 'dark');
        else root.removeAttribute('data-theme');
        localStorage.setItem('theme', dark ? 'dark' : 'light');
      });
    </script>
  </body>
</html>

<style>
  .app { display: flex; min-height: 100vh; }
  .main-area {
    flex: 1;
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: 60rem;
    margin: 0 auto;
    padding: 2.5rem 1.5rem calc(5rem + env(safe-area-inset-bottom));
  }
  @media (max-width: 48rem) {
    .app { display: block; }
    .sidebar { display: none; }
    .main-area { padding-top: 1.5rem; }
  }
</style>
```

- [ ] **Step 4: 把首页换成真实骨架验证**

将 `src/pages/index.astro` 整体替换为：

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout title="R03montia">
  <h1>R03montia</h1>
  <p>布局骨架验证页。</p>
</BaseLayout>
```

- [ ] **Step 5: 构建验证**

运行：构建，然后：

```bash
grep -q 'id="theme-toggle"' dist/index.html && grep -q 'silhouettes' dist/index.html && grep -q 'mobile-nav' dist/index.html && echo PASS
```

预期：PASS。

- [ ] **Step 6: 本地肉眼检查（可选但推荐）**

```bash
wsl.exe -d Ubuntu-24.04 -- sh -c 'cd /root/code/personal-website && HTTPS_PROXY=http://127.0.0.1:7897 npx astro dev --host' 
```

在 Windows 浏览器打开 `http://localhost:4321` 确认：浅灰底白卡片感、三层剪影、雨丝动画、点「明 / 暗」可切暗色。检查后 Ctrl+C 停掉。

- [ ] **Step 7: Commit**

```bash
git add src/layouts src/components src/pages/index.astro
git commit -m "feat: BaseLayout 布局骨架（侧边栏/移动导航/明暗切换/剪影与雨幕层）"
```

---

### Task 5: 文章卡片组件与博客列表页（含标签索引）

**Files:**
- Create: `src/components/PostCard.astro`
- Create: `src/pages/blog/index.astro`
- Create: `src/pages/tag/[tag].astro`

**Interfaces:**
- Consumes: `sortPosts()`（Task 2）、内容集合 `blog`、BaseLayout。
- Produces: `PostCard` 组件，prop `post: CollectionEntry<'blog'>`，渲染标题/日期/description/阅读时长/#标签（标签链至 `/tag/<tag>/`）。路由产物：`/blog/`、`/tag/<标签名>/`。

- [ ] **Step 1: 写 PostCard**

`src/components/PostCard.astro`：

```astro
---
import type { CollectionEntry } from 'astro:content';
import { readingTime } from '../utils/posts';

interface Props {
  post: CollectionEntry<'blog'>;
}
const { post } = Astro.props;
const { title, date, tags, description } = post.data;
const fmt = new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
---
<a class="post-card card" href={`/blog/${post.id}/`}>
  <div class="pc-head">
    <h3>{title}</h3>
    <time datetime={date.toISOString()}>{fmt.format(date)}</time>
  </div>
  <p class="pc-desc">{description}</p>
  <div class="pc-meta">
    <span>约 {readingTime(post.body ?? '')} 分钟</span>
    {tags.map((t) => <span class="tag">#{t}</span>)}
  </div>
</a>

<style>
  .post-card {
    display: block;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    color: inherit;
    transition: transform 0.15s ease;
  }
  .post-card:hover { text-decoration: none; transform: translateY(-2px); }
  .pc-head { display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; }
  h3 { margin: 0; font-family: var(--font-ui); font-size: 1.05rem; }
  time { color: rgb(var(--text-secondary)); font-size: 0.8rem; white-space: nowrap; }
  .pc-desc { color: rgb(var(--text-secondary)); font-size: 0.9rem; margin: 0.4rem 0 0.6rem; }
  .pc-meta { display: flex; flex-wrap: wrap; gap: 0.75rem; font-size: 0.78rem; color: rgb(var(--text-secondary)); }
  .tag { color: rgb(var(--accent)); }
</style>
```

- [ ] **Step 2: 写博客列表页**

`src/pages/blog/index.astro`：

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';
import PostCard from '../../components/PostCard.astro';
import { sortPosts } from '../../utils/posts';

const posts = sortPosts(await getCollection('blog'));
const allTags = [...new Set(posts.flatMap((p) => p.data.tags))];
---
<BaseLayout title="博客 | R03montia" description="全部文章。">
  <h1 class="page-title">博客</h1>
  <div class="tag-row">
    {allTags.map((t) => <a class="tag-pill" href={`/tag/${t}/`}>#{t}</a>)}
  </div>
  <div class="post-list">
    {posts.map((p) => <PostCard post={p} />)}
  </div>
</BaseLayout>

<style>
  .page-title { font-family: var(--font-ui); }
  .tag-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0 0 1.5rem; }
  .tag-pill {
    font-size: 0.8rem;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    border: 1px solid rgb(var(--line) / 0.5);
    color: rgb(var(--text-secondary));
  }
  .post-list { display: grid; gap: 0.9rem; }
</style>
```

- [ ] **Step 3: 写标签归档页**

`src/pages/tag/[tag].astro`：

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';
import PostCard from '../../components/PostCard.astro';
import { sortPosts } from '../../utils/posts';

export async function getStaticPaths() {
  const posts = await getCollection('blog');
  const tags = [...new Set(posts.flatMap((p) => p.data.tags))];
  return tags.map((tag) => ({ params: { tag } }));
}

const { tag } = Astro.params;
const posts = sortPosts(await getCollection('blog', (p) => p.data.tags.includes(tag!)));
---
<BaseLayout title={`#${tag} | R03montia`} description={`标签 #${tag} 下的全部文章。`}>
  <h1 class="page-title">#{tag}</h1>
  <p><a href="/blog/">← 返回全部文章</a></p>
  <div class="post-list">
    {posts.map((p) => <PostCard post={p} />)}
  </div>
</BaseLayout>

<style>
  .page-title { font-family: var(--font-ui); }
  .post-list { display: grid; gap: 0.9rem; }
</style>
```

注意：`getStaticPaths` 必须导出在 frontmatter 顶部（Astro 要求其不含对未导入符号的引用，以上代码自洽）。

- [ ] **Step 4: 构建验证**

运行：构建，然后：

```bash
test -f dist/blog/index.html && test -f "dist/tag/meta/index.html" && grep -q "你好，世界" dist/blog/index.html && echo PASS
```

预期：PASS。

- [ ] **Step 5: Commit**

```bash
git add src/components/PostCard.astro src/pages/blog src/pages/tag
git commit -m "feat: 博客列表页与标签归档页"
```

---

### Task 6: 文章详情页（阅读时长 + 标签 + 悬浮目录）

**Files:**
- Create: `src/pages/blog/[slug].astro`

**Interfaces:**
- Consumes: `readingTime()`（Task 2）、`render()` 来自 `astro:content`（返回 `{ Content, headings }`，headings 元素为 `{ depth: number; slug: string; text: string }`）。
- Produces: 路由 `/blog/<slug>/`；slug 即 md 文件名。

- [ ] **Step 1: 写详情页**

`src/pages/blog/[slug].astro`：

```astro
---
import { getCollection, render } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';
import { readingTime } from '../../utils/posts';

export async function getStaticPaths() {
  const posts = await getCollection('blog');
  return posts.map((post) => ({ params: { slug: post.id }, props: { post } }));
}

const { post } = Astro.props;
const { Content, headings } = await render(post);
const toc = headings.filter((h) => h.depth >= 2 && h.depth <= 3);
const fmt = new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
---
<BaseLayout title={`${post.data.title} | R03montia`} description={post.data.description}>
  <article class="post-card card post">
    <header>
      <h1>{post.data.title}</h1>
      <div class="meta">
        <time datetime={post.data.date.toISOString()}>{fmt.format(post.data.date)}</time>
        <span>约 {readingTime(post.body ?? '')} 分钟</span>
        {post.data.tags.map((t) => <a href={`/tag/${t}/`}>#{t}</a>)}
      </div>
    </header>
    {toc.length > 1 && (
      <aside class="toc card">
        <div class="toc-title">目录</div>
        <ul>
          {toc.map((h) => (
            <li class:list={[`d${h.depth}`]}><a href={`#${h.slug}`}>{h.text}</a></li>
          ))}
        </ul>
      </aside>
    )}
    <div class="prose">
      <Content />
    </div>
  </article>
</BaseLayout>

<style>
  .post { border-radius: 12px; padding: 2rem clamp(1.2rem, 4vw, 2.5rem); margin-bottom: 4rem; }
  h1 { font-family: var(--font-ui); line-height: 1.3; }
  .meta { display: flex; flex-wrap: wrap; gap: 1rem; font-size: 0.82rem; color: rgb(var(--text-secondary)); margin-bottom: 1.5rem; }
  .toc { position: fixed; top: 6rem; right: max(1rem, calc(50vw - 44rem)); width: 13rem; border-radius: 10px; padding: 0.8rem 1rem; font-size: 0.78rem; }
  .toc-title { font-family: var(--font-ui); margin-bottom: 0.4rem; color: rgb(var(--text-secondary)); }
  .toc ul { list-style: none; margin: 0; padding: 0; }
  .toc li.d3 { padding-left: 0.9rem; }
  .toc a { color: rgb(var(--text-secondary)); }
  .prose :global(h2) { font-family: var(--font-ui); border-bottom: 1px solid rgb(var(--line) / 0.4); padding-bottom: 0.3rem; scroll-margin-top: 2rem; }
  .prose :global(h3) { font-family: var(--font-ui); scroll-margin-top: 2rem; }
  .prose :global(blockquote) { margin: 1rem 0; padding: 0.2rem 1rem; border-left: 0.3rem solid rgb(var(--accent) / 0.7); background: rgb(var(--content-bg) / 0.6); }
  .prose :global(code) { background: rgb(var(--text) / 0.08); padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.88em; }
  .prose :global(pre) { background: rgb(var(--text) / 0.92); color: rgb(var(--content-bg)); padding: 1rem 1.2rem; border-radius: 8px; overflow-x: auto; }
  .prose :global(pre code) { background: none; color: inherit; padding: 0; }
  .prose :global(img) { max-width: 100%; filter: grayscale(1); transition: filter 0.3s ease; }
  .prose :global(img:hover) { filter: grayscale(0); }
  @media (max-width: 78rem) { .toc { display: none; } }
</style>
```

- [ ] **Step 2: 构建验证**

运行：构建，然后：

```bash
test -f "dist/blog/hello-world/index.html" && grep -q "这里会有什么" dist/blog/hello-world/index.html && grep -qi "分钟" dist/blog/hello-world/index.html && echo PASS
```

预期：PASS。

- [ ] **Step 3: Commit**

```bash
git add src/pages/blog/\[slug\].astro
git commit -m "feat: 文章详情页（阅读时长/标签/悬浮目录）"
```

---

### Task 7: 首页、项目页、关于页、404 页

**Files:**
- Modify: `src/pages/index.astro`（替换 Task 4 占位版）
- Create: `src/pages/projects/index.astro`
- Create: `src/pages/about.astro`
- Create: `src/pages/404.astro`

**Interfaces:**
- Consumes: BaseLayout、PostCard、`sortPosts`、`src/data/projects.json`。
- Produces: 完整四栏目路由。

- [ ] **Step 1: 首页**

`src/pages/index.astro` 整体替换为：

```astro
---
import { getCollection } from 'astro:content';
import BaseLayout from '../layouts/BaseLayout.astro';
import PostCard from '../components/PostCard.astro';
import { sortPosts } from '../utils/posts';

const recent = sortPosts(await getCollection('blog')).slice(0, 5);
---
<BaseLayout title="R03montia" description="R03montia 的个人站点：博客、项目与关于。">
  <section class="hero card">
    <h1>R03montia</h1>
    <p>写代码，也写字。</p>
  </section>
  <section class="recent">
    <h2>最近更新</h2>
    <div class="list">
      {recent.map((p) => <PostCard post={p} />)}
    </div>
    <a class="more" href="/blog/">浏览全部 →</a>
  </section>
</BaseLayout>

<style>
  .hero { border-radius: 12px; padding: 2.5rem 2rem; margin-bottom: 2.5rem; }
  .hero h1 { margin: 0; font-family: var(--font-deco); font-weight: 400; font-size: clamp(2.2rem, 6vw, 3.5rem); letter-spacing: 0.02em; }
  .hero p { margin: 0.5rem 0 0; color: rgb(var(--text-secondary)); }
  .recent h2 { font-family: var(--font-ui); font-size: 1.1rem; }
  .list { display: grid; gap: 0.9rem; }
  .more { display: inline-block; margin-top: 1rem; font-family: var(--font-ui); font-size: 0.9rem; }
</style>
```

- [ ] **Step 2: 项目页**

`src/pages/projects/index.astro`：

```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';
import projects from '../../data/projects.json';
---
<BaseLayout title="项目 | R03montia" description="我做过和正在做的项目。">
  <h1 class="page-title">项目</h1>
  <div class="grid">
    {projects.map((p) => (
      <a class="proj card" href={p.url} target="_blank" rel="noopener noreferrer">
        <h2>{p.name}</h2>
        <p>{p.description}</p>
        <div class="tech">{p.tech.map((t) => <span>{t}</span>)}</div>
      </a>
    ))}
  </div>
</BaseLayout>

<style>
  .page-title { font-family: var(--font-ui); }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr)); gap: 1rem; }
  .proj { display: block; border-radius: 10px; padding: 1.2rem 1.4rem; color: inherit; transition: transform 0.15s ease; }
  .proj:hover { text-decoration: none; transform: translateY(-2px); }
  .proj h2 { margin: 0; font-family: var(--font-ui); font-size: 1rem; }
  .proj p { color: rgb(var(--text-secondary)); font-size: 0.87rem; }
  .tech { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .tech span { font-size: 0.72rem; border: 1px solid rgb(var(--line) / 0.5); border-radius: 999px; padding: 0.05rem 0.5rem; color: rgb(var(--text-secondary)); }
</style>
```

- [ ] **Step 3: 关于页**

`src/pages/about.astro`：

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout title="关于 | R03montia" description="关于本站与本站主人。">
  <article class="card about">
    <h1>关于</h1>
    <p>你好，我是 R03montia。</p>
    <p>这里是我在网上的自留地：记录技术笔记、想法和一些生活碎片。</p>
    <p>联系方式见 <a href="https://github.com/R03montia" target="_blank" rel="noopener noreferrer">GitHub</a>。</p>
  </article>
</BaseLayout>

<style>
  .about { border-radius: 12px; padding: 2rem clamp(1.2rem, 4vw, 2.5rem); }
  h1 { font-family: var(--font-ui); }
</style>
```

- [ ] **Step 4: 404 页**

`src/pages/404.astro`：

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout title="404 | R03montia">
  <div class="lost card">
    <h1>404</h1>
    <p>这一页被雨冲走了。</p>
    <a href="/">回首页</a>
  </div>
</BaseLayout>

<style>
  .lost { border-radius: 12px; padding: 4rem 2rem; text-align: center; }
  h1 { font-family: var(--font-deco); font-weight: 400; font-size: 4rem; margin: 0; }
</style>
```

- [ ] **Step 5: 构建验证**

运行：构建，然后：

```bash
grep -q "最近更新" dist/index.html && test -f dist/projects/index.html && test -f dist/about/index.html && test -f dist/404.html && echo PASS
```

预期：PASS。

- [ ] **Step 6: Commit**

```bash
git add src/pages
git commit -m "feat: 首页/项目/关于/404 页面"
```

---

### Task 8: RSS 订阅

**Files:**
- Create: `src/pages/rss.xml.js`

**Interfaces:**
- Consumes: `getCollection`、`@astrojs/rss` 包（Task 1 已装）、`sortPosts`。
- Produces: `/rss.xml` 路由，输出标题+链接+日期+描述。

- [ ] **Step 1: 写 RSS 端点**

`src/pages/rss.xml.js`：

```js
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { sortPosts } from '../utils/posts';

export async function GET(context) {
  const posts = sortPosts(await getCollection('blog'));
  return rss({
    title: 'R03montia',
    description: 'R03montia 的个人站点。',
    site: context.site,
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description,
      pubDate: post.data.date,
      link: `/blog/${post.id}/`,
    })),
  });
}
```

- [ ] **Step 2: 在 BaseLayout 头部加 RSS 发现链接**

修改 `src/layouts/BaseLayout.astro`，在 `<link rel="icon" ...>` 之后加一行：

```html
<link rel="alternate" type="application/rss+xml" title="R03montia" href="/rss.xml" />
```

- [ ] **Step 3: 构建验证**

运行：构建，然后：

```bash
grep -q "<rss" dist/rss.xml && grep -q "hello-world" dist/rss.xml && echo PASS
```

预期：PASS。

- [ ] **Step 4: Commit**

```bash
git add src/pages/rss.xml.js src/layouts/BaseLayout.astro
git commit -m "feat: RSS 订阅"
```

---

### Task 9: GitHub Actions 部署工作流

**Files:**
- Create: `.github/workflows/deploy.yml`

**Interfaces:**
- Produces: push 到 `main` 触发的 Pages 构建发布流水线。

- [ ] **Step 1: 写工作流**

`.github/workflows/deploy.yml`：

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: withastro/action@v3

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: 本地构建复验（模拟 CI）**

运行：构建
预期：通过。CI 使用 `withastro/action` 会自动跑 `npm ci && npm run build`，本地等价已验证。

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: GitHub Pages 自动部署工作流"
```

---

### Task 10: 上线（需要用户配合的一次性步骤）

**Files:**
- 无新文件；远程仓库操作。

**Interfaces:**
- Consumes: Task 9 工作流、Task 1 的 `site` 配置。
- Produces: `https://r03montia.github.io/` 可访问的线上站点。

- [ ] **Step 1: 用户在 GitHub 创建仓库**

请用户登录 GitHub 手动创建名为 `r03montia.github.io` 的空公开仓库（不要初始化 README/license）。此步必须用户本人操作或授权后用 `gh` CLI 完成。

- [ ] **Step 2: 推送代码**

```bash
git branch -M main
git remote add origin https://github.com/R03montia/r03montia.github.io.git
git push -u origin main
```

推送前先与用户确认（push 属于影响远端的操作）。

- [ ] **Step 3: 开启 Pages 数据源**

用户在仓库 Settings → Pages → Source 选择 **GitHub Actions**。此后每次 push 自动部署。

- [ ] **Step 4: 验证上线**

等待 Actions 跑完（约 1–2 分钟）后访问 `https://r03montia.github.io/`，确认：首页渲染正常、雨幕与剪影可见、暗色切换生效、`/blog/` 列表与文章页可达、`/rss.xml` 有内容。
