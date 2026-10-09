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

# ───────────────────────── H · Neo-brutal (boxes, hard shadows, sticker, ticker)
ticker = " ✦ ".join(["CONTENT", "SEO", "SOCIAL MEDIA", "EMAIL", "WHITE-LABEL"] * 3)
page("h-neo-brutal", "Missive Letterhead H", """
  .h{background:var(--paper)}
  .h .box{position:absolute;border:.7mm solid var(--ink);border-radius:2.6mm;box-shadow:1.6mm 1.6mm 0 var(--ink)}
  .h .b1{top:13mm;left:14mm;width:84mm;height:25mm;background:#fff;display:flex;align-items:center;padding-left:6mm}
  .h .b1 svg{width:70mm;height:auto}
  .h .b2{top:13mm;left:103mm;width:44mm;height:25mm;background:var(--aqua);padding:4mm}
  .h .b3{top:13mm;left:152mm;width:44mm;height:25mm;background:var(--teal);color:#fff;padding:4mm}
  .h .lbl{font-size:5.6pt;font-weight:700;letter-spacing:.18em;opacity:.8;margin-bottom:2.2mm}
  .h .val{font-size:7.4pt;font-weight:700;line-height:1.35;word-break:break-all}
  .h .sticker{position:absolute;top:33mm;right:12mm;width:31mm;height:31mm;transform:rotate(-14deg)}
  .h .note{position:absolute;top:47mm;right:46mm;font-size:15pt;color:var(--teal);transform:rotate(-4deg);font-weight:700}
  .h .letter{top:52mm;left:20mm;right:20mm}
  .h .foot{position:absolute;left:14mm;right:14mm;bottom:19mm;background:#fff;padding:3mm 5mm;font-size:6.8pt;line-height:1.5;display:flex;justify-content:space-between;gap:6mm}
  .h .foot b{font-weight:700}
  .h .ticker{position:absolute;left:0;right:0;bottom:0;height:11mm;background:var(--ink);color:var(--aqua);font-size:7.6pt;font-weight:700;letter-spacing:.16em;white-space:nowrap;display:flex;align-items:center;overflow:hidden}
  .h .ticker span{padding-left:6mm}
  .h .mark-sm{position:absolute;top:14mm;left:14mm;height:9mm}
""", [
 ("first", f"""    <div class="box b1">{logo_svg()}</div>
    <div class="box b2 mono"><div class="lbl">SAY HELLO</div><div class="val">hello@missive<br>digital.com</div></div>
    <div class="box b3 mono"><div class="lbl">VISIT US ↗</div><div class="val">missive<br>digital.com</div></div>
    <svg class="sticker" viewBox="0 0 100 100"><defs><path id="ring" d="M50 50m-36 0a36 36 0 1 1 72 0a36 36 0 1 1 -72 0"/></defs>
      <circle cx="51.5" cy="51.5" r="47" fill="#0B0C0E"/><circle cx="50" cy="50" r="47" fill="#BDF2EA" stroke="#0B0C0E" stroke-width="2"/>
      <text font-family="JetBrains Mono" font-weight="700" font-size="8.6" letter-spacing="1.6" fill="#0B0C0E"><textPath href="#ring">CONTENT ✦ SEO ✦ SOCIAL ✦ EMAIL ✦</textPath></text>
      <g transform="translate(35 36) scale(.23)"><path fill="#5FC7C2" d="{MARK_LIGHT}"/><path fill="#1B8F9B" fill-rule="evenodd" d="{MARK_DARK}"/></g></svg>
    <div class="note hand">psst… this one’s for you ↙</div>
    {LETTER}
    <div class="box foot mono"><span><b>MISSIVE DIGITAL MARKETING LLP</b><br>{ADDR1} {ADDR2}</span><span style="text-align:right">{LEGAL}<br>LLP Act, 2008</span></div>
    <div class="ticker mono"><span>{ticker}</span></div>"""),
 ("continuation", f"""    <div class="box" style="top:13mm;left:14mm;width:20mm;height:20mm;background:#fff;display:grid;place-items:center">{mark_svg("cmark")}</div>
    <div class="box foot mono"><span><b>MISSIVE DIGITAL MARKETING LLP</b> · {LEGAL}</span><span>missivedigital.com</span></div>
    <div class="ticker mono"><span>{ticker}</span></div>
    <style>.h .cmark{{width:12mm}}</style>"""),
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

# ───────────────────────── K · Collage (torn paper, tape, die-cut sticker)
def torn(y0, y1, seed, step=2.4, amp=1.3):
    """Closed path of a sheet with ragged top edge at y0 and ragged bottom edge at y1 (mm)."""
    rnd = random.Random(seed)
    top = [(x, y0 + rnd.uniform(-amp, amp) + 1.2 * ((x // 37) % 2)) for x in [i * step for i in range(int(214 / step) + 1)]]
    bot = [(x, y1 + rnd.uniform(-amp, amp) - 1.0 * ((x // 41) % 2)) for x in [i * step for i in range(int(214 / step) + 1)]][::-1]
    pts = [(-2, y0)] + top + [(212, y0), (212, y1)] + bot + [(-2, y1)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"

def tape_path(w):
    return f"M0 .6 L2 0 L3.6 .9 L5 0 L{w-4} 0 L{w-2.5} 1 L{w-1} .2 L{w} 9 L{w-1.6} 9.8 L{w-3} 8.9 L{w-5} 9.8 L4 9.8 L2.5 9 L1 9.8 Z"
def tape(x, y, rot, text="", w=36):
    t = f'<text x="{w/2}" y="6.7" text-anchor="middle" font-family="Caveat" font-weight="700" font-size="5" fill="#0E5961">{text}</text>' if text else ""
    return f'<g transform="translate({x} {y}) rotate({rot})"><path d="{tape_path(w)}" fill="#EDEAD8" fill-opacity=".88"/>{t}</g>'

def sheet(y0, y1, seed, extras=""):
    p = torn(y0, y1, seed)
    return (f'<svg class="sheet" viewBox="0 0 210 297"><path d="{p}" fill="#000" fill-opacity=".22" transform="translate(.7 1.1)"/>'
            f'<path d="{p}" fill="#FFFEFB"/>{extras}</svg>')

page("k-collage", "Missive Letterhead K", """
  .k .bg{position:absolute;inset:0;width:210mm;height:297mm;object-fit:cover}
  .k .sheet{position:absolute;inset:0;width:210mm;height:297mm}
  .k .logo{position:absolute;top:14mm;left:18mm;height:12mm}
  .k .contact{position:absolute;top:15mm;right:18mm;text-align:right;color:#fff;font-size:6.8pt;line-height:1.6;letter-spacing:.04em}
  .k .sticker{position:absolute;top:36mm;right:24mm;width:21mm;transform:rotate(12deg)}
  .k .letter{top:60mm;left:22mm;right:22mm}
  .k .foot{position:absolute;left:18mm;right:18mm;bottom:9mm;display:flex;justify-content:space-between;align-items:flex-end;color:#fff;font-size:6.4pt;line-height:1.6;letter-spacing:.03em}
  .k .foot b{color:var(--mint)}
""", [
 ("first", f"""    <img class="bg" src="assets/textures/teal-page.jpg" alt="">
    {sheet(44, 268, 4, tape(10, 38, -9) + tape(138, 262, 4, "made with ♥ in Ahmedabad", w=54))}
    {logo_svg("logo", **WHITE_LOGO)}
    <div class="contact mono">hello@missivedigital.com<br>missivedigital.com</div>
    <svg class="sticker" viewBox="-14 -18 159 158"><path fill="#fff" stroke="#fff" stroke-width="26" stroke-linejoin="round" d="{MARK_DARK} {MARK_LIGHT}"/><path fill="#5FC7C2" d="{MARK_LIGHT}"/><path fill="#1B8F9B" fill-rule="evenodd" d="{MARK_DARK}"/></svg>
    {LETTER}
    <div class="foot mono"><span><b>MISSIVE DIGITAL MARKETING LLP</b><br>{ADDR1} {ADDR2}</span><span style="text-align:right">{LEGAL}<br>Registered under the LLP Act, 2008</span></div>"""),
 ("continuation", f"""    <img class="bg" src="assets/textures/teal-page.jpg" alt="">
    {sheet(22, 274, 9, tape(160, 17, 6))}
    {logo_svg("logo", **WHITE_LOGO).replace('class="logo"', 'class="logo" style="top:7mm;height:8mm"')}
    <div class="foot mono" style="bottom:7mm"><span><b>MISSIVE DIGITAL MARKETING LLP</b> · {LEGAL}</span><span>missivedigital.com</span></div>"""),
])
print("built g–k")
