# 个人网站设计稿

日期：2026-08-24
状态：已与用户确认

## 目标

为用户（GitHub 用户名 `R03montia`）搭建个人博客站，部署在 GitHub Pages 主仓库 `R03montia.github.io`，站点地址 `https://r03montia.github.io/`。

## 技术栈

- **Astro 5** 静态站点框架
  - 内容集合（content collections）管理博客文章与项目数据
  - 文章用 Markdown 编写，frontmatter：`title / date / tags / description`
- **部署**：GitHub Actions 构建静态产物，推送到 `R03montia.github.io` 仓库；git push 即上线
- 开发环境：WSL2 Ubuntu-24.04 安装 Node.js LTS；网络走 Clash 代理 `127.0.0.1:7897`

## 站点内容（纯中文）

| 路由 | 页面 | 内容 |
|------|------|------|
| `/` | 首页 | 横幅大字标 + 一句话简介 + 最近更新文章列表 |
| `/blog/` | 博客列表 | 全部文章倒序，支持 #标签筛选 |
| `/blog/<slug>/` | 文章页 | 标题、日期、阅读时长、标签、正文、悬浮目录（TOC） |
| `/projects/` | 项目页 | 项目卡片：名称、描述、技术栈、GitHub 链接 |
| `/about/` | 关于页 | 自我介绍 |
| `/rss.xml` | RSS 订阅 | 全文或摘要输出 |
| `404` | 错误页 | 与全站风格一致 |

## 布局骨架

- **桌面端**：左侧固定侧边栏——头像/站名、导航四项（首页/博客/项目/关于）、社交图标（GitHub）、明暗切换按钮。右侧为内容区。
- **移动端**：侧边栏收起，改为顶部细条 + 底部导航栏。
- 内容窄栏居中约 60rem，正文行宽舒适。

## 视觉风格：trauma（创伤）版式 + rainy 下雨预设

参考来源：`design-references/STYLE-NOTES.md` 与 `design-references/trauma.txt`（SCP-CN trauma 主题完整 CSS 已存档）。

### 基底特征（自 trauma 版式提炼，非照搬）

- **至上主义极简**："白上白"——浅灰底上浮起白色半透明内容卡片
  - 页面底色 `rgb(225,225,225)`，卡片 `rgba(255,255,255,0.9)`
  - 卡片柔和弥散阴影：`box-shadow: 0 0 2.5rem -1rem`
- **三层城市剪影装饰**：`position: fixed; bottom: 0` 三层不同透明度（0.15/0.05/0.05）剪影，低成本视差感
- **字体**：
  - 横幅装饰：Nixie One（细线衬线）
  - 标题/UI：Outfit + 中文回退（思源黑体）
  - 正文：Atkinson Hyperlegible + 中文回退（思源宋体）
  - 中文正文以 Noto Serif SC 为准（贴合原版式的高可读性思路）
- **排版**：`clamp()` 流式横幅字号（约 2–6rem）；引用块 = 左侧 0.3rem 粗边线 + 半透明底

### rainy 下雨预设

原版式通过 include 参数 `|rainy=true` 启用的配色变体。本站直接内置：

- 冷灰蓝调色板替换默认浅灰
- 雨幕氛围层（CSS 实现的雨丝动画覆盖层，低透明度不干扰阅读）
- 提供明/暗两种模式：跟随系统 `prefers-color-scheme`，侧边栏按钮手动切换并 localStorage 记忆

### 配色系统实现方式

采用 RGB 三元组 CSS 变量（trauma 原生做法）：

```css
:root {
  --body-bg: 225,225,225;      /* rainy 模式下换冷灰蓝 */
  --content-bg: 255,255,255;
  --text: 35,35,38;
}
.card { background: rgb(var(--content-bg) / .9); }
```

一套变量派生实色与任意透明度，明暗模式只改变量值。

## 第一版明确不做

- 站内搜索（文章多了再加）
- 评论系统
- 双语切换
- 文章页独立变体版式（用户明确：以后有文章了再看）

## 非功能要求

- Lighthouse 性能良好：零 JS 默认输出（明暗切换、TOC 高亮等少量内联脚本）
- 响应式断点：移动端优先保证阅读体验
- 无障碍：语义化标签、skip-link、对比度达标
