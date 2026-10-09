"""Builds the creative letterhead set (g–k) into standalone HTML files.

Inlines the outlined wordmark/mark paths and generates the torn-paper edges,
so each HTML file renders on its own. Run: python3 build_creative.py
"""
import random, re
from pathlib import Path

HERE = Path(__file__).parent
LETTER = (HERE / "partials" / "letter.html").read_text()
logo = (HERE / "assets" / "missive-logo.svg").read_text()
paths = re.findall(r'<path fill="([^"]+)"(?: fill-rule="evenodd")? d="([^"]+)"', logo)
MARK_LIGHT, MARK_DARK, WORD = paths[0][1], paths[1][1], paths[2][1]
DOT_CX = re.search(r'cx="([\d.]+)"', logo).group(1)

LEGAL = 'LLPIN: <span class="todo">XXX-XXXX</span>'
ADDR1, ADDR2 = "825, Iconic Shyamal, Shyamal Cross Road,", "132 Feet Ring Road, Ahmedabad, Gujarat 380015"
SERVICES = ["SEO", "Content", "Social", "Email", "White-label"]

def mark_svg(cls="", light="#5FC7C2", dark="#1B8F9B", light_op=1):
    return (f'<svg class="{cls}" viewBox="0 -4 131 122"><path fill="{light}" fill-opacity="{light_op}" d="{MARK_LIGHT}"/>'
            f'<path fill="{dark}" fill-rule="evenodd" d="{MARK_DARK}"/></svg>')

def logo_svg(cls="", word="#0B0C0E", dot="#1B8F9B", light="#5FC7C2", dark="#1B8F9B", light_op=1):
    return (f'<svg class="{cls}" viewBox="0 -4 637 126"><path fill="{light}" fill-opacity="{light_op}" d="{MARK_LIGHT}"/>'
            f'<path fill="{dark}" fill-rule="evenodd" d="{MARK_DARK}"/><path fill="{word}" d="{WORD}"/>'
            f'<circle cx="{DOT_CX}" cy="88" r="12.5" fill="{dot}"/></svg>')

WHITE_LOGO = dict(word="#fff", dot="#fff", light="#fff", dark="#fff", light_op=.55)

