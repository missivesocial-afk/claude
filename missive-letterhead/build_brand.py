"""Brand-system letterheads (V–X) built strictly on the Missive motion style tokens.

Run: python3 build_brand.py  then  node render.cjs v-chip w-band x-paper-tape
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
LETTER = (HERE / "partials" / "letter.html").read_text()
logo = (HERE / "assets" / "missive-logo.svg").read_text()
paths = re.findall(r'<path fill="([^"]+)"(?: fill-rule="evenodd")? d="([^"]+)"', logo)
MARK_LIGHT, MARK_DARK, WORD = paths[0][1], paths[1][1], paths[2][1]
DOT_CX = re.search(r'cx="([\d.]+)"', logo).group(1)

TEAL, DEEP, INK = "#5DC5C1", "#19929E", "#0B1314"
LLPIN = '<span class="todo">XXX-XXXX</span>'
ADDR = "825, Iconic Shyamal, Shyamal Cross Road,<br>132 Feet Ring Road, Ahmedabad,<br>Gujarat 380015, India"

def logo_svg(cls="logo", word=INK, dot=DEEP):
    return (f'<svg class="{cls}" viewBox="0 -4 637 126"><path fill="{TEAL}" d="{MARK_LIGHT}"/>'
            f'<path fill="{DEEP}" fill-rule="evenodd" d="{MARK_DARK}"/><path fill="{word}" d="{WORD}"/>'
            f'<circle cx="{DOT_CX}" cy="88" r="12.5" fill="{dot}"/></svg>')

def mark_svg(cls="mark"):
    return (f'<svg class="{cls}" viewBox="0 -4 131 122"><path fill="{TEAL}" d="{MARK_LIGHT}"/>'
            f'<path fill="{DEEP}" fill-rule="evenodd" d="{MARK_DARK}"/></svg>')

def legal_grid(cls="legal"):
    return f"""<div class="{cls}">
      <div><span class="lbl">Registered office</span><div class="val">{ADDR}</div></div>
      <div><span class="lbl">Entity</span><div class="val">Missive Digital Marketing LLP<br>LLPIN {LLPIN}<br>Registered under the LLP Act, 2008</div></div>
      <div><span class="lbl">Contact</span><div class="val">hello@missivedigital.com<br>missivedigital.com</div></div>
    </div>"""

def page(name, title, css, sheets):
    body = "\n".join(f'  <section class="page {name[0]}" data-name="{n}">\n{html}\n  </section>' for n, html in sheets)
    (HERE / f"{name}.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="missive-brand.css">
<style>{css}</style></head>
<body>
{body}
</body></html>
""")

GRID = """
  .{p} .legal{{position:absolute;left:18mm;right:18mm;bottom:13mm;display:grid;grid-template-columns:1.15fr 1.15fr 1fr;gap:6mm;border-top:.2mm solid var(--ink);padding-top:3.6mm}}
  .{p} .legal .val{{font-size:6.6pt}}
"""

# ───────────────────────── V · Chip (Swiss grid; one key word in a deep-teal chip)
page("v-chip", "Missive Letterhead V", GRID.format(p="v") + """
  .v .logo{position:absolute;top:16mm;left:18mm;height:9mm}
  .v .head{position:absolute;top:15.4mm;left:96mm;right:18mm;display:grid;grid-template-columns:1fr 1.35fr 1fr;gap:5mm}
  .v .rule{position:absolute;top:32mm;left:18mm;right:18mm;height:.2mm;background:var(--ink)}
  .v .letter{top:44mm;left:18mm;right:18mm}
  .v .line{position:absolute;left:17.4mm;right:18mm;bottom:38mm;font-size:30pt;font-weight:700;line-height:1;letter-spacing:-.045em;text-transform:uppercase}
  .v .line .chip{border-radius:.12em;padding:0 .12em;margin-left:.04em}
  .v .mark{position:absolute;top:17mm;left:18mm;height:7mm}
""", [
 ("first", f"""    {logo_svg()}
    <div class="head">
      <div><span class="lbl">Studio</span><div class="val">Ahmedabad, India</div></div>
      <div><span class="lbl">Write</span><div class="val">hello@missivedigital.com</div></div>
      <div><span class="lbl">Visit</span><div class="val">missivedigital.com</div></div>
    </div>
    <div class="rule"></div>
    {LETTER}
    <div class="line">Content that<br>gets you <span class="chip">found</span></div>
    {legal_grid()}"""),
 ("continuation", f"""    {mark_svg()}
    <div class="rule" style="top:28mm"></div>
    {legal_grid()}"""),
])

