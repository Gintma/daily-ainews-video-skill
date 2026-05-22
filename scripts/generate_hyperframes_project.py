#!/usr/bin/env python3
"""Generate a standalone HyperFrames news-video project from episode.json."""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_VOICE_REFERENCE = SKILL_DIR / "assets/voice-reference.wav"
DEFAULT_VOICE_TRANSCRIPT = SKILL_DIR / "assets/voice-reference-transcript.txt"
DEFAULT_BGM = SKILL_DIR / "assets/background-music.mp3"

PALETTE = ["cream", "ink", "electric", "cream", "ink", "electric"]
COLORS = {
    "cream": {"bg": "#F5EDE0", "fg": "#1A1A1A", "accent": "#FF4A1C", "wipe": "#2B4BFF"},
    "ink": {"bg": "#1A1A1A", "fg": "#F5EDE0", "accent": "#FFC93C", "wipe": "#D4A5E8"},
    "electric": {"bg": "#2B4BFF", "fg": "#F5EDE0", "accent": "#FFC93C", "wipe": "#1A1A1A"},
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def split_words(text: str) -> str:
    return " ".join(f"<span>{esc(part)}</span>" for part in text.split())


def split_metric(text: str) -> str:
    parts = re.findall(r"[A-Za-z0-9+.%/]+|[\u4e00-\u9fff]|[^\s]", text)
    return "".join(f"<span>{esc(part)}</span>" for part in parts if part.strip())


def media_src(path: str) -> str:
    if path.startswith(("http://", "https://", "/", "../")):
        return path
    return f"../{path}"


def media_available(path: str, out_dir: Path) -> bool:
    if path.startswith(("http://", "https://")):
        return True
    if path.startswith("/"):
        return Path(path).exists()
    if path.startswith("../"):
        return (out_dir / "compositions" / path).resolve().exists()
    return (out_dir / path).exists()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def update_story_duration(path: Path, duration: float) -> None:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r'data-duration="[^"]+"', f'data-duration="{duration:.3f}"', text, count=1)
    if updated != text:
        path.write_text(updated, encoding="utf-8")


def source_badge(story: dict) -> str:
    date = str(story.get("date", ""))
    month_day = date
    match = re.match(r"\d{4}-(\d{2})-(\d{2})", date)
    if match:
        month_day = f"{int(match.group(1))}月{int(match.group(2))}日"
    return f"来源：{story.get('source', '')} · {month_day}"


def story_layout(story: dict, has_image: bool) -> str:
    direction = story.get("visual_direction") or {}
    layout = direction.get("layout") or ("image-led" if has_image else "typography-led")
    allowed = {"typography-led", "image-led", "diagram-led", "split-panel", "poster"}
    return layout if layout in allowed else "typography-led"


def story_image_strategy(story: dict) -> str:
    direction = story.get("visual_direction") or {}
    strategy = direction.get("image_strategy", "none")
    return strategy if strategy in {"generate", "none"} else "none"


def duration_data(ep: dict) -> list[dict]:
    timing = ep["timing"]
    cursor = 0.0
    scene_seconds = timing.get("scene_seconds")
    if scene_seconds:
        rows = [{"id": "cover", "src": "cover.html", "start": cursor, "duration": scene_seconds[0]}]
        cursor += scene_seconds[0]
        for i, _story in enumerate(ep["stories"], 1):
            duration = scene_seconds[i]
            rows.append({"id": f"story-{i:02d}", "src": f"story-{i:02d}.html", "start": cursor, "duration": duration})
            cursor += duration
        rows.append({"id": "outro", "src": "outro.html", "start": cursor, "duration": scene_seconds[-1]})
        return rows
    rows = [{"id": "cover", "src": "cover.html", "start": cursor, "duration": timing["cover_seconds"]}]
    cursor += timing["cover_seconds"]
    for i, _story in enumerate(ep["stories"], 1):
        rows.append({"id": f"story-{i:02d}", "src": f"story-{i:02d}.html", "start": cursor, "duration": timing["story_seconds"]})
        cursor += timing["story_seconds"]
    rows.append({"id": "outro", "src": "outro.html", "start": cursor, "duration": timing["outro_seconds"]})
    return rows


