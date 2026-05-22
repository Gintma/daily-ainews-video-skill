# Chinese Vertical Editorial News Video Style

Create a 9:16 Chinese vertical editorial news video, designed for short-form
video platforms. The output is a HyperFrames video composition, not an
interactive website. Keep the visual spirit of a horizontal-swipe editorial
magazine: masthead metadata and page-to-page motion may appear as visual
motifs, but they must not require user interaction.

## Inputs

Use structured episode data instead of a single source URL:

- `episode.meta`: title, slug, language, date, topic, time window
- `episode.cover`: cover text and narration
- `episode.stories[]`: verified news stories, sources, dates, metrics, scripts
- `episode.outro`: closing text and narration
- required `story.visual_direction`
- conditional `story.visual_prompt` and `story.image_path` when
  `story.visual_direction.image_strategy` is `generate`

The video is primarily Chinese. Keep necessary English brand/product names such
as OpenAI, Google, Gemini, Claude, NVIDIA, C2PA, SynthID, Codex, MCP.

## Format

- 9:16 vertical video
- 1080 x 1920
- 30 fps
- Full-bleed, edge-to-edge
- No app chrome, no real buttons, no interactive controls
- Scene duration is controlled by `episode.timing`
- The number of story scenes is dynamic

## Aesthetic

Bold, fun, modern editorial magazine. Think playful Monocle energy, not austere
business slides. Use strong typography, color wipes, giant ghost numbers,
metadata bars, source badges, content-driven visuals, and kinetic captions.

No floating UI cards. No nested cards. No decorative gradients or bokeh blobs.
Use flat editorial color, halftone texture, geometric blocks, paper-like fields,
and sharp contrast.

## Palette

Use all colors across the video, but obey contrast:

- Cream `#F5EDE0`: paper background
- Ink `#1A1A1A`: primary text
- Vermillion `#FF4A1C`: primary accent
- Electric blue `#2B4BFF`: secondary accent
- Saffron `#FFC93C`: dark/electric background accent
- Mauve `#D4A5E8`: dark background accent
- Forest `#0F4D3A`: deep accent

Contrast rules:

- Cream background: ink text; accents are vermillion, electric blue, forest
- Ink background: cream text; accents are saffron, mauve, vermillion
- Electric blue background: cream text; accent is saffron only
- Vermillion background: cream text; accents are ink and saffron only
- Ghost numbers and decorative marks stay at `0.08-0.15` opacity
- Body/callout text must remain readable on mobile

## Typography

Use a Chinese-first type system:

- Chinese headlines: heavy sans-serif Chinese fallback, for example
  `Noto Sans SC`, `Source Han Sans SC`, `PingFang SC`, `Microsoft YaHei`, or
  system sans-serif.
- English brand/product words: `Space Grotesk` 700.
- Metadata, source badges, labels: `JetBrains Mono`.
- Use `Inter Tight` italic only for short accent words or Latin phrases. Do not
  rely on italic styling for long Chinese text.

Headline rules:

- Chinese must be large, bold, and readable at phone size.
- Mix Chinese and English intentionally, not randomly.
- Each story headline should have 2-4 short lines.
- Highlight one phrase using accent color or lighter weight, but avoid making
  Chinese italic-heavy.

## Video Structure

Scene 1: Cover

- Vermillion or ink-led full-bleed page
- Top masthead: issue/date left, topic right
- Huge Chinese title
- Short subtitle naming the news theme
- Decorative circle or halftone texture
- Optional visual motif: `→ Swipe` or `横滑感` as a decorative cue only

Story scenes:

- One scene per story
- Alternating background rhythm:
  cream -> ink -> electric blue -> cream -> ink -> electric blue
- Top metadata bar:
  `第 01 条 / 共 NN 条` on the left, source name on the right
- Giant ghost rank number behind the content
- Category tag
- Chinese editorial headline
- Source badge only: publisher and date, for example `来源：OpenAI · 5月20日`
- Do not show full source URLs on screen. Keep full URLs only in `episode.sources`
  and `episode.stories[].url` for verification.
- Metric block, for example `10 亿月活`, `C2PA + SynthID`, `SDK / CLI / MCP`
- Callout block labeled `这意味着`
- Do not show bottom pagination dots, bottom page counters, or swipe arrows.
  Keep navigation/status information in the top metadata bar only.