# ───────────────────────── W · Band (ink band with the system's tracked caps, deep-teal pill)
page("w-band", "Missive Letterhead W", GRID.format(p="w") + """
  .w .band{position:absolute;top:0;left:0;right:0;height:25mm;background:var(--ink);display:flex;align-items:center;justify-content:space-between;padding:0 18mm}
  .w .band .logo{height:8.5mm}
  .w .band .caps{display:flex;gap:7mm;font-size:6pt;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#fff}
  .w .band .caps span+span{color:var(--mist)}
  .w .surface{position:absolute;top:25mm;left:0;right:0;height:1.4mm;background:var(--teal)}
  .w .letter{top:42mm;left:18mm;right:18mm}
  .w .legal{grid-template-columns:1.15fr 1.15fr 1fr}
  .w .pill{position:absolute;right:18mm;bottom:63mm;font-size:7.4pt}
  .w .behind{position:absolute;left:12mm;bottom:-10mm;font-size:118pt;font-weight:700;letter-spacing:-.045em;line-height:.86;text-transform:uppercase;color:var(--mist);white-space:nowrap}
  .w .legal{bottom:37mm}
  .w .legal.cont{bottom:13mm}
""", [
 ("first", f"""    <div class="band">{logo_svg(word="#FFFFFF", dot=TEAL)}<div class="caps"><span>hello@missivedigital.com</span><span>Ahmedabad · India</span></div></div>
    <div class="surface"></div>
    {LETTER}
    <div class="behind">Missive</div>
    <span class="pill">missivedigital.com</span>
    {legal_grid()}"""),
 ("continuation", f"""    <div class="band" style="height:14mm">{logo_svg(word="#FFFFFF", dot=TEAL).replace('class="logo"', 'class="logo" style="height:6mm"')}<div class="caps"><span>missivedigital.com</span></div></div>
    <div class="surface" style="top:14mm"></div>
    {legal_grid("legal cont")}"""),
])

# ───────────────────────── X · Paper & tape (dot-grain paper, one mist tape strip, deep-teal word)
page("x-paper-tape", "Missive Letterhead X", GRID.format(p="x") + """
  .x{background:var(--paper) radial-gradient(rgba(11,19,20,.07) .32mm,transparent .4mm) 0 0/5.2mm 5.2mm}
  .x .logo{position:absolute;top:17mm;left:18mm;height:9.5mm}
  .x .tape{position:absolute;top:16mm;right:14mm;height:11.5mm;padding:0 7mm;background:var(--mist);display:flex;align-items:center;gap:5mm;
           transform:rotate(-2deg);box-shadow:0 1mm 4mm rgba(11,19,20,.08);font-size:7.4pt;white-space:nowrap}
  .x .tape b{font-weight:700;color:var(--deep)}
  .x .letter{top:46mm;left:18mm;right:18mm}
  .x .legal{border-top-color:rgba(11,19,20,.35)}
  .x .mark{position:absolute;top:17mm;left:18mm;height:7mm}
  .x .stripes{position:absolute;right:0;bottom:41mm;width:58mm;height:16mm;background:repeating-linear-gradient(180deg,var(--teal) 0 1.5mm,transparent 1.5mm 4.4mm)}
""", [
 ("first", f"""    {logo_svg()}
    <div class="tape"><span>hello@missivedigital.com</span><b>missivedigital.com</b></div>
    <div class="stripes"></div>
    {LETTER}
    {legal_grid()}"""),
 ("continuation", f"""    {mark_svg()}
    <div class="tape" style="top:15mm;height:9mm;font-size:6.8pt"><b>missivedigital.com</b></div>
    {legal_grid()}"""),
])

