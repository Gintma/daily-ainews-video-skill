#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

ok_count=0
warn_count=0
fail_count=0

ok() {
  ok_count=$((ok_count + 1))
  printf "OK    %s\n" "$1"
}

warn() {
  warn_count=$((warn_count + 1))
  printf "WARN  %s\n" "$1"
}

fail() {
  fail_count=$((fail_count + 1))
  printf "FAIL  %s\n" "$1"
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

have_file() {
  [ -f "$1" ]
}

have_dir() {
  [ -d "$1" ]
}

printf "Daily News Video skill setup check\n"
printf "Skill directory: %s\n\n" "$SKILL_DIR"

if have_cmd python3; then
  ok "python3 found: $(command -v python3)"
else
  fail "python3 not found. Needed to generate the HyperFrames project and stitch audio."
fi

if have_cmd node; then
  ok "node found: $(command -v node)"
else
  warn "node not found. Needed for HyperFrames rendering."
fi

if have_cmd npx; then
  ok "npx found: $(command -v npx)"
else
  warn "npx not found. Needed to run HyperFrames."
fi

if have_cmd ffmpeg; then
  ok "ffmpeg found: $(command -v ffmpeg)"
elif [ -n "${FFMPEG:-}" ] && [ -x "$FFMPEG" ]; then
  ok "ffmpeg found from FFMPEG: $FFMPEG"
elif [ -n "${FFMPEG_BIN_DIR:-}" ] && [ -x "$FFMPEG_BIN_DIR/ffmpeg" ]; then
  ok "ffmpeg found from FFMPEG_BIN_DIR: $FFMPEG_BIN_DIR/ffmpeg"
else
  warn "ffmpeg not found. Needed to stitch audio and render/check MP4 files."
fi

if have_cmd ffprobe; then
  ok "ffprobe found: $(command -v ffprobe)"
elif [ -n "${FFPROBE:-}" ] && [ -x "$FFPROBE" ]; then
  ok "ffprobe found from FFPROBE: $FFPROBE"
elif [ -n "${FFMPEG_BIN_DIR:-}" ] && [ -x "$FFMPEG_BIN_DIR/ffprobe" ]; then
  ok "ffprobe found from FFMPEG_BIN_DIR: $FFMPEG_BIN_DIR/ffprobe"
else
  warn "ffprobe not found. Needed to verify video and audio output."
fi

if have_file "$SKILL_DIR/assets/chinese-vertical-video-style-prompt.md"; then
  ok "Chinese vertical video style prompt found."
elif have_file "$SKILL_DIR/assets/editorial-style-prompt.md"; then
  warn "legacy editorial-style-prompt.md found, but chinese-vertical-video-style-prompt.md is missing."
else
  warn "style prompt missing. Codex can still write a style, but output will be less consistent."
fi

if have_file "$SKILL_DIR/assets/voice-reference.wav"; then
  ok "voice reference audio found."
else
  warn "assets/voice-reference.wav missing. VoxCPM voice cloning will not run until a reference audio is provided."
fi

if have_file "$SKILL_DIR/assets/voice-reference-transcript.txt"; then
  ok "voice reference transcript found."
else
  warn "assets/voice-reference-transcript.txt missing. VoxCPM voice cloning needs text matching the reference audio."
fi

if [ -n "${COMFY_PY:-}" ] && [ -x "$COMFY_PY" ]; then
  ok "COMFY_PY configured: $COMFY_PY"
elif have_cmd python3; then
  warn "COMFY_PY not set. VoxCPM will default to python3, which may not be the right environment."
else
  warn "COMFY_PY not set."
fi

if [ -n "${VOXCPM_SRC:-}" ] && have_dir "$VOXCPM_SRC"; then
  ok "VOXCPM_SRC configured: $VOXCPM_SRC"
else
  warn "VOXCPM_SRC not set or not found. Voice generation will be skipped/fail until VoxCPM is configured."
fi

if [ -n "${VOXCPM_MODEL:-}" ] && have_dir "$VOXCPM_MODEL"; then
  ok "VOXCPM_MODEL configured: $VOXCPM_MODEL"
else
  warn "VOXCPM_MODEL not set or not found. Voice generation will be skipped/fail until a VoxCPM model path is configured."
fi

printf "\nCapability summary\n"

if have_cmd python3 && { have_file "$SKILL_DIR/assets/chinese-vertical-video-style-prompt.md" || have_file "$SKILL_DIR/assets/editorial-style-prompt.md"; }; then
  ok "Script/project mode: available. Codex can research, write episode.json, and generate project files."
else
  fail "Script/project mode: incomplete. Install python3 and keep the skill assets in place."
fi

if have_cmd npx && (have_cmd ffmpeg || { [ -n "${FFMPEG:-}" ] && [ -x "$FFMPEG" ]; } || { [ -n "${FFMPEG_BIN_DIR:-}" ] && [ -x "$FFMPEG_BIN_DIR/ffmpeg" ]; }); then
  ok "Video render mode: likely available if HyperFrames can be fetched or is installed."
else
  warn "Video render mode: incomplete. Install Node.js/npx, HyperFrames access, and ffmpeg."
fi

if [ -n "${VOXCPM_SRC:-}" ] && have_dir "$VOXCPM_SRC" && [ -n "${VOXCPM_MODEL:-}" ] && have_dir "$VOXCPM_MODEL" && have_file "$SKILL_DIR/assets/voice-reference.wav" && have_file "$SKILL_DIR/assets/voice-reference-transcript.txt"; then
  ok "Voice mode: available."
else
  warn "Voice mode: incomplete. You can still generate scripts or render a silent/placeholder-audio video."
fi

printf "\nResult: %s OK, %s warnings, %s failures\n" "$ok_count" "$warn_count" "$fail_count"

if [ "$fail_count" -gt 0 ]; then
  exit 1
fi

exit 0
