---
title: 用纯 CSS 画城市剪影
description: 三层固定定位的剪影背景就能做出视差感，不需要任何 JavaScript。
date: 2026-08-23
tags: [CSS, 设计]
---

做氛围感背景最便宜的手段：三层 `position: fixed; bottom: 0` 的剪影，配不同透明度。

滚动时前景卡片移动而背景不动，天然形成层次。再叠一层雨丝动画，气氛就到位了。
