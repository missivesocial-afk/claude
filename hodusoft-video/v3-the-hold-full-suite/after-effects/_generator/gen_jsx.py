import json, math

FPS = 30
TM = json.load(open('../v3/timing.json'))
L = TM['L']
VO_TEXT = ["Every minute on hold, another customer hangs up.", "Your agents? Juggling six screens.", "Your supervisors? Flying blind.",
           "Meet HoduSoft.", "HoduCC. The AI contact center.", "Smart routing sends every call to the right agent.",
           "Predictive dialers keep agents talking, not waiting.", "Voice, WhatsApp, email and chat. One screen.",
           "AI scores every call. Supervisors see it live.", "HoduPBX. One phone system, unlimited brands.",
           "SIP trunking. Auto provisioning. Call recording.", "HoduBlast. Voice and SMS, to thousands at once.",
           "Nobody likes waiting.", "Now, nobody has to."]
MARKERS = [(0, "HOOK - on hold"), (3.55, "Call dropped"), (L[0], "PROBLEM 1 - hang-ups"), (L[1], "PROBLEM 2 - six screens"),
           (L[2], "PROBLEM 3 - flying blind"), (L[3] - .25, "BRAND - Meet HoduSoft"), (L[4] - .12, "SLATE 01 - HoduCC"),
           (L[5], "HoduCC - routing"), (L[6], "HoduCC - predictive dialer"), (L[7], "HoduCC - omnichannel"),
           (L[8], "HoduCC - AI call scoring"), (L[9] - .12, "SLATE 02 - HoduPBX"), (L[9] + 1.0, "HoduPBX - multi-tenant"),
           (L[10], "HoduPBX - SIP / provisioning / recording"), (L[11] - .12, "SLATE 03 - HoduBlast"),
           (L[11] + .9, "HoduBlast - broadcast"), (L[12], "END - rewind"), (L[13] + .75, "END CARD - logo + CTA")]


def compress(vals, eps):
    """keep frames where the value changes; linear interpolation between kept keys reproduces the series"""
    n = len(vals)
    keep = []
    for i in range(n):
        if i == 0 or i == n - 1 or abs(vals[i] - vals[i - 1]) > eps or abs(vals[i] - vals[i + 1]) > eps:
            keep.append(i)
    # drop keys that sit on the straight line between the last kept key and the next candidate
    out = []
    for j, i in enumerate(keep):
        if out and j < len(keep) - 1:
            a, b = out[-1], keep[j + 1]
            if all(abs(vals[a] + (vals[b] - vals[a]) * (k - a) / (b - a) - vals[k]) <= eps for k in range(a, b + 1)):
                continue
        out.append(i)
    return out


def keyed(frames_vals, f0, eps, nd):
    idx = compress(frames_vals, eps)
    return [[round((f0 + i) / FPS, 5), round(frames_vals[i], nd)] for i in idx]


def track(samples, f0):
    """samples: list of dicts (x,y,s,o) with o possibly 0 and missing coords -> hold last valid"""
    last = None
    xs, ys, ss, os_ = [], [], [], []
    firstvalid = next((s for s in samples if s and s.get('o', 0) > 0), None)
    for s in samples:
        if s and s.get('o', 0) > 0 and 'x' in s:
            last = s
        ref = last or firstvalid
        xs.append(ref['x']); ys.append(ref['y']); ss.append(ref['s']); os_.append((s or {}).get('o', 0) * 100)
    return {'x': keyed(xs, f0, .05, 2), 'y': keyed(ys, f0, .05, 2), 's': keyed([v * 100 for v in ss], f0, .02, 3), 'o': keyed(os_, f0, .1, 2)}


def segments(series, keyfn):
    """split a per-frame series into runs of constant key among visible frames"""
    segs, cur, curkey = [], None, None
    for f, s in enumerate(series):
        vis = s and s.get('o', 0) > 0.001 and 'x' in s
        if vis:
            k = keyfn(s)
            if cur is None or k != curkey:
                if cur is not None:
                    segs.append(cur)
                cur, curkey = {'key': k, 'first': f, 'last': f}, k
            else:
                cur['last'] = f
    if cur is not None:
        segs.append(cur)
    return segs


