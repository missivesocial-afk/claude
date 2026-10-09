# Missive letterhead (A4)

Three letterhead directions for **Missive Digital Marketing LLP**, built from the colour logo.

| | Design | Idea |
|---|---|---|
| A | `a-editorial-minimal.html` | Quiet header, aqua→teal accent rule, three-column legal footer, two-tone base bar |
| B | `b-side-rail.html` | Deep-teal edge rail with the aqua fold and vertical type |
| C | `c-fold-corner.html` | The mark as a folded page corner, plus a faint fold watermark |

### Creative directions
| | Design | Idea |
|---|---|---|
| D | `d-top-result.html` | Header is a search bar, footer is a search result; continuation sheet ends in "missssssive." pagination |
| E | `e-fold-reveal.html` | Printed both sides with DL fold ticks; folded, the back reads "You've got a missive." with a return address |
| F | `f-flight-path.html` | The mark flies as a paper plane along a dashed path and lands as the full stop of "Messages that land." |

Every design has a **first page** and a **continuation sheet** (page 2+). Design E also has a **reverse** sheet — print page 1 and the reverse duplex (flip on long edge).

## Files
- `output/*-letterhead.pdf` — blank print masters (page 1 + continuation), A4, no margins
- `output/*-sample-letter.pdf` — the same page with a sample letter, for review
- `output/*-preview.png`, `*-blank.png`, `*-continuation.png` — previews
- `output/all-three-designs.png`, `output/creative-designs.png` — side-by-side comparisons
- `assets/missive-logo.svg` — colour logo, redrawn as vectors (wordmark outlined)
- `assets/missive-mark.svg` — colour mark only
- `assets/missive-logo-white.svg` — for dark backgrounds
- `brand.css` — colours, fonts and shared styles

## Brand palette (sampled from the logo)
| Token | Hex | Use |
|---|---|---|
| Aqua | `#5FC7C2` | Light panel of the mark |
| Teal | `#1B8F9B` | Fold of the mark, full stop |
| Teal ink | `#0F5E67` | Small text on white |
| Ink | `#0B0C0E` | Wordmark |

Typeface: **Figtree** (SIL Open Font License), the closest free match to the wordmark.

## Before printing
- Replace the `XXX-XXXX` LLPIN placeholder (search for `class="todo"`). An LLP's official correspondence should show its name, registered office and LLPIN — confirm the exact wording with your CA.
- The logo was redrawn from a screenshot. For final print, swap in the original vector logo (`.ai` / `.eps` / `.svg`) at `assets/missive-logo.svg`.
- "Content · SEO · Growth" (B, C) and "Messages that land." (F) are placeholder lines — change or remove them.

## Re-rendering
```
PLAYWRIGHT_PATH=/opt/node-tools/node_modules/playwright node render.cjs            # all designs
node render.cjs f-flight-path   # one design
```
