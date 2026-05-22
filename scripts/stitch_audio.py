#!/usr/bin/env python3
"""Stitch VoxCPM scene clips into media/voice.mp3 for a generated project."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")
PADDING_SECONDS = float(os.environ.get("VOICE_SCENE_PADDING", "0.35"))


def probe(path: Path) -> float:
    out = subprocess.check_output([
        FFPROBE, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True)
    return float(out.strip())


def ensure_voice_track(project: Path, duration: float) -> None:
    index_path = project / "index.html"
    if not index_path.exists():
        return
    text = index_path.read_text(encoding="utf-8")
    if 'id="voiceover"' in text:
        return
    voice_tag = (
        f'\n      <audio id="voiceover" class="clip" data-start="0" '
        f'data-duration="{duration:.3f}" data-track-index="4" '
        f'src="media/voice.mp3" data-volume="1"></audio>'
    )
    marker = "\n    </div>\n    <script>"
    if marker in text:
        text = text.replace(marker, voice_tag + marker, 1)
        index_path.write_text(text, encoding="utf-8")


def update_episode_timing(project: Path, durations: list[float]) -> dict:
    episode_path = project / "episode.json"
    ep = json.loads(episode_path.read_text(encoding="utf-8"))
    padded = [round(duration + PADDING_SECONDS, 3) for duration in durations]
    timing = ep["timing"]
    timing["scene_seconds"] = padded
    timing["cover_seconds"] = padded[0]
    timing["outro_seconds"] = padded[-1]
    if len(padded) > 2:
        timing["story_seconds"] = round(max(padded[1:-1]), 3)
    timing["total_seconds"] = round(sum(padded), 3)
    episode_path.write_text(json.dumps(ep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ep


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: stitch_audio.py daily-news-video-runs/<slug>")
    project = Path(sys.argv[1]).resolve()
    ep = json.loads((project / "episode.json").read_text(encoding="utf-8"))
    expected_clips = 1 + len(ep["stories"]) + 1

    clips = sorted((project / "media/el").glob("s*.wav"))
    if len(clips) != expected_clips:
        raise SystemExit(f"Expected {expected_clips} clips, found {len(clips)}")

    durations = [probe(clip) for clip in clips]
    ep = update_episode_timing(project, durations)
    slots = ep["timing"]["scene_seconds"]
    starts = []
    cursor = 0.0
    for slot in slots:
        starts.append(cursor)
        cursor += slot

    cmd = [FFMPEG, "-y"]
    for clip in clips:
        cmd.extend(["-i", str(clip)])

    filters = []
    mix_labels = []
    for idx, (clip, start, _slot) in enumerate(zip(clips, starts, slots)):
        src = f"[{idx}:a]"
        out = f"a{idx}"
        delay = int(round(start * 1000))
        filters.append(f"{src}adelay={delay}|{delay}[{out}]")
        mix_labels.append(f"[{out}]")

    filters.append("".join(mix_labels) + f"amix=inputs={len(mix_labels)}:duration=longest:normalize=0,apad=whole_dur={cursor:.3f}[out]")
    cmd.extend(["-filter_complex", "; ".join(filters), "-map", "[out]", "-t", f"{cursor:.3f}", "-c:a", "libmp3lame", "-b:a", "192k", str(project / "media/voice.mp3")])
    subprocess.check_call(cmd)
    ensure_voice_track(project, cursor)
    print(f"Wrote {project / 'media/voice.mp3'} ({cursor:.2f}s)")


if __name__ == "__main__":
    main()
