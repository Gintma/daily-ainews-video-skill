# VoxCPM Voice Workflow

Use this reference when generating narration audio.

## Stable Voice

Use VoxCPM clone mode for stable voice across clips.

Check local configuration first:

```bash
bash scripts/setup_check.sh
```

Default files:

```text
assets/voice-reference.wav
assets/voice-reference-transcript.txt
```

`voice-reference.wav` is the voice reference audio.
`voice-reference-transcript.txt` is the transcript of that reference audio.

## Command Pattern

Set local paths before running:

```bash
export COMFY_PY="/path/to/python"
export VOXCPM_SRC="/path/to/ComfyUI-VoxCPM/src"
export VOXCPM_MODEL="/path/to/VoxCPM2"
```

Then run clone mode:

```bash
PYTHONPATH="$VOXCPM_SRC" "$COMFY_PY" -m voxcpm.cli clone \
  --model-path "$VOXCPM_MODEL" \
  --local-files-only \
  --no-denoiser \
  --text "$(cat scripts/s01.txt)" \
  --prompt-audio assets/voice-reference.wav \
  --prompt-file assets/voice-reference-transcript.txt \
  --output media/el/s01.wav
```

Use the bundled `scripts/generate_voice_voxcpm.sh` instead of hand-writing this
for every clip.

## Timing

If a generated clip is longer than the scene slot:

- Prefer shortening the script.
- Mild `atempo` is acceptable during stitching.
- Avoid speed-up above `1.30` unless the user accepts compressed speech.

## Audio Assembly

Use `scripts/stitch_audio.py` to generate:

```text
media/voice.mp3
```

The script reads `episode.json`, scene durations, and `media/el/s*.wav`.
