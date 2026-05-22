#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:?Usage: render_hyperframes.sh daily-news-video-runs/<slug>}"
PROJECT_ABS="$(cd "$PROJECT_DIR" && pwd)"

if [[ -n "${FFMPEG_BIN_DIR:-}" ]]; then
  export PATH="$FFMPEG_BIN_DIR:$PATH"
fi

cd "$PROJECT_ABS"
npx hyperframes lint
npx hyperframes render --fps 30 --quality standard --output renders/final.mp4

echo "Rendered: $PROJECT_ABS/renders/final.mp4"