def mark_white(cls="mark"):
    return (f'<svg class="{cls}" viewBox="0 -4 131 122"><path fill="#fff" fill-opacity=".55" d="{MARK_LIGHT}"/>'
            f'<path fill="#fff" fill-rule="evenodd" d="{MARK_DARK}"/></svg>')

# ───────────────────────── Y · Word grid (services interleaved with gradient tiles)
tile = '<i class="tl"></i>'
tile_mark = f'<i class="tl">{mark_white("tm")}</i>'
page("y-word-grid", "Missive Letterhead Y", GRID.format(p="y") + """
  .y .logo{position:absolute;top:16mm;left:18mm;height:9mm}
  .y .head{position:absolute;top:15.4mm;right:18mm;display:grid;grid-template-columns:auto auto;gap:9mm}
  .y .words{position:absolute;top:33mm;left:18mm;right:18mm;display:flex;justify-content:space-between;align-items:center;
            font-size:15pt;font-weight:700;letter-spacing:-.045em;text-transform:uppercase;line-height:1;border-top:.2mm solid var(--ink);border-bottom:.2mm solid var(--ink);padding:3mm 0}
  .y .tl{display:inline-grid;place-items:center;width:13mm;height:8.5mm;border-radius:.8mm;background:linear-gradient(140deg,var(--deep),var(--teal))}
  .y .tm{width:5.4mm}
  .y .letter{top:56mm;left:18mm;right:18mm}
  .y .mark{position:absolute;top:17mm;left:18mm;height:7mm}
""", [
 ("first", f"""    {logo_svg()}
    <div class="head"><div><span class="lbl">Write</span><div class="val">hello@missivedigital.com</div></div><div><span class="lbl">Visit</span><div class="val">missivedigital.com</div></div></div>
    <div class="words"><span>Content</span>{tile}<span>SEO</span>{tile_mark}<span>Social</span>{tile}<span>Email</span></div>
    {LETTER}
    {legal_grid()}"""),
 ("continuation", f"""    {mark_svg()}
    <div class="words" style="top:28mm;font-size:9pt;padding:2mm 0"><span>Content</span><span>SEO</span><span>Social</span><span>Email</span></div>
    {legal_grid()}"""),
])

# ───────────────────────── Z · Nodes (the logo wired to its contact tiles)
page("z-nodes", "Missive Letterhead Z", GRID.format(p="z") + """
  .z .logo{position:absolute;top:21mm;left:18mm;height:9.5mm}
  .z .wires{position:absolute;inset:0;width:210mm;height:297mm}
  .z .wires path{fill:none;stroke:var(--ink);stroke-width:.25}
  .z .node{position:absolute;left:112mm;height:7.4mm;display:flex;align-items:center;gap:2.6mm;padding:0 3.4mm;border-radius:1.6mm;
           background:var(--mist);border:.3mm solid rgba(11,19,20,.14);font-size:7.2pt;white-space:nowrap}
  .z .node .lbl{margin:0}
  .z .node.main{background:var(--teal);font-weight:700}
  .z .letter{top:52mm;left:18mm;right:18mm}
  .z .mark{position:absolute;top:17mm;left:18mm;height:7mm}
""", [
 ("first", f"""    {logo_svg()}
    <svg class="wires" viewBox="0 0 210 297">
      <path d="M66.4 27.9 H90 M90 18.8 V37 M90 18.8 H112 M90 27.9 H112 M90 37 H112"/>
      <circle cx="90" cy="27.9" r=".7" fill="#0B1314"/>
    </svg>
    <div class="node" style="top:15.1mm"><span class="lbl">Write</span>hello@missivedigital.com</div>
    <div class="node main" style="top:24.2mm"><span class="lbl" style="color:var(--ink)">Visit</span>missivedigital.com</div>
    <div class="node" style="top:33.3mm"><span class="lbl">Studio</span>Ahmedabad, India</div>
    {LETTER}
    {legal_grid()}"""),
 ("continuation", f"""    {mark_svg()}
    <svg class="wires" viewBox="0 0 210 297"><path d="M28 20.5 H112"/><circle cx="28" cy="20.5" r=".9" fill="#19929E"/></svg>
    <div class="node main" style="top:16.8mm">missivedigital.com</div>
    {legal_grid()}"""),
])

