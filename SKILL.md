---
name: daily-news-video
description: Generate daily Chinese vertical news videos with web research, structured episode data, HyperFrames visuals, VoxCPM voice cloning, audio stitching, and MP4 rendering. Use when the user asks to create a daily news video, AI news daily, 9:16 short-form news recap, or a repeatable Codex workflow that searches news and outputs a rendered video.
metadata:
  short-description: Generate daily news videos
---

# Daily News Video

Use this skill to create a new 9:16 Chinese daily news video from fresh web research.
The workflow is data-driven: research first, write `episode.json`, then generate a
new HyperFrames project from that structured data.

## Output Contract

Create each video in a new directory:

```text
daily-news-video-runs/<slug>/
├── episode.json
├── hyperframes.json
├── index.html
├── compositions/
├── scripts/
├── media/
│   ├── el/
│   ├── images/
│   └── voice.mp3
└── renders/
    └── final.mp4
```

Do not hard-code the number of stories or the total duration. The number of
`story-XX.html` files must equal `episode.stories.length`.

## Required Inputs

Ask for or infer:

- Topic, for example `今日 AI 新闻`
- Time window, default `past 24 hours`
- Item count, default `5`
- Language, default `zh-CN`
- Voice reference, default `assets/voice-reference.wav`
- Voice transcript, default `assets/voice-reference-transcript.txt`
- Background music, default `assets/background-music.mp3`
- Visual/editorial style prompt, default `assets/chinese-vertical-video-style-prompt.md`
- Run mode, default `interactive`. Use `auto` only when the user explicitly
  asks for a fully automatic run.

## Interaction Checkpoints

Default to an interactive workflow. Do not continue past a checkpoint until the
user explicitly approves it, unless the user asked for `auto` mode.

Required checkpoints:

1. **News selection checkpoint**
   - After research, show the candidate story list before writing final
     `episode.json`.
   - Include Chinese title, source, date, one-line summary, and why it matters.
   - Ask whether to keep, replace, reorder, or change the item count.

2. **Chinese script checkpoint**
   - After drafting translated content, show each story's `headline_lines`,
     `metric`, `callout`, and narration script.
   - Wait for approval before generating images, HTML, voice, or video.
   - If the user edits wording, update `episode.json` before continuing.
   - Once this checkpoint is approved, continue automatically through visual
     planning, optional image generation, story HTML, voice, stitching, final
     render, and verification.

If the user says "继续", treat it as approval for the current checkpoint only,
not as permission to skip all future checkpoints.

## Workflow

1. Check local setup when the user is new, non-technical, or unsure.
   - Run:
     ```bash
     bash scripts/setup_check.sh
     ```
   - If only script/project mode is available, still generate `episode.json`,
     scripts, and HyperFrames files.
   - If render or voice dependencies are missing, explain the missing capability
     and continue with the highest available mode.

2. Research the news.
   - Browse the web.
   - Prefer official announcements and primary sources.
   - Use roundups/social posts only for discovery and popularity signals.
   - Verify publication date and URL for every selected story.
   - Do not invent metrics.
   - Stop at the news selection checkpoint in interactive mode.

3. Write `episode.json`.
   - Follow `references/episode.schema.json`.
   - Translate every story into Chinese.
   - Keep narration concise and spoken.
   - Choose one strong metric or keyword per story.
   - Do not repeat the same key phrase across `headline_lines`, `metric`, and
     `callout`. If the headline already contains the strongest number or
     keyword, choose a different angle for `metric`, such as the date, scale,
     impacted user group, technical object, business implication, or review
     status.
   - Do not put full URLs on screen. Keep URLs in `episode.json` only for
     verification and source reporting.
   - For each story, write `visual_direction` so layout, image decision, shapes,
     image prompt, and motion are tailored to the story content.
   - For each story, set `visual_direction.image_strategy`:
     - `generate`: use an AI-generated abstract editorial image.
     - `none`: do not use any image-like visual; express the story with
       typography, numbers, source badges, color, whitespace, and motion.
   - Use `generate` when an image adds meaning, for example product launches,
     hardware, robotics, infrastructure, tools, platform ecosystems, or complex
     concepts.
   - Use `none` when pure editorial layout is clearer, for example short
     partnership, policy, funding, metrics-only, or simple company-update items.
   - When `image_strategy` is `generate`, write `visual_prompt` and later set
     `image_path`. When it is `none`, do not set `image_path`.
   - When `image_strategy` is `none`, do not add decorative diagrams,
     pseudo-SVG motifs, node-link graphics, icon clusters, or abstract
     illustration panels.
   - Set initial estimated timing only. Final scene timing must follow the
     generated VoxCPM audio durations.
   - Stop at the Chinese script checkpoint in interactive mode. After approval,
     continue automatically through the rest of the workflow.