def caption_tokens(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9+./:_-]*|[\u4e00-\u9fff]|[^\s]", text)
    return [token for token in tokens if token.strip()]


def caption_keywords(ep: dict) -> set[str]:
    keywords: set[str] = set()
    for story in ep["stories"]:
        keywords.add(str(story.get("source", "")).lower())
        for line in story.get("headline_lines", []):
            for token in caption_tokens(str(line)):
                if len(token) >= 2 or re.search(r"[A-Za-z0-9]", token):
                    keywords.add(token.lower())
        for token in caption_tokens(str(story.get("metric", ""))):
            if re.search(r"[0-9A-Za-z%倍亿万]", token):
                keywords.add(token.lower())
    return {item for item in keywords if item}


def is_caption_keyword(token: str, keywords: set[str]) -> bool:
    normalized = token.lower()
    return (
        normalized in keywords
        or bool(re.search(r"[0-9]", token))
        or bool(re.fullmatch(r"[A-Z][A-Z0-9+.-]{1,}", token))
    )


def index_html(ep: dict, has_voice: bool, has_bgm: bool) -> str:
    rows = duration_data(ep)
    total = rows[-1]["start"] + rows[-1]["duration"]
    clips = []
    for row in rows:
        # Avoid sub-millisecond floating-point overlap reports at scene boundaries.
        clip_duration = max(0.5, row["duration"] - 0.001)
        clips.append(f"""
      <div
        id="scene-{row['id']}"
        class="clip"
        data-composition-id="{row['id']}"
        data-composition-src="compositions/{row['src']}"
        data-start="{row['start']:.3f}"
        data-duration="{clip_duration:.3f}"
        data-track-index="1"
      ></div>""")
    audio_clips = []
    if has_bgm:
        audio_clips.append(f"""
      <audio id="background-music" class="clip" data-start="0" data-duration="{total:.3f}" data-track-index="2" src="media/background-music.mp3" data-volume="0.18" loop></audio>""")
    if has_voice:
        audio_clips.append(f"""
      <audio id="voiceover" class="clip" data-start="0" data-duration="{total:.3f}" data-track-index="4" src="media/voice.mp3" data-volume="1"></audio>""")
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #1A1A1A; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="1080" data-height="1920">
      {''.join(clips)}
      <div
        id="captions"
        class="clip"
        data-composition-id="captions"
        data-composition-src="compositions/captions.html"
        data-start="0"
        data-duration="{total:.3f}"
        data-track-index="3"
      ></div>
      {''.join(audio_clips)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines.main = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def cover_html(ep: dict, duration: float) -> str:
    cover = ep["cover"]
    meta = ep["meta"]
    return f"""<template id="cover-template">
  <div id="cover" data-composition-id="cover" data-width="1080" data-height="1920" data-start="0" data-duration="{duration:.3f}">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&family=Inter+Tight:ital,wght@1,200;1,300&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
    <div class="wipe"></div>
    <main class="page">
      <div class="halftone"></div><div class="circle"></div><div class="dot"></div>
      <header><span>日期 / {esc(meta.get('date', ''))}</span><span>{esc(meta.get('topic', 'AI 日报'))}</span></header>
      <section>
        <div class="kicker">{esc(cover['kicker'])}</div>
        <h1>{esc(cover['title'])}</h1>
        <p>{esc(cover['subtitle'])}</p>
      </section>
      <footer>声音打开 · {duration:.0f}秒开场</footer>
    </main>
    <style>
      #cover {{ width:1080px; height:1920px; overflow:hidden; position:relative; background:#FF4A1C; color:#F5EDE0; font-family:'Space Grotesk','PingFang SC',sans-serif; }}
      .wipe {{ display:none; }}
      .page {{ position:relative; height:100%; padding:132px 76px 140px; display:flex; flex-direction:column; justify-content:space-between; }}
      header, footer {{ display:flex; justify-content:space-between; font:700 22px 'JetBrains Mono',monospace; letter-spacing:.12em; z-index:2; }}
      section {{ z-index:2; }}
      .kicker {{ font:800 34px 'JetBrains Mono',monospace; letter-spacing:.16em; color:#FFC93C; margin-bottom:32px; }}
      h1 {{ font-size:170px; line-height:.9; margin:0; letter-spacing:0; max-width:900px; }}
      p {{ font:italic 300 42px 'Inter Tight','PingFang SC',sans-serif; max-width:780px; line-height:1.15; color:#FFC93C; }}
      .halftone {{ position:absolute; inset:-80px; background-image:radial-gradient(circle, rgba(26,26,26,.16) 2.5px, transparent 3px); background-size:40px 40px; }}
      .circle {{ position:absolute; right:-240px; bottom:-260px; width:840px; height:840px; border-radius:50%; background:#1A1A1A; opacity:.85; }}
      .dot {{ position:absolute; right:100px; top:250px; width:120px; height:120px; border-radius:50%; background:#FFC93C; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused:true }});
      tl.from('header span', {{ y:18, stagger:.08, duration:.45, ease:'power3.out' }}, .1);
      tl.from('.kicker', {{ x:-28, duration:.45, ease:'back.out(2)' }}, .22);
      tl.from('h1', {{ y:54, scale:.98, duration:.7, ease:'back.out(1.8)' }}, .32);
      tl.from('p', {{ y:24, duration:.45, ease:'power2.out' }}, .68);
      tl.from('footer', {{ x:28, duration:.4 }}, .88);
      tl.to('.halftone', {{ x:-40, y:-40, duration:12, ease:'none' }}, 0);
      window.__timelines.cover = tl;
    </script>
  </div>
</template>
"""


def story_html(story: dict, index: int, count: int, duration: float, out_dir: Path) -> str:
    theme = COLORS[PALETTE[(index - 1) % len(PALETTE)]]
    headline = story["headline_lines"]
    lines = "\n".join(f"          <span>{esc(line)}</span>" for line in headline)
    comp_id = f"story-{index:02d}"
    image_path = story.get("image_path", "")
    has_image = bool(image_path and media_available(str(image_path), out_dir))
    layout = story_layout(story, has_image)
    image_html = ""
    image_anim = ""
    if has_image:
        image_html = f"""
        <figure class="story-image">
          <img src="{esc(media_src(str(image_path)))}" crossorigin="anonymous" alt="" />
        </figure>"""
        image_anim = "      tl.from('.story-image', { y:28, opacity:0, scale:.96, duration:.55, ease:'power3.out' }, .52);"
    return f"""<template id="{comp_id}-template">
  <div id="{comp_id}" class="layout-{layout}" data-composition-id="{comp_id}" data-width="1080" data-height="1920" data-start="0" data-duration="{duration:.3f}">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&family=Inter+Tight:ital,wght@1,200;1,300&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
    <div class="wipe"></div>
    <main class="page">
      <div class="halftone"></div><div class="ghost">{index:02d}</div>
      <header><span>第 {index:02d} 条 / 共 {count:02d} 条</span><span>{esc(story['source'])}</span></header>
      <section class="body">
{image_html}
        <div class="tag">{esc(story['category'])}</div>
        <h1>
{lines}
        </h1>
        <div class="source-badge">{esc(source_badge(story))}</div>
        <div class="metric">
          <div class="label">亮点</div>
          <div class="value">{split_metric(str(story['metric']))}</div>
        </div>
        <aside>
          <div class="aside-label">这意味着</div>
          <p>{esc(story['callout'])}</p>
        </aside>
      </section>
    </main>
    <style>
      #{comp_id} {{ width:1080px; height:1920px; overflow:hidden; position:relative; background:{theme['bg']}; color:{theme['fg']}; font-family:'Space Grotesk','PingFang SC',sans-serif; }}
      .wipe {{ position:absolute; inset:0; background:{theme['wipe']}; z-index:20; transform-origin:{'left' if index % 2 == 0 else 'right'} center; }}
      .page {{ position:relative; height:100%; padding:132px 70px 170px; display:flex; flex-direction:column; justify-content:flex-start; }}
      header {{ display:flex; justify-content:space-between; font:700 20px 'JetBrains Mono',monospace; letter-spacing:.11em; z-index:2; border-bottom:2px solid currentColor; padding-bottom:18px; }}
      .body {{ z-index:2; display:flex; flex-direction:column; gap:28px; }}
      .story-image {{ margin:0 0 4px; width:100%; max-width:940px; height:260px; border:3px solid currentColor; box-shadow:14px 14px 0 {theme['accent']}; overflow:hidden; background:color-mix(in srgb, {theme['accent']} 18%, transparent); }}
      .story-image img {{ display:block; width:100%; height:100%; object-fit:cover; }}
      .tag {{ align-self:flex-start; border:1.5px solid currentColor; border-radius:999px; padding:10px 22px; font:700 20px 'JetBrains Mono',monospace; letter-spacing:.14em; }}
      h1 {{ margin:0; font-size:112px; line-height:.96; letter-spacing:0; max-width:940px; }}
      h1 span {{ display:block; }}
      h1 span:nth-child(2) {{ font-family:'Inter Tight','PingFang SC',sans-serif; font-style:italic; font-weight:300; color:{theme['accent']}; }}
      .source-badge {{ align-self:flex-start; font:800 20px 'JetBrains Mono',monospace; letter-spacing:.08em; opacity:.88; border-bottom:2px solid {theme['accent']}; padding-bottom:8px; }}
      .metric .label {{ font:700 20px 'JetBrains Mono',monospace; letter-spacing:.18em; opacity:.75; }}
      .metric .value {{ font-size:118px; line-height:1; color:{theme['accent']}; font-weight:700; margin-top:8px; }}
      .metric .value span {{ display:inline-block; transform-origin:50% 80%; will-change:transform, opacity; }}
      aside {{ border-left:7px solid {theme['accent']}; background:color-mix(in srgb, {theme['accent']} 14%, transparent); padding:24px 28px; max-width:900px; }}
      .aside-label {{ font:800 20px 'JetBrains Mono',monospace; color:{theme['accent']}; letter-spacing:.18em; margin-bottom:10px; }}
      aside p {{ margin:0; font:italic 300 34px/1.25 'Inter Tight','PingFang SC',sans-serif; }}
      .ghost {{ position:absolute; left:-40px; top:120px; font-size:760px; line-height:.8; font-weight:700; color:{theme['accent']}; opacity:.10; }}
      .halftone {{ position:absolute; inset:-80px; background-image:radial-gradient(circle, currentColor 2px, transparent 2.5px); background-size:36px 36px; opacity:.08; }}
      .layout-image-led .story-image {{ height:390px; margin-bottom:14px; }}
      .layout-image-led h1 {{ font-size:98px; }}
      .layout-split-panel .body {{ display:grid; grid-template-columns:1fr 1fr; column-gap:34px; align-items:start; }}
      .layout-split-panel .story-image {{ grid-row:1 / span 5; height:760px; }}
      .layout-split-panel h1 {{ font-size:82px; }}
      .layout-split-panel aside {{ grid-column:1 / -1; }}
      .layout-diagram-led h1 {{ max-width:820px; }}
      .layout-diagram-led .metric {{ margin-left:auto; max-width:540px; text-align:right; }}
      .layout-poster .body {{ min-height:1260px; justify-content:center; }}
      .layout-poster h1 {{ font-size:132px; }}
      .layout-poster .story-image {{ display:none; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused:true }});
      tl.to('.wipe', {{ scaleX:0, duration:.52, ease:'power4.inOut' }}, 0);
      tl.from('header span', {{ y:24, opacity:0, stagger:.08, duration:.45 }}, .32);
      tl.from('.tag', {{ x:-30, rotate:-5, opacity:0, duration:.5, ease:'back.out(2)' }}, .48);
      tl.from('h1 span', {{ y:72, opacity:0, duration:.55, stagger:.10, ease:'back.out(1.8)' }}, .62);
      tl.from('.source-badge', {{ x:-30, opacity:0, duration:.4 }}, 1.15);
      tl.from('.metric .label', {{ x:-18, opacity:0, duration:.34, ease:'power3.out' }}, 1.28);
      tl.from('.metric .value span', {{ y:60, opacity:0, rotateX:-55, scale:.86, duration:.72, stagger:.035, ease:'back.out(1.65)' }}, 1.35);
      tl.to('.metric .value span', {{ y:-4, duration:1.35, stagger:.02, ease:'sine.inOut', yoyo:true, repeat:1 }}, 2.28);
      tl.from('aside', {{ x:-36, opacity:0, duration:.5, ease:'power3.out' }}, 1.75);
{image_anim}
      tl.to('.halftone', {{ x:-36, y:-36, duration:14, ease:'none' }}, 0);
      tl.to('.ghost', {{ y:-24, duration:8, ease:'sine.inOut' }}, 0.8);
      window.__timelines['{comp_id}'] = tl;
    </script>
  </div>
</template>
"""


def outro_html(ep: dict, duration: float) -> str:
    outro = ep["outro"]
    return f"""<template id="outro-template">
  <div id="outro" data-composition-id="outro" data-width="1080" data-height="1920" data-start="0" data-duration="{duration:.3f}">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&family=Inter+Tight:ital,wght@1,200;1,300&family=JetBrains+Mono:wght@400;700;800&display=swap" rel="stylesheet">
    <div class="wipe"></div>
    <main class="page"><div class="circle"></div><div class="dot"></div>
      <header><span>片尾</span><span>AI 日报</span></header>
      <section><h1>{esc(outro['title'])}</h1><p>{esc(outro['subtitle'])}</p></section>
      <footer>关注更新</footer>
    </main>
    <style>
      #outro {{ width:1080px; height:1920px; overflow:hidden; position:relative; background:#1A1A1A; color:#F5EDE0; font-family:'Space Grotesk','PingFang SC',sans-serif; }}
      .wipe {{ position:absolute; inset:0; background:#D4A5E8; z-index:20; transform-origin:left center; }}
      .page {{ height:100%; padding:132px 76px 150px; display:flex; flex-direction:column; justify-content:space-between; position:relative; }}
      header, footer {{ display:flex; justify-content:space-between; font:700 22px 'JetBrains Mono',monospace; letter-spacing:.14em; z-index:2; }}
      h1 {{ font-size:168px; line-height:.9; color:#FFC93C; margin:0; }}
      p {{ font:italic 300 42px/1.2 'Inter Tight','PingFang SC',sans-serif; max-width:760px; }}
      .circle {{ position:absolute; left:-260px; bottom:-260px; width:820px; height:820px; border-radius:50%; background:#D4A5E8; opacity:.32; }}
      .dot {{ position:absolute; right:110px; top:240px; width:120px; height:120px; border-radius:50%; background:#FFC93C; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused:true }});
      tl.to('.wipe', {{ scaleX:0, duration:.55, ease:'power4.inOut' }}, 0);
      tl.from('header span', {{ y:24, opacity:0, stagger:.08, duration:.45 }}, .3);
      tl.from('h1', {{ y:80, opacity:0, duration:.6, ease:'back.out(1.8)' }}, .5);
      tl.from('p', {{ y:30, opacity:0, duration:.5 }}, .9);
      tl.from('footer', {{ x:30, opacity:0, duration:.45 }}, 1.2);
      tl.to(['section','footer','header','.circle','.dot'], {{ opacity:0, duration:.55 }}, {max(0, duration - 0.65):.2f});
      window.__timelines.outro = tl;
    </script>
  </div>
</template>
"""


def captions_html(ep: dict, rows: list[dict]) -> str:
    groups = []
    keywords = caption_keywords(ep)
    scripts = [ep["cover"]["script"]] + [s["script"] for s in ep["stories"]] + [ep["outro"]["script"]]
    for row, script in zip(rows, scripts):
        chunks = [part.strip() for part in script.replace("。", "。|").replace("，", "，|").split("|") if part.strip()]
        slot = row["duration"] / max(1, len(chunks))
        for i, chunk in enumerate(chunks):
            start = row["start"] + i * slot + 0.08
            end = min(row["start"] + (i + 1) * slot - 0.08, row["start"] + row["duration"] - 0.08)
            tokens = caption_tokens(chunk)
            word_slot = max(0.08, (end - start) / max(1, len(tokens)))
            words = []
            for word_index, token in enumerate(tokens):
                word_start = start + word_index * word_slot
                words.append({
                    "t": token,
                    "s": round(word_start, 2),
                    "e": round(min(word_start + word_slot * 0.9, end), 2),
                    "kw": is_caption_keyword(token, keywords),
                })
            groups.append({"start": round(start, 2), "end": round(end, 2), "text": chunk, "words": words})
    return f"""<template id="captions-template">
  <div id="captions" data-composition-id="captions" data-width="1080" data-height="1920" data-start="0" data-duration="{rows[-1]['start'] + rows[-1]['duration']:.3f}">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@700;800&display=swap" rel="stylesheet">
    <div id="cap"></div>
    <style>
      #captions {{ width:1080px; height:1920px; position:relative; pointer-events:none; overflow:visible; }}
      #cap {{ position:absolute; left:70px; right:70px; bottom:170px; text-align:center; z-index:100; }}
      .g {{ position:absolute; left:0; right:0; bottom:0; opacity:0; visibility:hidden; display:flex; flex-wrap:wrap; justify-content:center; gap:8px 10px; color:#F5EDE0; font:800 56px/1.2 'JetBrains Mono','PingFang SC',sans-serif; text-shadow:4px 4px 0 #1A1A1A, -2px -2px 0 #1A1A1A, 0 0 20px rgba(26,26,26,.6); }}
      .w {{ display:inline-block; min-width:.55em; opacity:.58; transform:translateY(12px) scale(.94); transform-origin:center bottom; }}
      .w.kw {{ color:#FFC93C; }}
      .w.on {{ opacity:1; color:#FFC93C; text-shadow:4px 4px 0 #1A1A1A, 0 0 26px rgba(255,201,60,.72); }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const groups = {json.dumps(groups, ensure_ascii=False)};
      const root = document.getElementById('cap');
      groups.forEach((g, i) => {{
        const el = document.createElement('div');
        el.className = 'g';
        el.id = 'cg' + i;
        g.words.forEach((word, j) => {{
          const span = document.createElement('span');
          span.className = 'w' + (word.kw ? ' kw' : '');
          span.id = 'cg' + i + 'w' + j;
          span.textContent = word.t;
          el.appendChild(span);
        }});
        root.appendChild(el);
      }});
      const tl = gsap.timeline({{ paused:true }});
      groups.forEach((g, i) => {{
        const s = '#cg' + i;
        tl.set(s, {{ visibility:'visible' }}, g.start);
        tl.fromTo(s, {{ opacity:0, y:20, scale:.94 }}, {{ opacity:1, y:0, scale:1, duration:.16, ease:'back.out(2)' }}, g.start);
        g.words.forEach((word, j) => {{
          const ws = '#cg' + i + 'w' + j;
          tl.to(ws, {{ opacity:1, y:0, scale:1.08, color:'#FFC93C', duration:.12, ease:'back.out(2)' }}, word.s);
          tl.to(ws, {{ scale:1, duration:.12 }}, Math.max(word.s + .14, word.e - .08));
        }});
        tl.to(s, {{ opacity:0, y:-12, duration:.12 }}, Math.max(g.start + .2, g.end - .12));
        tl.set(s, {{ visibility:'hidden' }}, g.end);
      }});
      window.__timelines.captions = tl;
    </script>
  </div>
</template>
"""


def main() -> None:
    args = [arg for arg in sys.argv[1:] if arg != "--overwrite-stories"]
    overwrite_stories = "--overwrite-stories" in sys.argv[1:]
    if len(args) != 1:
        raise SystemExit("Usage: generate_hyperframes_project.py path/to/episode.json [--overwrite-stories]")
    episode_path = Path(args[0]).resolve()
    out_dir = episode_path.parent
    ep = json.loads(episode_path.read_text(encoding="utf-8"))
    rows = duration_data(ep)
    total = rows[-1]["start"] + rows[-1]["duration"]
    ep["timing"]["total_seconds"] = total
    write(episode_path, json.dumps(ep, ensure_ascii=False, indent=2) + "\n")

    for name in ["compositions", "scripts", "media/el", "media/images", "renders"]:
        (out_dir / name).mkdir(parents=True, exist_ok=True)

    if DEFAULT_BGM.exists():
        shutil.copy2(DEFAULT_BGM, out_dir / "media/background-music.mp3")
    if DEFAULT_VOICE_REFERENCE.exists():
        shutil.copy2(DEFAULT_VOICE_REFERENCE, out_dir / "media/voice-reference.wav")
    if DEFAULT_VOICE_TRANSCRIPT.exists():
        shutil.copy2(DEFAULT_VOICE_TRANSCRIPT, out_dir / "media/voice-reference-transcript.txt")

    write(out_dir / "hyperframes.json", json.dumps({
        "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}
    }, indent=2) + "\n")
    write(out_dir / "meta.json", json.dumps({"id": ep["meta"]["slug"], "name": ep["meta"]["title"]}, ensure_ascii=False, indent=2) + "\n")
    write(out_dir / "index.html", index_html(
        ep,
        has_voice=(out_dir / "media/voice.mp3").exists(),
        has_bgm=(out_dir / "media/background-music.mp3").exists(),
    ))
    write(out_dir / "compositions/cover.html", cover_html(ep, ep["timing"]["cover_seconds"]))
    for i, story in enumerate(ep["stories"], 1):
        story_path = out_dir / f"compositions/story-{i:02d}.html"
        if story_path.exists() and not overwrite_stories:
            update_story_duration(story_path, ep["timing"]["story_seconds"])
        else:
            write(story_path, story_html(story, i, len(ep["stories"]), ep["timing"]["story_seconds"], out_dir))
    write(out_dir / "compositions/outro.html", outro_html(ep, ep["timing"]["outro_seconds"]))
    write(out_dir / "compositions/captions.html", captions_html(ep, rows))

    scripts = [ep["cover"]["script"]] + [s["script"] for s in ep["stories"]] + [ep["outro"]["script"]]
    for i, script in enumerate(scripts, 1):
        write(out_dir / f"scripts/s{i:02d}.txt", script + "\n")
    narration = "\n\n".join(f"SCENE {i:02d}\n{script}" for i, script in enumerate(scripts, 1))
    write(out_dir / "scripts/narration.txt", narration + "\n")

    print(f"Generated HyperFrames project: {out_dir}")
    print(f"Scenes: {len(rows)}  Duration: {total:.2f}s")


if __name__ == "__main__":
    main()
