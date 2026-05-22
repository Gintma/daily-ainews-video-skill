# Visual Decision And Images

Use this reference when writing `visual_direction` and when generating story
images.

## Default Rule

Every story must have a visual decision. Images are allowed, but not required.
The LLM chooses per story:

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

## Image Strategy

Use `image_strategy: "generate"` when an AI-generated abstract image adds real
meaning:

- product launches or product surfaces
- hardware, chips, robotics, infrastructure, data centers
- developer tools, agent toolchains, platform ecosystems
- research concepts that benefit from metaphorical visuals
- provenance, safety, policy, or evaluation systems that need a clear symbol

Use `image_strategy: "none"` when a pure editorial scene is clearer:

- short partnerships or company updates
- funding, hiring, policy, or legal summaries
- metrics-only stories
- stories where a big headline, number, or source badge is stronger than an
  image

Do not scrape or download publisher images unless the user explicitly asks and
the source/license is acceptable.

## Episode Fields

When `image_strategy` is `generate`, include:

```json
{
  "visual_prompt": "Abstract editorial illustration for ...",
  "image_path": "media/images/story-01.png"
}
```

When `image_strategy` is `none`, do not set `image_path`; keep `image_prompt`
empty.

`none` means no image-like visual. Do not add generated images, web images,
SVG-like motifs, decorative diagrams, node-link graphics, icon clusters, or
large abstract illustration panels. Use only typography, numbers, source badges,
simple section color, whitespace, and basic motion.

If `image_path` is missing or the file does not exist, the generator falls back
to the text/layout scene.

## Generated Image Style

Generate images as abstract concept illustrations:

- Editorial magazine aesthetic
- 16:9 bitmap, recommended 1920x1080
- No readable text inside the image
- No logos unless explicitly requested and legally appropriate
- Use the skill palette: cream, ink, vermillion, electric blue, saffron, mauve,
  forest
- Visual metaphors should relate to the story: agents, provenance, model
  reasoning, research, infrastructure, tools, regulation, chips, robotics

## File Placement

Save generated images under:

```text
daily-news-video-runs/<slug>/media/images/story-XX.png
```

Then set:

```json
"image_path": "media/images/story-XX.png"
```