# ───────────────────────── AA · Window (a rounded deep-teal window reveals the mark)
page("aa-window", "Missive Letterhead AA", GRID.format(p="a") + """
  .a .logo{position:absolute;top:16mm;left:18mm;height:9.5mm}
  .a .info{position:absolute;top:32mm;left:18mm;display:grid;grid-template-columns:auto auto;gap:9mm}
  .a .win{position:absolute;top:14mm;right:18mm;width:64mm;height:32mm;border-radius:4mm;overflow:hidden;background:linear-gradient(140deg,var(--deep),var(--teal))}
  .a .win .big{position:absolute;right:6mm;bottom:5mm;width:24mm}
  .a .win .cap{position:absolute;left:5mm;top:4.6mm;color:#fff;font-size:5.6pt;font-weight:700;letter-spacing:.14em;text-transform:uppercase;line-height:1.7}
  .a .letter{top:56mm;left:18mm;right:18mm}
  .a .mark{position:absolute;top:17mm;left:18mm;height:7mm}
""", [
 ("first", f"""    {logo_svg()}
    <div class="info"><div><span class="lbl">Write</span><div class="val">hello@missivedigital.com</div></div><div><span class="lbl">Visit</span><div class="val">missivedigital.com</div></div></div>
    <div class="win"><div class="cap">Content<br>SEO<br>Social</div>{mark_white("big")}</div>
    {LETTER}
    {legal_grid()}"""),
 ("continuation", f"""    {mark_svg()}
    <div class="win" style="height:14mm;width:30mm">{mark_white("big").replace('class="big"', 'class="big" style="width:11mm;right:3mm;bottom:2.6mm"')}</div>
    {legal_grid()}"""),
])

# ───────────────────────── AB · Frame (the letter sits as a white sheet framed on paper)
page("ab-frame", "Missive Letterhead AB", """
  .a{background:var(--paper)}
  .a .sheet{position:absolute;top:11mm;left:8mm;right:8mm;bottom:11mm;background:#fff;border-radius:3mm;box-shadow:0 .6mm 2.4mm rgba(11,19,20,.06)}
  .a .rim{position:absolute;left:11mm;right:11mm;display:flex;justify-content:space-between;font-size:5.4pt;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2);line-height:1}
  .a .rim.t{top:4.6mm} .a .rim.b{bottom:4.6mm}
  .a .rim b{color:var(--deep);font-weight:700}
  .a .logo{position:absolute;top:22mm;left:20mm;height:9.5mm}
  .a .head{position:absolute;top:21.6mm;right:20mm;display:grid;grid-template-columns:auto auto;gap:9mm}
  .a .letter{top:48mm;left:20mm;right:20mm}
  .a .mark{position:absolute;top:20mm;left:20mm;height:7mm}
""", [
 ("first", f"""    <div class="sheet"></div>
    <div class="rim t"><span>Missive Digital Marketing LLP</span><b>missivedigital.com</b></div>
    {logo_svg()}
    <div class="head"><div><span class="lbl">Write</span><div class="val">hello@missivedigital.com</div></div><div><span class="lbl">Studio</span><div class="val">Ahmedabad, India</div></div></div>
    {LETTER}
    <div class="rim b"><span>825, Iconic Shyamal, Shyamal Cross Road, 132 Feet Ring Road, Ahmedabad, Gujarat 380015</span><span>LLPIN {LLPIN} · LLP Act, 2008</span></div>"""),
 ("continuation", f"""    <div class="sheet"></div>
    <div class="rim t"><span>Missive Digital Marketing LLP</span><b>missivedigital.com</b></div>
    {mark_svg()}
    <div class="rim b"><span>Ahmedabad, India</span><span>LLPIN {LLPIN}</span></div>"""),
])
print("built v–ab")
