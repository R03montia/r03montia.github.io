#!/usr/bin/env bash
# 一键发布：构建校验 → 提交改动 → 推送到 GitHub 触发自动部署。
#
# 用法（Windows 里）：
#   wsl.exe -e bash /root/code/personal-website/publish.sh "提交消息(可选)"
# 用法（WSL 终端里）：
#   cd /root/code/personal-website && ./publish.sh "提交消息(可选)"
set -euo pipefail
cd "$(dirname "$0")"

MSG="${1:-内容更新}"

echo "▶ 1/3 构建校验（能提前抓到 frontmatter 写错之类的问题）…"
npm run build

echo "▶ 2/3 提交改动…"
git add -A
if [ -z "$(git status --porcelain)" ]; then
  echo "   没有待提交的改动，跳过 commit。"
else
  git commit -m "$MSG"
fi

echo "▶ 3/3 同步并推送到 GitHub…"
git pull --rebase origin main
git push

echo "✔ 完成。等 1~2 分钟 GitHub Actions 部署上线，然后强刷新查看。"