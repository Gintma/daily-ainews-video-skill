#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:?Usage: generate_voice_voxcpm.sh daily-news-video-runs/<slug>}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

COMFY_PY="${COMFY_PY:-python3}"
VOXCPM_SRC="${VOXCPM_SRC:?Set VOXCPM_SRC to the local ComfyUI-VoxCPM src directory}"
VOXCPM_MODEL="${VOXCPM_MODEL:?Set VOXCPM_MODEL to the local VoxCPM model directory}"
REF_AUDIO="${REF_AUDIO:-$SKILL_DIR/assets/voice-reference.wav}"
REF_TEXT="${REF_TEXT:-$SKILL_DIR/assets/voice-reference-transcript.txt}"

mkdir -p "$PROJECT_DIR/media/el"

for script in "$PROJECT_DIR"/scripts/s*.txt; do
  base="$(basename "$script" .txt)"
  out="$PROJECT_DIR/media/el/${base}.wav"
  echo "Generating $out"
  PYTHONPATH="$VOXCPM_SRC" "$COMFY_PY" -m voxcpm.cli clone \
    --model-path "$VOXCPM_MODEL" \
    --local-files-only \
    --no-denoiser \
    --text "$(cat "$script")" \
    --prompt-audio "$REF_AUDIO" \
    --prompt-file "$REF_TEXT" \
    --output "$out"
done
