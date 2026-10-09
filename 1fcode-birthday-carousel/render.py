#!/usr/bin/env python3
"""Render every .slide in a carousel HTML file to PNGs plus one PDF.

Usage: python3 render.py carousel.html out_dir
Each .slide must have a fixed pixel size set in CSS (e.g. 1080x1350).
Outputs: out_dir/slide-01.png ... and out_dir/carousel.pdf,
plus out_dir/contact-sheet.png for quick visual QA.
"""
import sys, pathlib, img2pdf
from PIL import Image
from playwright.sync_api import sync_playwright

src = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "out").resolve()
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(viewport={"width": 1200, "height": 2000}, device_scale_factor=1)
    pg.goto(src.as_uri())
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    # Overflow check: any text element that spills out of its slide
    problems = pg.evaluate("""() => {
      const out = [];
      document.querySelectorAll('.slide').forEach((s, i) => {
        const r = s.getBoundingClientRect();
        s.querySelectorAll('*:not(.bleed):not(.bleed *)').forEach(el => {
          const e = el.getBoundingClientRect();
          if (e.width && (e.right > r.right + 1 || e.bottom > r.bottom + 1 || e.left < r.left - 1))
            out.push(`slide ${i+1}: <${el.tagName.toLowerCase()} class="${el.className}"> overflows`);
        });
        if (s.scrollHeight > s.clientHeight + 1) out.push(`slide ${i+1}: content taller than slide`);
      });
      return out;
    }""")
    slides = pg.query_selector_all(".slide")
    paths = []
    for i, s in enumerate(slides, 1):
        name = s.get_attribute("data-name")
        f = out / (f"{name}.png" if name else f"slide-{i:02d}.png")
        s.screenshot(path=str(f))
        paths.append(f)
    b.close()

# PDF (one page per slide, exact pixel size)
(out / "carousel.pdf").write_bytes(img2pdf.convert([str(x) for x in paths]))

# Contact sheet for QA
ims = [Image.open(x) for x in paths]
w, h = ims[0].size
cols = min(4, len(ims)); rows = -(-len(ims) // cols)
scale = 0.3
tw, th = int(w * scale), int(h * scale)
sheet = Image.new("RGB", (cols * tw + (cols + 1) * 16, rows * th + (rows + 1) * 16), "#888")
for k, im in enumerate(ims):
    r, c = divmod(k, cols)
    sheet.paste(im.convert("RGB").resize((tw, th)), (16 + c * (tw + 16), 16 + r * (th + 16)))
sheet.save(out / "contact-sheet.png")

print(f"Rendered {len(paths)} slides to {out}")
print("OVERFLOW WARNINGS:\n  " + "\n  ".join(problems) if problems else "No overflow detected.")
