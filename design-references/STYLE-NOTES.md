# SCP-CN 主题版式风格笔记

来源：7 个 scp-wiki-cn.wikidot.com 主题页（原始 HTML 在 `raw/`，CSS+介绍全文在同目录 `*.txt`）。本文档是提炼后的版式参考，供个人网站设计时使用。

## 七个主题速览

| 主题 | 氛围 | 配色基调 | 标题字体 | 正文字体 |
|------|------|----------|----------|----------|
| trauma（创伤） | 至上主义极简，白上白 | 浅灰底 `rgb(225,225,225)` + 白卡片半透明 | Outfit / Nixie One | Atkinson Hyperlegible |
| deserted-years（废年） | 黑白老照片怀旧 | 大理石纹理底 + 纯黑白灰，无彩色 | Zhi Mang Xing 手写体 / Oswald | Noto Serif SC |
| lampeter-warm（兰彼得暖色） | 深夜车站蒸汽朋克暖光 | 夜紫 `#33232e` 底 + 琥珀橙 `#ec9413` / 金 `#eab52f` | ZCOOL XiaoWei + Crimson Text | Noto Serif SC + Playfair Display |
| wish-for-miracle（祈冀） | 暗夜星空许愿，庄重浪漫 | 近黑深蓝 `rgb(5,13,23)` + 奶油黄 `rgb(255,253,208)` + 绯红 | ZCOOL XiaoWei / Playfair Display | Noto Sans SC |
| another-night（另一夜） | 雨夜地铁舷窗，文学朦胧 | 全屏夜景照打底 + 蓝紫链接 `rgb(120,140,255)`，亮暗双模式 | Afacad Flux + 思源宋 | Sofia Sans（可变字重 440） |
| petrifaction（石化） | 大理石墓碑冷寂 | 全站 `grayscale(0.85)`，白底黑字 + 主灰 `#707070` | Oswald + Ma Shan Zheng 特大毛笔字 | Noto Serif SC（细字重 200） |
| greyday（灰日） | 末世沙尘暴废土 | 冷灰绿 `#CAD1D1` 文字 + 近黑半透明层叠模糊背景 | FlyFlowerSong 自托管手写体 | 细字重衬线回退 |

## 共性版式手法

1. **内容区窄栏居中**：44.5rem（石化）～ 67.25rem（兰彼得），多数在 57.5–60rem。侧栏 14–17rem。
2. **大页头 + 渐变过渡进正文**：页头用多层 repeat-x 背景图叠加景深（祈冀叠 5 张），或超大字号站名（石化 8.75rem 毛笔字）。
3. **氛围背景三层法**：固定全屏背景图（常配 `filter: blur()`）→ 半透明内容面板 → 低透明度装饰剪影/云层动画。
4. **引用块是风格主战场**：左边线+半透明底（trauma）、信封图标框（兰彼得）、data-title 标签牌+徽章（祈冀）、堆叠纸张 ±2.5° 双伪元素（another-night）、大理石圆角块（石化）。
5. **分割线带装饰**：双弧线伪元素（废年）、中央嵌四角星 SVG（祈冀）、火车车厢图标（兰彼得）。
6. **中文衬线为主**：正文几乎全是 Noto Serif SC；标题混用手写体（Zhi Mang Xing / Ma Shan Zheng / ZCOOL XiaoWei / FlyFlowerSong）制造复古感。

## 值得复用的 CSS 技巧库

### 配色系统
- **RGB 三元组变量**：`--c: 18,25,35;` 存色值，用 `rgb(var(--c) / .5)` 派生任意透明度，一套变量通吃实色与半透明（trauma / 祈冀 / another-night 共同做法）
- 一行全局调色：`html { filter: grayscale(0.85); }` 统一全站色调（石化）；`filter: grayscale(100%)` 只处理图片区（废年）

### 排版
- `clamp(2rem, 8vw, 6rem)` 流式横幅字号，一行解决响应式（trauma）
- 可变字重正文字体（Sofia Sans wght 440）比离散字重更细腻（another-night）
- 渐变文字标题：`linear-gradient` + `background-clip: text`（石化 / greyday）

### 布局与组件
- 三层 `position: fixed; bottom: 0` 不同透明度剪影 = 零 JS 视差（trauma）；多层背景不同时长 `translateX` 关键帧 = 廉价视差动画（greyday 云层 120s + 沙尘 8s）
- 固定模糊背景不受滚动影响：`position: fixed` 伪元素 + `filter: blur(15px)`（greyday）
- 毛玻璃面板浮于照片上：`backdrop-filter: blur()` + 半透明底（another-night / trauma）
- 纯 CSS 抽屉侧栏：`:target` / `:focus-within` 控制 `-18rem → 0` 滑入（石化）
- `body:has(#side-bar:hover)::before` 展开侧栏时全屏压暗遮罩，零 JS（祈冀）
- `mask-image` + 内联 SVG data URI 给任意图标/logo 换色（兰彼得 / 祈冀）
- 切角图片框：`clip-path: polygon()`（兰彼得）
- 硬偏移阴影做版画质感：`box-shadow: 0 2px 0 rgba(0,0,0,.6)`（废年）
- 柔和弥散卡片阴影：`box-shadow: 0 0 2.5rem -1rem`（trauma）
- `content: var(--text)` 把文案做成 CSS 配置接口，配合 transition 做纯 CSS 文字切换（another-night）
- 自定义 `::selection` 与滚动条配色强化主题一致性（兰彼得 / greyday）

### 字体清单（Google Fonts 可直接引入）
Zhi Mang Xing（行书）、Ma Shan Zheng（毛笔楷）、ZCOOL XiaoWei（古风标题）、Noto Serif SC（正文衬线）、Noto Sans SC（正文黑体）、Oswald、Playfair Display、Crimson Text、Nixie One、Atkinson Hyperlegible、Outfit、Sofia Sans、Afacad Flux

## 对个人网站的启示

这批主题的共同气质：**复古、有文学性、氛围感强、细节精致**。若沿用此方向：
- 深色系可选「祈冀」（暗夜+奶油黄，最精致规范）或「兰彼得」（暖橙霓虹，最有温度）
- 浅色系可选「trauma」（最干净现代，CSS 变量体系最适合直接改造）
- 怀旧向选「废年」或「石化」（灰度滤镜 + 手写体 + 衬线的组合成本最低）
- 另一夜的「全屏氛围图 + 毛玻璃内容卡」结构最适合个人主页首屏

basalt 框架主题（祈冀 / another-night）代码质量最高、变量命名规范，做新样式建议以其为骨架参考。
