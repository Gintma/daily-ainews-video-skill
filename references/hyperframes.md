# HyperFrames Notes

Use this reference when generating or debugging the video project.

## Project Rules

- Output is a standalone HyperFrames project under `daily-news-video-runs/<slug>/`.
- Root file is `index.html`.
- Scene files live in `compositions/`.
- Every scene must register a paused GSAP timeline on `window.__timelines`.
- Timed sub-compositions in `index.html` must use:
  - `class="clip"`
  - `data-composition-id`
  - `data-composition-src`
  - `data-start`
  - `data-duration`
  - `data-track-index`

## Dynamic Scenes

The project generator creates:

- `cover.html`
- `story-01.html ... story-N.html`
- `outro.html`
- `captions.html`

Scene timing comes from `episode.json`, not from fixed assumptions.

## Visual Style

- 9:16, 1080x1920.
- Full-bleed editorial pages.
- No interactive UI controls.
- Use strong headline, source, metric, and `这意味着` callout.
- Keep text large and readable for mobile.
- Use color wipes for scene entrances.

## Validation

Check availability first:

```bash
bash scripts/setup_check.sh
```

Run:

```bash
npx hyperframes lint
npx hyperframes render --fps 30 --quality standard --output renders/final.mp4
```

Warnings are acceptable if there are no errors and the render completes.