- Conditional abstract image:
  if `story.visual_direction.image_strategy` is `generate` and
  `story.image_path` exists, include it as a cropped editorial image panel;
  if `image_strategy` is `none`, do not use an image, illustration panel,
  decorative diagram, pseudo-SVG motif, icon cluster, node-link graphic, or
  image-like geometry. Use only text hierarchy, numbers, source badges, simple
  section color, and basic motion.
- Content-driven visual direction:
  choose a layout per story based on `story.visual_direction.layout`, such as
  `typography-led`, `image-led`, `diagram-led`, `split-panel`, or `poster`.
  Shapes, image placement, and motion should match the story meaning, not a
  single fixed template.

Outro:

- Ink background
- Large Chinese closing line, for example `明天继续`
- Short subtitle about the beat: models, products, agents, infrastructure
- Optional colophon-style metadata: `来源 / 字体 / 下一期`

## Captions

Add Chinese captions as a timed overlay:

- Bottom area, centered
- Large enough for phone viewing
- Strong text shadow or stroke for contrast
- Do not cover metric or headline blocks incoherently
- Captions should follow the narration, not duplicate every screen label
- Use kinetic caption effects: each phrase enters with a pop, current words
  highlight sequentially, numbers and product names receive accent color.

## Motion

Preserve the feel of horizontal-swipe editorial pacing as animation:

- Color wipe transitions between scenes
- Content enters with slight horizontal movement
- Ghost numbers drift subtly
- Halftone backgrounds move slowly
- Do not animate pagination dots or bottom page counters; they should not be
  present in the video.
- Use a 0.5-0.7s `cubic-bezier(0.76, 0, 0.24, 1)` feeling for scene wipes

Do not implement real click, wheel, keypress, or touch handlers in video output.
Their visual language is allowed; their interaction logic is not needed.

## Visual Decision And Abstract Images

For every story, the LLM must first write a visual decision. Images are not
mandatory for every story.

Use `story.visual_direction.image_strategy`:

- `generate`: generate an abstract editorial image because the story benefits
  from a visual metaphor, product surface, hardware/infrastructure cue, tool
  ecosystem, robotics, research, or complex concept.
- `none`: do not generate or insert any image-like visual. Use this when
  typography, numbers, and editorial layout alone communicate the story more
  clearly.

When `image_strategy` is `generate`:

- Generate abstract editorial images, not scraped news images
- Recommended image size: 1920 x 1080
- No readable text inside the image
- Use metaphorical visuals: agents, tools, provenance, model reasoning,
  infrastructure, chips, robots, charts, network paths
- Keep the same palette as the video
- Save as `media/images/story-XX.png`
- Set `story.image_path` accordingly

When `image_strategy` is `none`:

- Do not set `story.image_path`
- Do not insert diagram motifs, pseudo-SVG graphics, decorative node-link
  shapes, icon clusters, or image-like geometry
- Prefer `typography-led` or restrained `poster` layouts
- Use strong headlines, ghost numbers, source badges, metric blocks, color
  rhythm, whitespace, and motion to carry the visual idea

Visual direction example:

```json
{
  "visual_direction": {
    "layout": "typography-led",
    "image_strategy": "none",
    "composition": "Large headline and metric carry the page without image-like graphics",
    "shapes": [],
    "image_prompt": "",
    "motion": "headline and metric enter with restrained editorial motion"
  }
}
```

## Writing Tone

Use Chinese short-video narration:

- Direct, compressed, understandable
- Explain what happened and why it matters
- Assume viewers are builders, product people, founders, investors, and AI tool
  users
- Avoid academic over-explanation
- Avoid hype without evidence

Screen labels should be Chinese-first:

- `这意味着`
- `第 01 条 / 共 NN 条`
- `来源`
- `发布`
- `明天继续`

Keep English only where it is a product name, source name, metric label, or
intentional editorial styling.

## Do Not

- Do not output a horizontal-swipe website as the final artifact
- Do not add real buttons, forms, menus, clickable navigation, or user input
- Do not rely on desktop/mobile responsive layout rules for the video
- Do not use `HOW TO APPLY THIS` in Chinese videos; use `这意味着`
- Do not show long source URLs on screen
- Do not use web-scraped images by default
- Do not force a fixed number of stories
- Do not force 60 seconds unless requested