def page(name, title, css, sheets):
    body = "\n".join(f'  <section class="page {name[0]}" data-name="{n}">\n{html}\n  </section>' for n, html in sheets)
    (HERE / f"{name}.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="brand.css">
<style>{css}</style></head>
<body>
{body}
</body></html>
""")

# ───────────────────────── G · Billboard (oversized cropped wordmark)
page("g-billboard", "Missive Letterhead G", """
  .g .mark{position:absolute;top:15mm;left:20mm;height:9mm}
  .g .name{position:absolute;top:16.6mm;left:32mm;font-size:6.6pt;letter-spacing:.14em;line-height:1.5;color:var(--ink)}
  .g .name b{font-weight:700}
  .g .contact{position:absolute;top:16.6mm;right:20mm;text-align:right;font-size:6.6pt;line-height:1.5;letter-spacing:.04em}
  .g .contact span{color:var(--teal)}
  .g .letter{top:40mm;left:20mm;right:20mm}
  .g .info{position:absolute;left:20mm;right:20mm;bottom:60mm;display:flex;justify-content:space-between;font-size:6.4pt;letter-spacing:.06em;color:var(--grey);border-top:.3mm solid var(--ink);padding-top:2.4mm}
  .g .giant{position:absolute;left:-7mm;bottom:5mm;width:215mm}
  .g .tag{position:absolute;right:20mm;bottom:47mm;font-size:6.4pt;letter-spacing:.2em;color:var(--teal);font-weight:700}
""", [
 ("first", f"""    {mark_svg("mark")}
    <div class="name mono"><b>MISSIVE DIGITAL MARKETING LLP</b><br>CONTENT / SEO / SOCIAL</div>
    <div class="contact mono">hello@missivedigital.com<br><span>missivedigital.com ↗</span></div>
    {LETTER}
    <div class="info mono"><span>{ADDR1} {ADDR2}</span><span>{LEGAL}</span></div>
    <svg class="giant" viewBox="160 0 476 104"><defs><pattern id="wf" patternUnits="userSpaceOnUse" x="160" y="0" width="476" height="104"><image href="assets/textures/word-fill.jpg" width="476" height="104" preserveAspectRatio="xMidYMid slice"/></pattern></defs>
      <path fill="url(#wf)" d="{WORD}"/><circle cx="{DOT_CX}" cy="88" r="12.5" fill="#1B8F9B"/></svg>"""),
 ("continuation", f"""    {mark_svg("mark")}
    <div class="name mono"><b>MISSIVE DIGITAL MARKETING LLP</b><br>{LEGAL}</div>
    <div class="contact mono">hello@missivedigital.com<br><span>missivedigital.com ↗</span></div>
    <svg class="giant" style="bottom:-24mm" viewBox="160 0 476 100"><defs><pattern id="wf2" patternUnits="userSpaceOnUse" x="160" y="0" width="476" height="100"><image href="assets/textures/word-fill.jpg" width="476" height="100" preserveAspectRatio="xMidYMid slice"/></pattern></defs>
      <path fill="url(#wf2)" d="{WORD}"/><circle cx="{DOT_CX}" cy="88" r="12.5" fill="#1B8F9B"/></svg>"""),
])

# ───────────────────────── H · Neo-brutal (one hard-shadow bar, sticker, ticker) — refined
ticker = " ✦ ".join(["CONTENT", "SEO", "SOCIAL MEDIA", "EMAIL", "WHITE-LABEL"] * 3)
STICKER = (f'<svg class="sticker" viewBox="0 0 100 100"><defs><path id="ring" d="M50 50m-35 0a35 35 0 1 1 70 0a35 35 0 1 1 -70 0"/></defs>'
           f'<circle cx="52" cy="52" r="46" fill="#0B0C0E"/><circle cx="50" cy="50" r="46" fill="#BDF2EA" stroke="#0B0C0E" stroke-width="2.4"/>'
           f'<text font-family="JetBrains Mono" font-weight="700" font-size="8.4" letter-spacing="1.5" fill="#0B0C0E"><textPath href="#ring">CONTENT ✦ SEO ✦ SOCIAL ✦ EMAIL ✦</textPath></text>'
           f'<g transform="translate(35.5 36.5) scale(.22)"><path fill="#5FC7C2" d="{MARK_LIGHT}"/><path fill="#1B8F9B" fill-rule="evenodd" d="{MARK_DARK}"/></g></svg>')
page("h-neo-brutal", "Missive Letterhead H", """
  .h{background:var(--paper)}
  .h .bar{position:absolute;left:15mm;right:15mm;display:grid;border:.6mm solid var(--ink);border-radius:2.4mm;box-shadow:1.3mm 1.3mm 0 var(--ink);background:#fff;overflow:hidden}
  .h .cell{padding:0 5mm;display:flex;flex-direction:column;justify-content:center;min-width:0}
  .h .cell+.cell{border-left:.6mm solid var(--ink)}
  .h .top{top:14mm;height:20mm;grid-template-columns:1.35fr 1fr 1fr}
  .h .top .c1 svg{width:44mm}
  .h .c2{background:var(--aqua)}
  .h .c3{background:var(--teal);color:#fff}
  .h .lbl{font-size:5.2pt;font-weight:700;letter-spacing:.18em;opacity:.75;margin-bottom:1.3mm}
  .h .val{font-size:7.4pt;font-weight:700}
  .h .sticker{position:absolute;top:24mm;right:8mm;width:25mm;transform:rotate(-12deg)}
  .h .letter{top:48mm;left:20mm;right:20mm}
  .h .bot{bottom:14.5mm;height:12mm;grid-template-columns:2.7fr 1.15fr .75fr;font-size:6.2pt;line-height:1.45}
  .h .bot b{font-weight:700}
  .h .ticker{position:absolute;left:0;right:0;bottom:0;height:8.5mm;background:var(--ink);color:var(--aqua);font-size:6.8pt;font-weight:700;letter-spacing:.18em;white-space:nowrap;display:flex;align-items:center;overflow:hidden}
  .h .ticker span{padding-left:15mm}
  .h .cmark{width:9mm}
""", [
 ("first", f"""    <div class="bar top mono">
      <div class="cell c1">{logo_svg()}</div>
      <div class="cell c2"><div class="lbl">SAY HELLO</div><div class="val">hello@missivedigital.com</div></div>
      <div class="cell c3"><div class="lbl">VISIT ↗</div><div class="val">missivedigital.com</div></div>
    </div>
    {STICKER}
    {LETTER}
    <div class="bar bot mono">
      <div class="cell"><div><b>MISSIVE DIGITAL MARKETING LLP</b><br>{ADDR1} {ADDR2}</div></div>
      <div class="cell"><div>{LEGAL}<br>LLP Act, 2008</div></div>
      <div class="cell c2" style="align-items:center"><b>AMD · IN</b></div>
    </div>
    <div class="ticker mono"><span>{ticker}</span></div>"""),
 ("continuation", f"""    <div class="bar top mono" style="height:14mm;grid-template-columns:16mm 1fr;right:auto;width:80mm">
      <div class="cell c2" style="align-items:center;padding:0">{mark_svg("cmark")}</div>
      <div class="cell"><div class="val">MISSIVE DIGITAL MARKETING LLP</div></div>
    </div>
    <div class="bar bot mono" style="height:9mm;grid-template-columns:1fr 1fr"><div class="cell"><div>{LEGAL}</div></div><div class="cell c2">missivedigital.com</div></div>
    <div class="ticker mono"><span>{ticker}</span></div>"""),
])

# ───────────────────────── I · Aura (grain gradient header, wave edge, glass pill)
WAVE = "M0 10 C30 2 55 2 85 9 C115 16 150 18 175 10 C192 5 203 5 210 7 V20 H0Z"
page("i-aura", "Missive Letterhead I", """
  .i .aura{position:absolute;top:0;left:0;width:210mm;height:84mm;object-fit:cover}
  .i .wave{position:absolute;top:66mm;left:0;width:210mm;height:20mm}
  .i .ghost{position:absolute;top:-14mm;right:-20mm;width:92mm;opacity:.16}
  .i .logo{position:absolute;top:18mm;left:20mm;height:13mm}
  .i .line{position:absolute;top:39mm;left:20mm;font-size:21pt;font-weight:800;line-height:1.02;letter-spacing:-.02em;color:#fff}
  .i .line i{font-style:normal;color:var(--mint)}
  .i .pill{position:absolute;top:19.5mm;right:20mm;padding:2.2mm 4.2mm;border-radius:10mm;background:rgba(255,255,255,.16);border:.3mm solid rgba(255,255,255,.55);color:#fff;font-size:6.8pt;letter-spacing:.04em}
  .i .letter{top:90mm;left:20mm;right:20mm}
  .i .foot{position:absolute;left:20mm;right:20mm;bottom:12mm;display:flex;justify-content:space-between;align-items:flex-end;font-size:6.6pt;line-height:1.6;color:var(--grey)}
  .i .foot b{color:var(--ink)}
  .i .strip{position:absolute;left:0;right:0;bottom:0;height:5mm;object-fit:cover;width:210mm}
  .i .aura.sm{height:24mm}
""", [
 ("first", f"""    <img class="aura" src="assets/textures/aura-header.jpg" alt="">
    {mark_svg("ghost", light="#fff", dark="#fff", light_op=.5)}
    {logo_svg("logo", **WHITE_LOGO)}
    <div class="pill mono">hello@missivedigital.com · missivedigital.com</div>
    <div class="line">Content that gets found<i>.</i><br>Stories that get read<i>.</i></div>
    <svg class="wave" viewBox="0 0 210 20" preserveAspectRatio="none"><path fill="#fff" d="{WAVE}"/></svg>
    {LETTER}
    <div class="foot mono"><span><b>Missive Digital Marketing LLP</b><br>{ADDR1}<br>{ADDR2}</span><span style="text-align:right">{LEGAL}<br>Registered under the LLP Act, 2008</span></div>
    <img class="strip" src="assets/textures/aura-header.jpg" alt="">"""),
 ("continuation", f"""    <img class="aura sm" src="assets/textures/aura-header.jpg" alt="">
    <svg class="wave" style="top:14mm;height:12mm" viewBox="0 0 210 20" preserveAspectRatio="none"><path fill="#fff" d="{WAVE}"/></svg>
    {logo_svg("logo", **WHITE_LOGO).replace('class="logo"', 'class="logo" style="top:6mm;height:8mm"')}
    <div class="foot mono"><span><b>Missive Digital Marketing LLP</b> · {LEGAL}</span><span>missivedigital.com</span></div>
    <img class="strip" src="assets/textures/aura-header.jpg" alt="">"""),
])

# ───────────────────────── J · Bento (tile grid header + footer)
pills = "".join(f"<span>{s}</span>" for s in SERVICES)
page("j-bento", "Missive Letterhead J", """
  .j .grid{position:absolute;top:12mm;left:12mm;right:12mm;height:60mm;display:grid;grid-template-columns:1.55fr 1fr 1fr;grid-template-rows:1fr 1fr;gap:3mm}
  .j .t{border-radius:4.5mm;padding:5mm;position:relative;overflow:hidden}
  .j .t1{grid-row:1/3;background:url(assets/textures/bento-tile.jpg) center/cover;display:flex;flex-direction:column;justify-content:space-between}
  .j .t1 svg{width:62mm}
  .j .t1 .k{color:#fff;font-size:6.4pt;letter-spacing:.16em}
  .j .t2{background:var(--night);color:#fff}
  .j .t3{background:var(--mint)}
  .j .t3 .dot{position:absolute;right:-7mm;bottom:-9mm;width:26mm;height:26mm;border-radius:50%;background:var(--teal)}
  .j .t4{grid-column:2/4;background:#fff;border:.3mm solid var(--hair);display:flex;flex-direction:column;justify-content:space-between}
  .j .lbl{font-size:5.6pt;letter-spacing:.18em;color:var(--aqua);margin-bottom:2mm}
  .j .t3 .lbl{color:var(--teal-ink)}
  .j .t4 .lbl{color:var(--teal)}
  .j .val{font-size:8.6pt;font-weight:700}
  .j .pills span{display:inline-block;border:.3mm solid var(--ink);border-radius:5mm;padding:.9mm 2.8mm;margin:0 1.2mm 1.2mm 0;font-size:6.8pt;font-weight:600}
  .j .pills span:nth-child(2){background:var(--aqua);border-color:var(--aqua)}
  .j .pills span:nth-child(4){background:var(--ink);color:#fff}
  .j .web{position:absolute;right:5mm;top:5mm;font-size:7pt;font-weight:700;color:var(--teal)}
  .j .letter{top:82mm;left:20mm;right:20mm}
  .j .fgrid{position:absolute;left:12mm;right:12mm;bottom:12mm;height:17mm;display:grid;grid-template-columns:1.55fr 1fr;gap:3mm}
  .j .fgrid .t{padding:3.4mm 5mm;font-size:6.8pt;line-height:1.5}
  .j .f1{background:var(--mist);color:var(--grey)}
  .j .f1 b{color:var(--ink)}
  .j .f2{background:var(--ink);color:#d6e6e6}
""", [
 ("first", f"""    <div class="grid">
      <div class="t t1"><span class="k mono">CONTENT · SEO · SOCIAL</span>{logo_svg(**WHITE_LOGO)}</div>
      <div class="t t2"><div class="lbl mono">EMAIL</div><div class="val">hello@<br>missivedigital.com</div></div>
      <div class="t t3"><div class="lbl mono">BASED IN</div><div class="val">Ahmedabad,<br>India</div><span class="dot"></span></div>
      <div class="t t4"><div class="lbl mono">WHAT WE DO</div><div class="pills">{pills}</div><span class="web mono">missivedigital.com ↗</span></div>
    </div>
    {LETTER}
    <div class="fgrid mono"><div class="t f1"><b>Missive Digital Marketing LLP</b><br>{ADDR1} {ADDR2}</div><div class="t f2">{LEGAL}<br>Registered under the LLP Act, 2008</div></div>"""),
 ("continuation", f"""    <div class="grid" style="height:20mm;grid-template-rows:1fr"><div class="t t1" style="grid-row:auto;padding:4mm 5mm;justify-content:center">{logo_svg(**WHITE_LOGO).replace('<svg ', '<svg style="width:34mm" ')}</div><div class="t t2" style="padding:4mm"><div class="val" style="font-size:7pt">hello@missivedigital.com</div></div><div class="t t3"><span class="dot" style="width:16mm;height:16mm;right:-4mm;bottom:-6mm"></span></div></div>
    <div class="fgrid mono"><div class="t f1"><b>Missive Digital Marketing LLP</b> · missivedigital.com</div><div class="t f2">{LEGAL}</div></div>"""),
])

# ───────────────────────── K · Collage (torn paper, tape, die-cut sticker) — refined
def torn(y0, y1, seed, step=2.2, amp=1.1):
    """Closed path of a sheet with ragged top edge at y0 and ragged bottom edge at y1 (mm)."""
    rnd = random.Random(seed)
    xs = [i * step for i in range(int(214 / step) + 1)]
    top = [(x, y0 + rnd.uniform(-amp, amp) + 1.0 * ((x // 37) % 2)) for x in xs]
    bot = [(x, y1 + rnd.uniform(-amp, amp) - 0.8 * ((x // 41) % 2)) for x in xs][::-1]
    pts = [(-2, y0)] + top + [(212, y0), (212, y1)] + bot + [(-2, y1)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"

def tape_path(w):
    return f"M0 .6 L2 0 L3.6 .9 L5 0 L{w-4} 0 L{w-2.5} 1 L{w-1} .2 L{w} 9 L{w-1.6} 9.8 L{w-3} 8.9 L{w-5} 9.8 L4 9.8 L2.5 9 L1 9.8 Z"
def tape(x, y, rot, text="", w=36):
    t = f'<text x="{w/2}" y="6.7" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="5" fill="#0E5961">{text}</text>' if text else ""
    return f'<g transform="translate({x} {y}) rotate({rot})"><path d="{tape_path(w)}" fill="#EDEAD8" fill-opacity=".9"/>{t}</g>'

def sheet(y0, y1, seed, extras=""):
    p = torn(y0, y1, seed)
    return (f'<svg class="sheet" viewBox="0 0 210 297"><path d="{p}" fill="#000" fill-opacity=".2" transform="translate(.6 1)"/>'
            f'<path d="{p}" fill="#FFFEFB"/>{extras}</svg>')

DIECUT = (f'<svg class="sticker" viewBox="-14 -18 159 158"><path fill="#fff" stroke="#fff" stroke-width="26" stroke-linejoin="round" d="{MARK_DARK} {MARK_LIGHT}"/>'
          f'<path fill="#5FC7C2" d="{MARK_LIGHT}"/><path fill="#1B8F9B" fill-rule="evenodd" d="{MARK_DARK}"/></svg>')
page("k-collage", "Missive Letterhead K", """
  .k .bg{position:absolute;inset:0;width:210mm;height:297mm;object-fit:cover}
  .k .sheet{position:absolute;inset:0;width:210mm;height:297mm}
  .k .logo{position:absolute;top:13mm;left:18mm;height:10mm}
  .k .contact{position:absolute;top:13.4mm;right:18mm;text-align:right;color:#fff;font-size:6.6pt;line-height:1.55;letter-spacing:.04em}
  .k .sticker{position:absolute;top:27mm;right:17mm;width:17mm;transform:rotate(10deg)}
  .k .letter{top:47mm;left:20mm;right:20mm}
  .k .foot{position:absolute;left:18mm;right:18mm;bottom:7mm;display:flex;justify-content:space-between;align-items:flex-end;color:#fff;font-size:6.2pt;line-height:1.55;letter-spacing:.03em}
  .k .foot b{color:var(--mint)}
""", [
 ("first", f"""    <img class="bg" src="assets/textures/teal-page.jpg" alt="">
    {sheet(35, 275, 4, tape(12, 30, -7) + tape(142, 270, 3, "made with ♥ in Ahmedabad", w=52))}
    {logo_svg("logo", **WHITE_LOGO)}
    <div class="contact mono">hello@missivedigital.com<br>missivedigital.com</div>
    {DIECUT}
    {LETTER}
    <div class="foot mono"><span><b>MISSIVE DIGITAL MARKETING LLP</b><br>{ADDR1} {ADDR2}</span><span style="text-align:right">{LEGAL}<br>LLP Act, 2008</span></div>"""),
 ("continuation", f"""    <img class="bg" src="assets/textures/teal-page.jpg" alt="">
    {sheet(22, 279, 9, tape(160, 17, 6))}
    {logo_svg("logo", **WHITE_LOGO).replace('class="logo"', 'class="logo" style="top:7mm;height:8mm"')}
    <div class="foot mono" style="bottom:7mm"><span><b>MISSIVE DIGITAL MARKETING LLP</b> · {LEGAL}</span><span>missivedigital.com</span></div>"""),
])

# ───────────────────────── L · Airmail (stripe border, perforated stamp, postmark)
def perforated(w, h, r=1.1, step=3.2):
    """Stamp outline with semicircular perforations, drawn clockwise from the top-left corner."""
    def edge(x0, y0, x1, y1):
        n = max(1, round(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5 / step))
        out = []
        for i in range(n):
            t = (i + .5) / n
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            dx, dy = (x1 - x0) / ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5, (y1 - y0) / ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5
            out.append(f"L{cx - dx * r:.2f} {cy - dy * r:.2f} A{r} {r} 0 0 0 {cx + dx * r:.2f} {cy + dy * r:.2f}")
        return " ".join(out) + f" L{x1} {y1}"
    return f"M0 0 {edge(0, 0, w, 0)} {edge(w, 0, w, h)} {edge(w, h, 0, h)} {edge(0, h, 0, 0)} Z"

def stamp(cls, w=28, h=34):
    p = perforated(w, h)
    return (f'<svg class="{cls}" viewBox="-1 -1 {w + 3} {h + 3}"><path d="{p}" fill="#0B0C0E" fill-opacity=".14" transform="translate(.8 .8)"/>'
            f'<path d="{p}" fill="#fff"/><rect x="2.4" y="2.4" width="{w - 4.8}" height="{h - 4.8}" fill="url(#st)"/>'
            f'<defs><pattern id="st" patternUnits="userSpaceOnUse" width="{w}" height="{h}"><image href="assets/textures/bento-tile.jpg" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/></pattern></defs>'
            f'<g transform="translate({w / 2 - 7.5} {h / 2 - 9}) scale(.115)"><path fill="#fff" fill-opacity=".6" d="{MARK_LIGHT}"/><path fill="#fff" fill-rule="evenodd" d="{MARK_DARK}"/></g>'
            f'<text x="4.4" y="7.6" font-family="JetBrains Mono" font-weight="700" font-size="2.6" letter-spacing=".3" fill="#fff">INDIA</text>'
            f'</svg>')

WAVES = " ".join(f'<path d="M0 {y} q4 -2.2 8 0 t8 0 t8 0 t8 0 t8 0 t8 0" />' for y in (0, 4, 8, 12))
POSTMARK = (f'<svg class="postmark" viewBox="-60 -20 104 40"><g fill="none" stroke="#0E5961" stroke-width=".7" opacity=".85">'
            f'<g transform="translate(-58 -6)">{WAVES}</g><circle r="16"/><circle r="11.2"/></g>'
            f'<defs><path id="pm" d="M0 0m-13.4 0a13.4 13.4 0 1 1 26.8 0a13.4 13.4 0 1 1 -26.8 0"/></defs>'
            f'<text font-family="JetBrains Mono" font-weight="700" font-size="2.7" letter-spacing=".55" fill="#0E5961" opacity=".85"><textPath href="#pm">AHMEDABAD ✦ GUJARAT ✦ 380015 ✦</textPath></text>'
            f'<text y="-.6" text-anchor="middle" font-family="Figtree" font-weight="800" font-size="5" fill="#0E5961" opacity=".85">missive.</text>'
            f'<text y="4.4" text-anchor="middle" font-family="JetBrains Mono" font-weight="700" font-size="2.3" letter-spacing=".4" fill="#0E5961" opacity=".85">PRIORITY</text></svg>')

page("l-airmail", "Missive Letterhead L", """
  .l{background:#fff}
  .l .border{position:absolute;inset:0;background:repeating-linear-gradient(-45deg,var(--teal) 0 6mm,#fff 6mm 9mm,var(--aqua) 9mm 15mm,#fff 15mm 18mm)}
  .l .inner{position:absolute;inset:4.5mm;background:url(assets/textures/paper.jpg) center/cover}
  .l .logo{position:absolute;top:16mm;left:17mm;height:10.5mm}
  .l .via{position:absolute;top:30.5mm;left:17mm;display:flex;gap:0;font-size:5.8pt;font-weight:700;letter-spacing:.16em}
  .l .via span{border:.35mm solid var(--teal-ink);padding:.9mm 2.2mm;color:var(--teal-ink)}
  .l .via span+span{border-left:0;background:var(--teal-ink);color:#fff}
  .l .stamp{position:absolute;top:13mm;right:15mm;width:30mm;transform:rotate(3deg)}
  .l .postmark{position:absolute;top:27mm;right:27mm;width:56mm;transform:rotate(-9deg)}
  .l .letter{top:50mm;left:19mm;right:19mm}
  .l .foot{position:absolute;left:17mm;right:17mm;bottom:13mm;display:grid;grid-template-columns:auto 1fr auto;gap:5mm;align-items:start;font-size:6.2pt;line-height:1.55;color:var(--grey);border-top:.35mm dashed var(--teal);padding-top:3mm}
  .l .foot .from{font-size:5.6pt;font-weight:700;letter-spacing:.18em;color:#fff;background:var(--teal);padding:.8mm 2mm}
  .l .foot b{color:var(--ink)}
  .l .stamp.sm{width:17mm;top:11mm;right:12mm}
""", [
 ("first", f"""    <div class="border"></div><div class="inner"></div>
    {logo_svg("logo")}
    <div class="via mono"><span>BY MISSIVE</span><span>PRIORITY POST</span></div>
    {stamp("stamp")}
    {POSTMARK}
    {LETTER}
    <div class="foot mono"><span class="from">FROM</span><span><b>Missive Digital Marketing LLP</b><br>{ADDR1} {ADDR2}</span><span style="text-align:right">hello@missivedigital.com<br>{LEGAL}</span></div>"""),
 ("continuation", f"""    <div class="border"></div><div class="inner"></div>
    {logo_svg("logo").replace('class="logo"', 'class="logo" style="height:8mm"')}
    {stamp("stamp sm")}
    <div class="foot mono"><span class="from">FROM</span><span><b>Missive Digital Marketing LLP</b> · {LEGAL}</span><span>missivedigital.com</span></div>"""),
])

# ───────────────────────── M · Riso (two-colour overprint, halftone full stop)
def halftone(cx, cy, R, step=.95, light=(-.55, -.6, .58)):
    """Halftone sphere: dot size follows shading, so the full stop reads as a lit ball."""
    import math
    ln = math.sqrt(sum(v * v for v in light)); L = [v / ln for v in light]
    teal, aqua = [], []
    n = int(R / step) + 1
    for j in range(-n, n + 1):
        for i in range(-n, n + 1):
            x, y = i * step + (step / 2 if j % 2 else 0), j * step * .87
            d2 = (x * x + y * y) / (R * R)
            if d2 > 1: continue
            z = math.sqrt(1 - d2)
            lum = max(0, (x / R) * L[0] + (y / R) * L[1] + z * L[2])
            r_t = step * .52 * min(1, max(0, 1.05 - lum) ** .9) * (1 - d2) ** .25
            if r_t > .08: teal.append(f'<circle cx="{cx + x:.2f}" cy="{cy + y:.2f}" r="{r_t:.2f}"/>')
            aqua.append(f'<circle cx="{cx + x + .55:.2f}" cy="{cy + y + .35:.2f}" r="{step * .52 * math.sqrt(1 - d2) ** .6:.2f}"/>')
    return f'<g class="ink-a" fill="#5FC7C2">{"".join(aqua)}</g><g class="ink-t" fill="#1B8F9B">{"".join(teal)}</g>'

REG = '<svg class="reg {pos}" viewBox="-5 -5 10 10"><circle r="2.6" fill="none" stroke="#1B8F9B" stroke-width=".35"/><path d="M-4.6 0H4.6M0 -4.6V4.6" stroke="#1B8F9B" stroke-width=".35"/></svg>'
S = .27   # wordmark scale, mm per logo unit
WX, WBASE = 15, 40   # wordmark left edge and baseline (mm)
word_t = f'translate({WX - 162.5 * S:.2f} {WBASE - 97 * S:.2f}) scale({S})'
word_a = f'translate({WX - 162.5 * S + .7:.2f} {WBASE - 97 * S + .45:.2f}) scale({S})'
DOT_R = 15
dot_cx = WX + (596.6 - 162.5) * S + 6 + DOT_R
page("m-riso", "Missive Letterhead M", f"""
  .m{{background:url(assets/textures/paper.jpg) center/cover}}
  .m .head{{position:absolute;inset:0;width:210mm;height:297mm}}
  .m .ink-a,.m .ink-t{{mix-blend-mode:multiply}}
  .m .info{{position:absolute;top:46mm;left:15mm;right:15mm;display:flex;justify-content:space-between;font-size:6.4pt;letter-spacing:.08em;color:var(--teal-ink);border-top:.35mm solid var(--teal);padding-top:2.2mm}}
  .m .info b{{color:var(--ink);font-weight:700}}
  .m .letter{{top:60mm;left:20mm;right:20mm}}
  .m .foot{{position:absolute;left:15mm;right:15mm;bottom:13mm;display:flex;justify-content:space-between;align-items:flex-end;font-size:6.2pt;line-height:1.55;color:var(--grey);border-top:.35mm solid var(--teal);padding-top:2.6mm}}
  .m .foot b{{color:var(--ink)}}
  .m .swatch{{display:flex;align-items:center;gap:1.6mm;font-size:5.6pt;letter-spacing:.14em;color:var(--teal-ink)}}
  .m .swatch i{{width:3.2mm;height:3.2mm;display:inline-block;mix-blend-mode:multiply}}
  .m .swatch i:nth-child(1){{background:var(--aqua)}} .m .swatch i:nth-child(2){{background:var(--teal);margin-left:-1.6mm}}
  .m .reg{{position:absolute;width:5mm;height:5mm}}
  .m .reg.tl{{top:5mm;left:5mm}} .m .reg.tr{{top:5mm;right:5mm}} .m .reg.bl{{bottom:5mm;left:5mm}} .m .reg.br{{bottom:5mm;right:5mm}}
""", [
 ("first", f"""    <svg class="head" viewBox="0 0 210 297">
      <path class="ink-a" fill="#5FC7C2" transform="{word_a}" d="{WORD}"/>
      <path class="ink-t" fill="#1B8F9B" fill-opacity=".9" transform="{word_t}" d="{WORD}"/>
      {halftone(dot_cx, WBASE - DOT_R, DOT_R)}
    </svg>
    <div class="info mono"><span><b>MISSIVE DIGITAL MARKETING LLP</b></span><span>hello@missivedigital.com</span><span>missivedigital.com ↗</span></div>
    {LETTER}
    <div class="foot mono"><span><b>{ADDR1}</b><br>{ADDR2} · {LEGAL}</span><span class="swatch"><i></i><i></i>&nbsp;PRINTED IN AQUA + TEAL</span></div>
    {"".join(REG.format(pos=p) for p in ("tl", "tr", "bl", "br"))}"""),
 ("continuation", f"""    <svg class="head" viewBox="0 0 210 297">{halftone(24, 22, 8)}</svg>
    <div class="info mono" style="top:16mm;left:36mm"><span><b>MISSIVE DIGITAL MARKETING LLP</b></span><span>missivedigital.com ↗</span></div>
    <div class="foot mono"><span>{LEGAL}</span><span class="swatch"><i></i><i></i>&nbsp;PRINTED IN AQUA + TEAL</span></div>
    {"".join(REG.format(pos=p) for p in ("tl", "tr", "bl", "br"))}"""),
])

print("built g–m")
