# Daily News Video Skill / AI 日报视频 Skill

> 中文说明在前，English follows.

## 中文

## Demo / 示例

https://github.com/user-attachments/assets/69fcd767-3c17-4d53-9d21-b3b31bf22e04

这是一个用于 Codex 的日报视频 skill。它可以联网搜索新闻，整理中文文案，生成 HyperFrames 竖屏视频页面，使用本地 VoxCPM 生成统一音色旁白，拼接旁白和 BGM，最后渲染成 9:16 MP4。

默认工作方式是交互式：Codex 会先让你确认新闻列表，再让你确认中文文案。中文文案确认后，后续视觉、音频、拼接和渲染会自动执行。

### 目录结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── chinese-vertical-video-style-prompt.md
│   ├── editorial-style-prompt.md
│   ├── voice-reference.wav
│   ├── voice-reference-source.m4a
│   ├── voice-reference-transcript.txt
│   └── background-music.mp3
├── references/
│   ├── episode.schema.json
│   ├── hyperframes.md
│   ├── research.md
│   ├── visuals.md
│   ├── voxcpm.md
│   └── workflow.md
└── scripts/
    ├── generate_hyperframes_project.py
    ├── generate_voice_voxcpm.sh
    ├── render_hyperframes.sh
    ├── setup_check.sh
    └── stitch_audio.py
```

生成结果默认放在：

```text
daily-news-video-runs/<slug>/
```

### 工作流

1. Codex 搜索新闻，并让你确认候选列表。
2. Codex 生成中文标题、亮点、callout 和旁白，并让你确认文案。
3. 文案确认后，Codex 自动生成视觉页面、语音、音频拼接和最终 MP4。

如果你明确要求 `auto` 或“全自动”，Codex 才会跳过确认点。

### 依赖

- Codex，且需要联网搜索新闻
- Node.js 和 HyperFrames CLI（通过 `npx hyperframes`）
- Python 3
- `ffmpeg` 和 `ffprobe`
- 本地 VoxCPM，用于生成语音
- 可选：自己的参考音频、参考文本和 BGM

运行环境检查：

```bash
bash scripts/setup_check.sh
```

### 公开资产说明

仓库内包含示例参考音频和背景音乐：

- `assets/voice-reference.wav`
- `assets/voice-reference-source.m4a`
- `assets/voice-reference-transcript.txt`
- `assets/background-music.mp3`

这些文件可以公开，前提是你有权分享它们。但生产使用时建议替换成你自己的声音和授权 BGM。参考音频和参考文本应该匹配，否则 VoxCPM 克隆效果会变差。

### 常用命令

从 `episode.json` 生成 HyperFrames 项目外壳：

```bash
python3 scripts/generate_hyperframes_project.py daily-news-video-runs/<slug>/episode.json
```

生成本地语音：

```bash
bash scripts/generate_voice_voxcpm.sh daily-news-video-runs/<slug>
```

拼接音频并写入真实场景时长：

```bash
python3 scripts/stitch_audio.py daily-news-video-runs/<slug>
```

渲染视频：

```bash
bash scripts/render_hyperframes.sh daily-news-video-runs/<slug>
```

### 设计原则

- 新闻条数和视频时长都是动态的。
- 完整来源 URL 只保存在 `episode.json`，视频里只显示来源和日期。
- 每条新闻的 `story-XX.html` 由大模型按内容设计，脚本默认不会覆盖。
- 如果 `image_strategy` 是 `none`，不要插入伪 SVG、假插图或无意义 motif。
- 如果 `image_strategy` 是 `generate`，必须使用真实生成的 bitmap 图片，并保存到 `media/images/`。

### 许可证

MIT

---

## English

## Demo

https://github.com/user-attachments/assets/69fcd767-3c17-4d53-9d21-b3b31bf22e04

Daily News Video Skill is a Codex skill for generating Chinese vertical daily news videos. It researches fresh news, drafts Chinese scripts, creates HyperFrames story compositions, generates local VoxCPM narration, stitches voice and BGM, and renders a 9:16 MP4.

The default mode is interactive. Codex asks you to confirm the selected news items, then asks you to confirm the Chinese scripts. After script approval, visual generation, voice generation, audio stitching, and rendering run automatically.

### Structure

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── chinese-vertical-video-style-prompt.md
│   ├── editorial-style-prompt.md
│   ├── voice-reference.wav
│   ├── voice-reference-source.m4a
│   ├── voice-reference-transcript.txt
│   └── background-music.mp3
├── references/
│   ├── episode.schema.json
│   ├── hyperframes.md
│   ├── research.md
│   ├── visuals.md
│   ├── voxcpm.md
│   └── workflow.md
└── scripts/
    ├── generate_hyperframes_project.py
    ├── generate_voice_voxcpm.sh
    ├── render_hyperframes.sh
    ├── setup_check.sh
    └── stitch_audio.py
```

Generated outputs are written to:

```text
daily-news-video-runs/<slug>/
```

### Workflow

1. Codex researches candidate stories and asks you to confirm the list.
2. Codex drafts Chinese headlines, metrics, callouts, and narration scripts, then asks you to confirm the scripts.
3. After script approval, Codex automatically generates visuals, voice, audio stitching, and the final MP4.

Use `auto` mode only when you explicitly want no checkpoints.

### Requirements

- Codex with web access for research
- Node.js and HyperFrames CLI via `npx hyperframes`
- Python 3
- `ffmpeg` and `ffprobe`
- Local VoxCPM setup for voice generation
- Optional custom voice reference, transcript, and BGM

Run a setup check:

```bash
bash scripts/setup_check.sh
```

### Public Assets

This repository includes sample voice reference and background music assets:

- `assets/voice-reference.wav`
- `assets/voice-reference-source.m4a`
- `assets/voice-reference-transcript.txt`
- `assets/background-music.mp3`

They can be published if you have the right to share them, but users should replace them before production use. The reference audio and transcript should match each other for better VoxCPM cloning quality.

### Core Commands

Generate a HyperFrames shell from an episode file:

```bash
python3 scripts/generate_hyperframes_project.py daily-news-video-runs/<slug>/episode.json
```

Generate local voice:

```bash
bash scripts/generate_voice_voxcpm.sh daily-news-video-runs/<slug>
```

Stitch audio and write audio-driven scene timing:

```bash
python3 scripts/stitch_audio.py daily-news-video-runs/<slug>
```

Render:

```bash
bash scripts/render_hyperframes.sh daily-news-video-runs/<slug>
```

### Design Rules

- Story count and duration are dynamic.
- Full source URLs stay in `episode.json`; videos show only source/date badges.
- Story HTML is LLM-designed and preserved by the project generator by default.
- If `image_strategy` is `none`, do not insert fake SVGs, fake illustrations, or meaningless motifs.
- If `image_strategy` is `generate`, use an actual generated bitmap image and save it under `media/images/`.

### License

MIT
