Create a horizontal-swipe editorial magazine as a single responsive HTML file, built for both desktop and mobile. Before the magazine, show a full-screen intro with the source URL and time window displayed — tapping/clicking anywhere or pressing any key dismisses the intro and the magazine begins.

=== INPUTS (fill these in) ===
SOURCE_URL: [paste the website or source here, e.g. news.ycombinator.com]
TIME_WINDOW: [Past 24 hours / This week / This month]
NUMBER_OF_ITEMS: [e.g. 10 — total pages will be items + 2 for cover/back]
PERSONAL_CONTEXT: [brief note about who you are / what you work on, so the "How to apply this" callouts are tailored]

=== AESTHETIC ===
Bold, fun, modern editorial — think Monocle energy but playful, not austere. Full-bleed, edge-to-edge, no floating cards or boxed-in padding containers.

Palette (all used):
- Cream #F5EDE0 (paper)
- Ink #1A1A1A (primary text)
- Vermillion #FF4A1C (primary accent)
- Electric blue #2B4BFF (secondary accent)
- Saffron #FFC93C (for dark backgrounds only)
- Mauve #D4A5E8 (for dark backgrounds only)
- Forest #0F4D3A (deep accent)

Contrast rules — obey these to avoid same-on-same clashes:
- Cream bg → ink text; accents are vermillion, electric, forest
- Ink bg → cream text; accents are saffron, mauve, vermillion
- Electric blue bg → cream text; accent is saffron ONLY (never vermillion — they vibrate)
- Vermillion bg → cream text; accents are ink and saffron only
- Ghost/decorative elements stay at 0.08–0.15 opacity so they never compete with foreground
- Description text min 0.82 opacity on cream, 0.85 on dark

=== TYPOGRAPHY (all sans) ===
- Space Grotesk (700) — bold display, headlines, metrics, brand
- Inter Tight (200 italic) — the light/delicate counterpoint word inside each headline
- JetBrains Mono — all metadata, tags, page numbers, UI labels

Each headline mixes Space Grotesk bold with one Inter Tight italic phrase in an accent color. No two headlines should look identical in structure.

=== STRUCTURE ===
Page 1: Cover (vermillion bg)
Pages 2 to N+1: One page per item from the source
Page N+2: Back cover (ink bg)

Alternate content page backgrounds in a rhythm: cream → ink → electric blue → cream → ink → electric... Never two same-colored pages in a row.

=== INTRO SCREEN ===
Full-screen, cream background, grid layout: left side has a big Space Grotesk headline with one italic Inter Tight phrase and a short Inter Tight blurb; right side displays the issue metadata — source URL, time window, item count, date — styled as Space Grotesk text with underline borders, like a newspaper masthead. No form, no button. Instead, a subtle animated cue at the bottom: "Tap anywhere to begin →" in JetBrains Mono. Decorative saffron and electric circles in the background (don't let them overlap text).

Whole intro is clickable — any click, tap, keypress, or swipe dismisses it with a 0.6s fade + translateY transition.

On mobile: stack vertically, metadata below headline.

=== EACH CONTENT PAGE (55/45 split on desktop, stacked on mobile) ===
Left column:
- Giant ghost rank number (Space Grotesk 700, ~34vw, 0.08–0.15 opacity) absolute positioned top-left behind content
- Category tag (pill, 1.5px border, JetBrains Mono uppercase)
- Editorial headline (clamp(40px, 5.6vw, 110px), Space Grotesk bold + one Inter Tight italic phrase in accent color)
- Source path (JetBrains Mono, 0.7 opacity)
- Description (Inter Tight, clamp(15px, 1.4vw, 21px), 1.5 line-height)

Right column:
- Metric label (JetBrains Mono uppercase, small)
- Headline metric (Space Grotesk 700, clamp(72px, 7.5vw, 170px), in accent color) — e.g. stars, points, upvotes
- Meta tag with colored dot (language, comment count, etc.)
- Callout box: tinted bg at ~0.08–0.18 alpha of the accent color, 4px left border in solid accent color, JetBrains Mono label ("HOW TO APPLY THIS") and Inter Tight italic body text. This is a personalized note about how the reader should think about applying this item to their own work, based on PERSONAL_CONTEXT.

Page meta bar at top: "Entry 0X of NN" left, source URL right, 1.5px bottom border.

=== COVER ===
Vermillion background, cream text. Issue number + date top-left, source name top-right. Huge two-line title: "[Word]" in Space Grotesk bold cream, "[phrase]" in Inter Tight italic saffron. Decorative ink circle bottom-right corner (not overlapping title), small saffron circle top-right. Kicker sentence bottom-left in Inter Tight italic. "→ Swipe" bottom-right.

=== BACK COVER ===
Ink background, cream text. Mauve circle bottom-left corner, saffron dot top-right. "See you [Inter Tight italic phrase in saffron]" huge title. Three-column colophon: Source / Typography / Next Issue — Space Grotesk headings in saffron, JetBrains Mono body.

=== INTERACTION ===
- CSS transform horizontal pagination, 0.7s cubic-bezier(0.76, 0, 0.24, 1)
- Arrow keys, wheel (throttled 800ms), touch swipe (60px threshold, direction-locked so horizontal swipe only triggers if horizontal motion > 1.5× vertical), clickable dot nav
- Page counter bottom-right, hint "← → swipe" bottom-left (hidden on mobile), dots center-bottom, all with mix-blend-mode: difference so they read on any page color
- safe-area-inset-bottom respected

=== RESPONSIVE (critical) ===
All font sizes use clamp() — never fixed px for display type. Min touch target 44px.

Desktop (>768px): 55/45 two-column grid on content pages.

Mobile (≤768px):
- Content grid collapses to single column, left content above right
- content-grid becomes overflow-y: auto with -webkit-overflow-scrolling: touch so long content scrolls inside the page without breaking horizontal swipe
- Decorative circles reposition and resize (use min-width/min-height so they never shrink to nothing)
- Hint label hidden, dots shrink, headlines use larger vw ratios
- Intro metadata stacks below headline

Landscape phones (max-height: 500px): keep 55/45 split, reduce padding, shrink display type.
Very small phones (≤380px): hard caps on headline/metric sizes.

=== OUTPUT ===
Single self-contained HTML file. Fonts via Google Fonts. No external JS libraries. Clean, commented CSS. Real working navigation. Pull actual content from SOURCE_URL for the specified TIME_WINDOW — real headlines, real metrics, real source paths — and write genuine editorial headlines (not just repeating the source title). Each "How to apply this" callout must be specific to PERSONAL_CONTEXT, not generic.

