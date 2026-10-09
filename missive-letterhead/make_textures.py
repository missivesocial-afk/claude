"""Grainy mesh-gradient textures in Missive teals (300 dpi, JPEG for print)."""
import numpy as np  # noqa
from PIL import Image
from pathlib import Path

OUT = Path(__file__).parent / "assets" / "textures"
DPI = 300
mm = lambda v: int(round(v / 25.4 * DPI))
hexrgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)

def mesh(w, h, base, blobs, grain=11, seed=7):
    """base colour + soft radial colour blobs (x, y in 0..1, radius as fraction of width) + film grain."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    img = np.ones((h, w, 3)) * hexrgb(base)
    for (cx, cy, r, col, strength) in blobs:
        d = np.sqrt((xx - cx * w) ** 2 + (yy - cy * h) ** 2) / (r * w)
        a = np.clip(1 - d, 0, 1) ** 1.3 * strength
        img = img * (1 - a[..., None]) + hexrgb(col) * a[..., None]
    img += rng.normal(0, grain, (h, w, 1))          # monochrome film grain
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

AQUA, TEAL, DEEP, MINT, INK, OPAL = "#5FC7C2", "#1B8F9B", "#0E5961", "#BDF2EA", "#08262B", "#C8C3FF"

# Aura header (full width, 92 mm tall)
mesh(mm(210), mm(92), DEEP, [
    (0.05, 0.0, 0.75, AQUA, 1.0), (0.55, 0.15, 0.32, MINT, 1.0), (0.30, 0.9, 0.45, TEAL, 0.9),
    (0.98, 0.95, 0.6, INK, 1.0), (0.80, 0.25, 0.26, OPAL, 0.8)]).save(OUT / "aura-header.jpg", quality=88, dpi=(DPI, DPI))
# Billboard wordmark fill
mesh(mm(240), mm(70), DEEP, [
    (0.0, 0.3, 0.55, AQUA, 1.0), (0.38, 0.1, 0.25, MINT, 1.0), (0.62, 0.7, 0.3, TEAL, 1.0), (1.0, 1.0, 0.45, INK, 1.0), (0.82, 0.25, 0.2, OPAL, 0.8)],
    seed=3).save(OUT / "word-fill.jpg", quality=88, dpi=(DPI, DPI))
# Full-page grainy teal (collage background)
mesh(mm(210), mm(297), TEAL, [
    (0.1, 0.0, 0.6, AQUA, 0.9), (1.0, 1.0, 0.8, INK, 0.75), (0.9, 0.1, 0.3, MINT, 0.35)],
    grain=13, seed=11).save(OUT / "teal-page.jpg", quality=84, dpi=(DPI, DPI))
# Bento hero tile
mesh(mm(100), mm(60), AQUA, [
    (0.0, 0.0, 0.6, MINT, 0.8), (1.0, 1.0, 0.9, TEAL, 1.0), (0.85, 0.15, 0.3, OPAL, 0.45)],
    seed=5).save(OUT / "bento-tile.jpg", quality=88, dpi=(DPI, DPI))
print("ok")

# Uncoated cream paper with fine tooth (riso / airmail backgrounds), 200 dpi keeps it light
def paper(w_mm, h_mm, base="#F4F1EA", grain=5, dpi=200, seed=21):
    rng = np.random.default_rng(seed)
    w, h = int(w_mm / 25.4 * dpi), int(h_mm / 25.4 * dpi)
    img = np.ones((h, w, 3)) * hexrgb(base) + rng.normal(0, grain, (h, w, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
paper(210, 297).save(OUT / "paper.jpg", quality=80, dpi=(200, 200))