def build_format(path, label, plate):
    D = json.load(open(path))
    fr, meta, N = D['frames'], D['meta'], D['N']
    out = {'label': label, 'W': D['W'], 'H': D['H'], 'fps': FPS, 'dur': round(N / FPS, 4), 'plate': plate, 'shapes': [], 'clips': [], 'texts': []}

    def seg_range(seg):
        a = max(0, seg['first'] - 1); b = min(N - 1, seg['last'] + 1)
        return a, b

    def text_layers(ui, clip_opacity=None):
        ser = [f['u'][ui] for f in fr]
        if clip_opacity is not None:  # word opacity is relative to its line precomp
            ser = [dict(s, o=(s['o'] / clip_opacity[i] if clip_opacity[i] > 0.001 else 0)) if s else s for i, s in enumerate(ser)]
        res = []
        for seg in segments(ser, lambda s: (s['text'], s['font'], round(s['fs'], 1), tuple(round(c, 3) for c in s['col']))):
            a, b = seg_range(seg)
            s0 = ser[seg['first']]
            sub = [ser[i] if (ser[i] and ser[i].get('text') == s0['text']) else {'o': 0} for i in range(a, b + 1)]
            res.append({'name': meta['units'][ui]['name'] if meta['units'][ui]['name'] != s0['text'] else s0['text'],
                        'text': s0['text'], 'font': s0['font'], 'fs': round(s0['fs'], 2), 'tr': s0['tr'],
                        'col': [round(c, 4) for c in s0['col']], 'in': round(a / FPS, 5), 'out': round((b + 1) / FPS, 5),
                        'k': track(sub, a)})
        return res

    # clip groups -> precomps with word layers
    in_clip = set()
    for ci, c in enumerate(meta['clips']):
        ser = [f['c'][ci] for f in fr]
        segs = segments(ser, lambda s: 1)
        if not segs:
            continue
        a, b = segs[0]['first'], segs[-1]['last']; a = max(0, a - 1); b = min(N - 1, b + 1)
        w = max(s['w'] for s in ser if s and s.get('o', 0) > 0); h = max(s['h'] for s in ser if s and s.get('o', 0) > 0)
        cop = [s.get('o', 0) if s else 0 for s in ser]
        words = []
        for ui in c['words']:
            in_clip.add(ui)
            ws = text_layers(ui, cop)
            if c['name'].startswith('HL'):  # headlines are text-transform:uppercase in the design
                for w_ in ws: w_['text'] = w_['text'].upper(); w_['name'] = w_['text']
            words += ws
        out['clips'].append({'name': c['name'], 'w': int(math.ceil(w)), 'h': int(math.ceil(h)), 'in': round(a / FPS, 5), 'out': round((b + 1) / FPS, 5),
                             'k': track(ser[a:b + 1], a), 'words': words})
    # free text units
    for ui, u in enumerate(meta['units']):
        if ui in in_clip or u['clip'] >= 0:
            continue
        ts = text_layers(ui)
        if 'tagline' in u['name']:
            for t_ in ts: t_['text'] = t_['text'].upper()
        out['texts'] += ts
    # shapes
    for si, sh in enumerate(meta['shapes']):
        ser = [f['s'][si] for f in fr]
        for seg in segments(ser, lambda s: (round(s['w']), round(s['h']))):
            a, b = seg_range(seg)
            s0 = ser[seg['first']]
            sub = [ser[i] if (ser[i] and ser[i].get('o', 0) > 0 and round(ser[i]['w']) == round(s0['w'])) else {'o': 0} for i in range(a, b + 1)]
            out['shapes'].append({'name': sh['name'], 'kind': sh['kind'], 'fill': sh['fill'], 'stroke': sh['stroke'], 'sw': sh['sw'], 'arrow': sh['arrow'],
                                  'w': round(s0['w'], 2), 'h': round(s0['h'], 2), 'in': round(a / FPS, 5), 'out': round((b + 1) / FPS, 5), 'k': track(sub, a)})
    return out


DATA = {
    'formats': [build_format('data_9x16.json', '9x16', 'footage/plate_9x16.mp4'),
                build_format('data_16x9.json', '16x9', 'footage/plate_16x9.mp4')],
    'vo': [{'file': 'audio/vo/VO_%02d.wav' % (i + 1), 'start': L[i], 'text': VO_TEXT[i]} for i in range(14)],
    'ivrStart': TM['ivr'],
    'markers': [[round(t, 3), n] for t, n in MARKERS],
}
for f in DATA['formats']:
    print(f['label'], 'texts', len(f['texts']), 'clips', len(f['clips']), 'words', sum(len(c['words']) for c in f['clips']), 'shapes', len(f['shapes']))

js = open('builder_template.jsx').read().replace('__DATA__', json.dumps(DATA, separators=(',', ':')))
open('HoduSoft_TheHold_BUILD.jsx', 'w').write(js)
print('jsx bytes', len(js))
