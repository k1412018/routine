#!/bin/bash
# ============================================================
# 変更（音声ファイルの追加・index.htmlの更新など）を
# GitHub Pagesに反映するスクリプト
#
# 使い方: ターミナルでこのフォルダに移動して
#   bash publish.sh
# ============================================================
cd "$(dirname "$0")" || exit 1
git add -A
if git commit -m "更新: $(date '+%Y-%m-%d %H:%M')"; then
  git push
  echo ""
  echo "push完了！ 1〜2分後に反映されます → https://k1412018.github.io/routine/"
else
  echo "変更がないので、何もしませんでした。"
fi