4. Generate selected abstract editorial images.
   - Use `references/visuals.md`.
   - Generate images only for stories where
     `story.visual_direction.image_strategy` is `generate`.
   - Save images under `daily-news-video-runs/<slug>/media/images/`.
   - Set each generated story `image_path` relative to the run directory, for
     example `media/images/story-01.png`.
   - Do not scrape or download publisher images unless the user explicitly asks.

5. Generate story composition HTML with the LLM.
   - Read `assets/chinese-vertical-video-style-prompt.md`.
   - For each story, write a fresh standalone HyperFrames composition:
     `daily-news-video-runs/<slug>/compositions/story-XX.html`.
   - Each story file must contain a `<template>` with:
     - `data-composition-id="story-XX"`
     - `data-width="1080"`
     - `data-height="1920"`
     - `data-duration="<current story duration>"`
     - `window.__timelines["story-XX"] = gsap.timeline({ paused: true })`
   - Let the LLM design the layout, typography, shapes, transitions, and
     story-specific GSAP animation from `story.visual_direction`.
   - Do not make all stories the same template with only colors changed.
   - Keep source URLs off screen. Use only publisher/date source badges.
   - Respect `image_strategy`: only insert a bitmap image when `image_path`
     exists; if `none`, do not create fake illustration motifs.
6. Generate the HyperFrames project shell.
   - Run:
     ```bash
     python3 scripts/generate_hyperframes_project.py \
       daily-news-video-runs/<slug>/episode.json
     ```
   - This script writes `index.html`, `hyperframes.json`, cover, outro,
     captions, scripts, media references, BGM, and voice wiring.
   - It preserves existing `compositions/story-XX.html` files by default and
     only updates their `data-duration`. Use `--overwrite-stories` only when
     intentionally falling back to the deterministic template.
   - If `assets/background-music.mp3` exists, it is copied into the run and
     added as a low-volume BGM track.
   - The voice track is added only after `media/voice.mp3` exists.

7. Generate voice with VoxCPM.
   - Use clone mode with a stable reference voice.
   - Run:
     ```bash
     bash scripts/generate_voice_voxcpm.sh \
       daily-news-video-runs/<slug>
     ```

8. Stitch audio.
   - Run:
     ```bash
     python3 scripts/stitch_audio.py \
       daily-news-video-runs/<slug>
     ```
   - This reads the real duration of each VoxCPM clip, writes
     `timing.scene_seconds`, updates `timing.total_seconds`, writes
     `media/voice.mp3`, and inserts the voice track into `index.html`.
   - Do not speed up narration to fit fixed story slots. Video duration follows
     the audio.
9. Regenerate the HyperFrames project shell after stitching audio.
   - Run the project generator again so scene durations, captions, BGM
     duration, and voiceover duration use the audio-driven timing:
     ```bash
     python3 scripts/generate_hyperframes_project.py \
       daily-news-video-runs/<slug>/episode.json
     ```
   - This must not overwrite LLM-designed story HTML. It only updates the
     existing story file `data-duration` values.

10. Render video.
   - Run:
     ```bash
     bash scripts/render_hyperframes.sh \
       daily-news-video-runs/<slug>
     ```

11. Verify.
   - Confirm `renders/final.mp4` exists.
   - Use `ffprobe` to check 1080x1920, 30 fps, video duration, and audio track.
   - Report source URLs and any unresolved warnings.

## References

- Research rules: `references/research.md`
- Episode data contract: `references/episode.schema.json`
- HyperFrames generation notes: `references/hyperframes.md`
- VoxCPM voice workflow: `references/voxcpm.md`
- Visual decision and image generation rules: `references/visuals.md`

Load only the reference file needed for the current step.
