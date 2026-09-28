// Injected into page.html after window.ready. Exposes AE.setup(), AE.sample(t), AE.hideForPlate().
window.AE = (function () {
  const st = document.getElementById('stage');
  const SR = st.getBoundingClientRect();
  const units = [];   // text units: {name, el, clip?}
  const shapes = [];  // {name, el, kind:'rect'|'ellipse', fill|stroke}
  const clips = [];   // {name, el, words:[unitIdx]}
  const ratio = {};   // font key -> {base, h}  (baseline & content-height as fraction of font-size)

  function fontKey(el) {
    const cs = getComputedStyle(el), fam = cs.fontFamily.replace(/["']/g, '').split(',')[0].trim();
    const w = parseInt(cs.fontWeight, 10);
    if (fam === 'Anton') return 'Anton-Regular';
    if (fam === 'Mono') return w >= 600 ? 'JetBrainsMono-Bold' : 'JetBrainsMono-Medium';
    return w >= 800 ? 'Inter-ExtraBold' : w >= 600 ? 'Inter-Bold' : 'Inter-Medium';
  }
  function cssFam(k) { return k.indexOf('Anton') === 0 ? 'Anton' : k.indexOf('JetBrains') === 0 ? 'Mono' : 'Inter'; }
  function calibrate(k) {
    if (ratio[k]) return ratio[k];
    const d = document.createElement('div');
    d.style.cssText = `position:absolute;left:0;top:0;font-family:${cssFam(k)};font-size:200px;line-height:1;white-space:nowrap;font-weight:${/Bold|ExtraBold/.test(k) ? (k.indexOf('Extra') > 0 ? 800 : 700) : (k.indexOf('Medium') > 0 ? 500 : 400)}`;
    d.innerHTML = '<span class="p" style="display:inline-block;width:0;height:0;vertical-align:baseline"></span><span class="t">H</span>';
    document.body.appendChild(d);
    const r = document.createRange(); const tn = d.querySelector('.t').firstChild; r.setStart(tn, 0); r.setEnd(tn, 1);
    const rr = r.getClientRects()[0], pr = d.querySelector('.p').getBoundingClientRect();
    ratio[k] = { base: (pr.top - rr.top) / 200, h: rr.height / 200 };
    d.remove(); return ratio[k];
  }
  function firstText(el) {
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, { acceptNode: n => /\S/.test(n.nodeValue) ? 1 : 3 });
    return w.nextNode();
  }
  function effOpacity(el) {
    let o = 1;
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      o *= parseFloat(cs.opacity);
    }
    return o;
  }
  const rgb = s => { const m = s.match(/[\d.]+/g).map(Number); return [m[0] / 255, m[1] / 255, m[2] / 255]; };
  function addText(name, el, clip) { units.push({ name, el, clip }); return units.length - 1; }

  function setup() {
    // wrap bare text nodes that need to become their own layers
    const logoEl = [...document.querySelectorAll('.c')].find(e => e.textContent === 'HoduSoft' && /150px|170px/.test(e.style.fontSize));
    logoEl.innerHTML = '<span>Hodu</span><span style="color:var(--lime)">Soft</span>';
    const ctaPill = [...document.querySelectorAll('.pill')].find(p => p.textContent.indexOf('BOOK A FREE DEMO') >= 0);
    const tn = ctaPill.firstChild; const sp = document.createElement('span'); sp.textContent = tn.nodeValue.trim(); ctaPill.replaceChild(sp, tn);

    // headlines: every .hl line is a clip group (overflow:hidden), words are units
    document.querySelectorAll('.hl').forEach((h, hi) => {
      h.querySelectorAll('.ln').forEach((ln, li) => {
        const c = { name: `HL${String(hi + 1).padStart(2, '0')} line ${li + 1}`, el: ln, words: [] };
        ln.querySelectorAll('.w').forEach((w, wi) => c.words.push(addText(`${w.textContent}`, w, ln)));
        clips.push(c);
      });
    });
    // slates
    SL.forEach((sl, j) => {
      addText(`Slate ${j + 1} label`, sl.lab);
      const c = { name: `Slate ${j + 1} product name`, el: sl.nm, words: [addText(sl.nm.textContent, sl.nm.firstChild, sl.nm)] };
      clips.push(c);
      addText(`Slate ${j + 1} tagline`, sl.sb);
    });
    // brand reveal
    addText('Brand MEET', meet); addText('Brand HoduSoft', brand); addText('Brand products', by);
    // product tag (two colour runs, text changes per chapter) + feature chip
    units.push({ name: 'Tag product', el: null, dyn: () => tag.children[0] });
    units.push({ name: 'Tag by HoduSoft', el: null, dyn: () => tag.children[1] });
    addText('Feature chip', chip);
    shapes.push({ name: 'Feature chip outline', el: chip, kind: 'rect', stroke: rgb(getComputedStyle(chip).borderTopColor), sw: 2 });
    // end card
    addText('End logo Hodu', logoEl.children[0]); addText('End logo Soft', logoEl.children[1]);
    addText('End products', sub5); addText('End URL', url);
    shapes.push({ name: 'CTA pill', el: ctaPill, kind: 'rect', fill: rgb(getComputedStyle(ctaPill).backgroundColor) });
    addText('CTA text', sp);
    const arr = ctaPill.children[1];
    shapes.push({ name: 'CTA arrow circle', el: arr, kind: 'ellipse', fill: [10 / 255, 10 / 255, 11 / 255], arrow: true });
    return { units: units.length, clips: clips.length, shapes: shapes.length };
  }

  function sampleUnit(u) {
    const el = u.dyn ? u.dyn() : u.el;
    if (!el) return null;
    const o = effOpacity(el);
    const tnode = firstText(el);
    const text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!tnode || o <= 0.001) return { o: 0, text };
    const k = fontKey(el), cs = getComputedStyle(el), fs = parseFloat(cs.fontSize), cal = calibrate(k);
    const r = document.createRange(); const i0 = tnode.nodeValue.search(/\S/); r.setStart(tnode, i0); r.setEnd(tnode, i0 + 1);
    const rr = r.getClientRects()[0]; if (!rr) return { o: 0, text };
    const s = rr.height / (cal.h * fs);
    let x = rr.left - SR.left, y = rr.top - SR.top + cal.base * fs * s;
    if (u.clip) { const cr = u.clip.getBoundingClientRect(); x = rr.left - cr.left; y = rr.top - cr.top + cal.base * fs * s; }
    const ls = parseFloat(cs.letterSpacing) || 0;
    return { o, text, x, y, s, font: k, fs, tr: Math.round(ls / fs * 1000), col: rgb(cs.color) };
  }
  function sampleBox(el) {
    const o = effOpacity(el); if (o <= 0.001) return { o: 0 };
    const r = el.getBoundingClientRect(); const s = r.width / el.offsetWidth;
    return { o, x: r.left - SR.left + r.width / 2, y: r.top - SR.top + r.height / 2, s, w: el.offsetWidth, h: el.offsetHeight };
  }
  function sample(t) {
    render(t);
    return {
      u: units.map(sampleUnit),
      c: clips.map(c => sampleBox(c.el)),
      s: shapes.map(sh => sampleBox(sh.el)),
    };
  }
  function meta() {
    return {
      units: units.map(u => ({ name: u.name, clip: u.clip ? clips.findIndex(c => c.el === u.clip) : -1 })),
      clips: clips.map(c => ({ name: c.name, words: c.words })),
      shapes: shapes.map(s => ({ name: s.name, kind: s.kind, fill: s.fill || null, stroke: s.stroke || null, sw: s.sw || 0, arrow: !!s.arrow })),
    };
  }
  function hideForPlate() {
    const css = document.createElement('style');
    css.textContent = '.aehide{visibility:hidden!important}';
    document.head.appendChild(css);
    units.forEach(u => { if (u.el) u.el.classList.add('aehide'); });
    clips.forEach(c => c.el.classList.add('aehide'));
    shapes.forEach(s => s.el.classList.add('aehide'));
    tag.classList.add('aehide');
  }
  return { setup, sample, meta, hideForPlate };
})();
