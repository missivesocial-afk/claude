# Canva build: "Celebrating the Visionary"

The locked design (F3, "name ledge"), rebuilt in Canva with these changes:

- Headline changed from HAPPY BIRTHDAY to **CELEBRATING THE / VISIONARY**.
- The small handwritten side notes are removed.
- **HAPPY BIRTHDAY** is added above his name in the green band.

Local reference render: `../locked-post/locked-celebrating-the-visionary.png` (from `../locked-post.html`).

## Assets uploaded to Canva

| File | Canva asset |
|---|---|
| `rishabh-chair-cutout.png` (650 x 790, transparent) | Rishabh M Shah cutout (chair pose) |
| `1fcode-logo-on-dark.png` (1436 x 256, transparent) | 1FCode logo (for dark backgrounds) |

## Layout (1080 x 1350)

| Element | Position (left, top) | Size | Colour |
|---|---|---|---|
| Background | 0, 0 | 1080 x 1350 | Bond White #F4F4ED |
| Lime highlight bar | 56, 96 | 830 x 112, rotated -1.2° | Light Lime #EAE26A |
| "CELEBRATING THE" | 68, 74 | 128 px condensed caps | Legacy Green #043335 |
| "VISIONARY" | 62, 212 | 250 px condensed caps | Legacy Green #043335 |
| Photo cutout | 244, 404 | 618 x 751 | full colour |
| Green band | 0, 1062 | 1080 x 288 | Legacy Green #043335 |
| "HAPPY BIRTHDAY" | 72, 1156 | 26 px, letter-spaced | Bond White |
| "Rishabh M Shah" | 70, 1196 | 74 px bold | Light Lime #EAE26A |
| "Founder & CEO, 1FC Group of Companies" | 72, 1284 | 28 px | Bond White |
| 1FCode logo | 752, 1196 | 258 x 46 | logo colours |

## Saved Canva design

- Design: "1FCode founder birthday Instagram post" (`DAHXgFsHbwM`)
- Edit link: https://www.canva.com/d/VZEVkJb9WtxT0zE
- Canva generated the page at 1080 x 1440 (3:4), which Instagram accepts for portrait posts. The local render in `../locked-post/` is 1080 x 1350 (4:5).

## Typography update

Canva's editing tools can't set a font family, so the headline (Anton) and the name block (Inter + Google Sans) are placed as transparent graphics rendered from `typo.html`: `headline.png` and `name-block.png`. The photo, logo and colour shapes are still separate Canva elements. To edit the words, change `typo.html`, re-render, and replace the two images in Canva.

## Page 2: editable-text version

Page 2 of the same design has every word as editable Canva text, in fonts close to the original:

- "VISIONARY": Canva's Anton-style heavy condensed font.
- "CELEBRATING THE": a narrower condensed display font. Canva's tools here can only reuse fonts already placed in a design, so only one Anton text box was available.
- Name, "HAPPY BIRTHDAY" and the title: a Poppins-style geometric sans.

It was built in a helper design, "Helper: editable page 2 source (safe to delete)" (`DAHXgDxJ_9A`), and copied in. A worker restart also left a blank page 3 and a partial copy of page 1 as page 4. The user chose to keep them, and they can be deleted in Canva.

## 9:16 Story

- Canva design: "1FCode founder birthday Instagram Story" (`DAHXg2l7WkA`), 1080 x 1920, all text editable.
- Centred layout: logo at the top, headline, photo with hands on the green band, then HAPPY BIRTHDAY (44 px), name and title centred in the band. Text stays clear of the Story UI at the top and bottom.
- Ready-to-post image with the exact original typography: `../story-post/story-celebrating-the-visionary.png` (from `../story-post.html`).
