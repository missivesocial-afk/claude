# Missive brand colour guide

Source of truth: the active **Missive Brand** design (`missive-brand`) on the Missive WordPress site, captured from missivedigital.com. If the site design changes, update this file to match.

## Palette

| Token | Hex | Role |
|---|---|---|
| `--bg` | `#F9F7F6` | Warm off-white ground, default background |
| `--surface` | `#FFFFFF` | Cards and panels on the warm ground |
| `--ink` | `#292929` | Charcoal: headings, body, header CTA pill |
| `--muted` | `#54595F` | Secondary text, captions, small labels |
| `--accent` | `#0C81F3` | Missive blue: gradient start; alone only for small icons and focus states |
| `--accent-2` | `#EB8988` | Coral: gradient end; never used alone as a large fill |
| `--lavender-grey` | `#F3F3F7` | Alternate light band, secondary cards |
| `--lilac` | `#DAD0FF` | Hero wash, start |
| `--mint` | `#D8FFD8` | Hero wash, end |
| `--line` | `#DEDEDE` | Dividers and hairlines |
| `--night` | `#171720` | Dark band / dark scenes |
| `--night-line` | `#30303D` | Dividers on night |
| `--mist-on-night` | `#A3A3B2` | Secondary text on night |

## Gradients

```css
--brand-gradient: linear-gradient(90deg, #0C81F3 0%, #EB8988 100%);   /* signature: buttons, badges, one accent word */
--hero-wash:      linear-gradient(135deg, #DAD0FF 0%, #D8FFD8 100%);  /* hero and end-card backgrounds */
```

Gradient text (one highlighted word):
```css
.accent-word { background: var(--brand-gradient); -webkit-background-clip: text; background-clip: text; color: transparent; }
```

## Drop-in `:root` for a video or page

```css
:root{
  --bg:#F9F7F6; --surface:#FFFFFF; --ink:#292929; --muted:#54595F;
  --accent:#0C81F3; --accent-2:#EB8988;
  --lavender-grey:#F3F3F7; --lilac:#DAD0FF; --mint:#D8FFD8; --line:#DEDEDE;
  --night:#171720; --night-line:#30303D; --mist-on-night:#A3A3B2;
  --brand-gradient:linear-gradient(90deg,#0C81F3,#EB8988);
  --hero-wash:linear-gradient(135deg,#DAD0FF,#D8FFD8);
  --shadow-card:0 25px 70px rgba(0,0,0,.07);
  --font-head:"Instrument Sans",sans-serif; --font-body:"Rubik",sans-serif;
}
```

## Typography

| Use | Font | Weight | Notes |
|---|---|---|---|
| Display / headline | Instrument Sans | 600 | −0.03em tracking, 1.04–1.15 leading |
| Large list titles | Instrument Sans | 400 | light and large |
| Buttons / CTA | Instrument Sans | 600 | white on the gradient pill |
| Body / captions | Rubik | 400 | 1.7 leading on web; 1.3 in video captions |

Both are Google Fonts (OFL). For video, download the woff2 files into `source/fonts/` and load them with `@font-face`.

## Shapes and depth

- Buttons and badges are pills (fully rounded). Cards 20 px radius, hero card 28 px, icon tiles 12 px.
- Shadows are soft, wide and low-opacity, and only on white cards over the warm ground. Primary button gets a soft blue-tinted shadow. No hard shadows.
- Feature icons: 44 px tile filled with the brand gradient, white icon.

## Contrast (check before shipping)

| Pairing | Use it for |
|---|---|
| `#292929` on `#F9F7F6` / `#FFFFFF` | All text. Safe at any size |
| `#54595F` on `#F9F7F6` | Secondary text, 14 px+ |
| White on brand gradient | Buttons and badges only, 16 px+ semibold; the coral end is light, so keep text bold and short |
| `#FFFFFF` / `#A3A3B2` on `#171720` | Dark scenes: white for headlines, mist for secondary |
| Coral or blue as a flat background behind body text | Never |

## Do / don't

**Do**
- Use the brand gradient for primary CTAs, eyebrow badges and at most one highlighted word per heading.
- Keep headings charcoal Instrument Sans with tight negative tracking.
- Alternate bands: warm ground → lavender-grey → night, for rhythm.

**Don't**
- Use blue or coral as large flat fills behind text.
- Add off-palette colours (no purple-to-pink "AI" gradients, no neon).
- Use Inter or system fonts in place of Instrument Sans / Rubik.
- Invent statistics, reviews or customer logos. Avoid em-dashes in copy.
