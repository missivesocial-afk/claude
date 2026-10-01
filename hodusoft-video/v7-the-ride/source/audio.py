import numpy as np, soundfile as sf, json
from scipy.signal import butter, sosfilt, resample_poly, fftconvolve
SR = 44100; DUR = 37.75; N = int(SR * DUR)
rng = np.random.default_rng(21)
DU = json.load(open('durs.json'))
T = dict(hold=0.6, s2=4.3, menu=4.35, s3=9.6, x1=9.8, x2=10.7, x3=11.6, s4=12.8, rep=12.9, sam1=14.5, rep2=15.6, sam2=15.75,
         s5=17.35, snap=17.45, land=18.3, narr=18.85, s6=20.95, rail=21.55, meet=21.85, s7=22.95, pick=23.25, fly=23.65, arrive=24.95,
         maya=25.15, res=27.75, s7b=28.55, s8=30.85, e1=31.05, e2=32.45, logo=33.85, cta=34.65, p1=4.45, p2=5.65, p3=6.9, jump=8.25, lv2=8.9)
t = np.arange(N) / SR
z = lambda: np.zeros(N)
tt = lambda d: np.arange(int(d * SR)) / SR
def add(b, s, t0, g=1.0):
    i = int(t0 * SR); j = min(N, i + len(s))
    if 0 <= i < N: b[i:j] += s[:j - i] * g
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
noise = lambda n: rng.standard_normal(n)
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
def load(f, g=1.0):
    a, sr = sf.read(f); a = resample_poly(a, SR, sr) if sr != SR else a
    return a / (np.max(np.abs(a)) + 1e-9) * g
def reverb(x, secs, damp=4000, wet=.25):
    n = int(secs * SR); ir = noise(n) * np.exp(-np.arange(n) / SR * (6.9 / secs)); ir = lp(ir, damp); ir /= np.sqrt(np.sum(ir ** 2))
    return x * (1 - wet) + fftconvolve(x, ir)[:len(x)] * wet
def tone(f, d, dec=6, h=(1, .3, .1), a=.004):
    s = tt(d); return sum(g * np.sin(2 * np.pi * f * (k + 1) * s) for k, g in enumerate(h)) * np.exp(-s * dec) * np.minimum(1, s / a)
def phone(x): return np.tanh(bp(x, 320, 3300) * 2.0) * .6
def sweep(f0, f1, d, g=.2, shape='exp'):
    s = tt(d); f = f0 * (f1 / f0) ** (s / d) if shape == 'exp' else f0 + (f1 - f0) * s / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, s / .01) * np.minimum(1, (d - s) / .04) * g

# ---------------- cartoon SFX kit ----------------
def boing(f=220, d=.45, g=.25): s = tt(d); fr = f * (1 + .6 * np.sin(2 * np.pi * 9 * s) * np.exp(-s * 6)); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-s * 5) * g
def pop(f=700, g=.25): s = tt(.12); fr = f * (1 + 2 * np.exp(-s * 60)); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-s * 35) * g
def ping(m, g=.15, d=.8): return tone(mid(m), d, 5, (1, .4, .15)) * g
def whoosh(d=.35, g=.2, lo=600, hi=7000): s = tt(d); k = s / d; return bp(noise(len(s)), lo, hi) * np.sin(np.pi * k) ** 2 * g
def thud(g=.5): s = tt(.25); f = 60 + 90 * np.exp(-s * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-s * 14) * g
def click(g=.2): n = int(.015 * SR); return hp(noise(n), 2500) * np.exp(-np.arange(n) / SR * 400) * g
def sparkle(d=.8, g=.08):
    x = np.zeros(int(d * SR))
    for k in range(14):
        i = int(rng.uniform(0, d - .15) * SR); s_ = tone(rng.uniform(2500, 5500), .15, 25, (1,)); x[i:i + len(s_)] += s_[:len(x) - i]
    return x * g
def twang(g=.3): s = tt(.6); f = 180 * (1 + .15 * np.exp(-s * 8) * np.sin(2 * np.pi * 30 * s)); return (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .3 + np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-s * 6) * g
def trombone(m, d, g=.18):  # brassy note with a droopy vibrato
    s = tt(d); f = mid(m) * (1 + .012 * np.sin(2 * np.pi * 5.5 * s) * np.clip(s / .2, 0, 1)) * (1 - .03 * (s / d) ** 2)
    x = sum(h * np.sin(2 * np.pi * np.cumsum(f * (k + 1)) / SR) for k, h in enumerate([1, .7, .5, .35, .2, .1]))
    return lp(x, 2200) * np.minimum(1, s / .04) * np.minimum(1, (d - s) / .08) * g
def scratch(g=.25): s = tt(.3); f = 900 * (1 - s / .3) + 120; return bp(noise(len(s)), 400, 4000) * (np.sin(2 * np.pi * np.cumsum(f) / SR) > 0) * np.exp(-s * 6) * g

fx = z()
# hook: hold muzak (tinny) + IVR in phone band
hold = z(); b = 60 / 108
mel = [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 83, 79, 76, 74]
for i, m in enumerate(mel):
    t0 = .05 + i * b / 2
    if t0 > T['s2']: break
    add(hold, tone(mid(m), b / 2 * 1.6, 5, (1, .5, .2, .1)), t0, .2)
hold = bp(hold, 400, 3200) * 1.5 * (t < T['s2'])
add(fx, phone(load('vo/hold.wav', .6)), T['hold'])
add(fx, sparkle(.6, .05), 3.0)                                  # cobweb sparkle
add(fx, sweep(500, 260, .5, .08), 1.95)                          # yawn
# IVR maze
for f, k in (('m1', 'p1'), ('m2', 'p2'), ('m3', 'p3')): add(fx, phone(load(f'vo/{f}.wav', .6)), T[k])
for i in range(3): add(fx, pop(500 + i * 120, .12), T['s2'] + i * .06)
for i, k in enumerate(('p1', 'p2', 'p3')): add(fx, ping(79 + i * 4, .1, .6), T[k])          # each door lights
add(fx, boing(260, .4, .2), T['jump']); add(fx, whoosh(.35, .2, 400, 6000), T['jump'] + .35)
for i in range(3): add(fx, pop(500 + i * 120, .12), T['lv2'] + i * .06)
add(fx, sweep(420, 300, .5, .06), T['lv2'] + .3)                                              # little sigh
# transfer ping-pong
for i, tl in enumerate([T['x1'] - .25, T['x2'] - .25, T['x3'] - .25, T['x3'] + .8]):
    add(fx, boing(300 + i * 40, .35, .18), tl); add(fx, ping(84 + i * 2, .14), tl + .42)
add(fx, load('vo/xfer1.wav', .55), T['x1']); add(fx, load('vo/xfer2.wav', .55), T['x2']); add(fx, load('vo/xfer3.wav', .55), T['x3'])
add(fx, sweep(400, 900, .25, .05, 'lin') * 1, T['x3'] + .4); add(fx, boing(500, .9, .1), T['x3'] + .6)   # dizzy
# repeat
for tb in (T['rep'], T['rep2']): add(fx, pop(650, .18), tb)
for tb in (T['sam1'], T['sam1'] + .55): add(fx, pop(900, .16), tb)
add(fx, pop(500, .25), T['sam2']); add(fx, lp(noise(int(.3 * SR)), 300) * np.exp(-tt(.3) * 8) * .2, T['sam2'])
add(fx, load('vo/repeat.wav', .55), T['rep']); add(fx, load('vo/sam1.wav', .55), T['sam1']); add(fx, load('vo/sam2.wav', .62), T['sam2'])
# the drop
add(fx, scratch(.3), T['snap'] - .03); add(fx, twang(.32), T['snap'])
add(fx, sweep(1600, 300, T['land'] - T['snap'] - .05, .14), T['snap'] + .05)       # slide-whistle fall
add(fx, thud(.55), T['land']); add(fx, boing(160, .5, .15), T['land'] + .02)
for i, (m, d) in enumerate([(58, .38), (57, .38), (56, .38), (55, 1.1)]): add(fx, trombone(m, d, .14), T['land'] + .35 + i * .4)   # wah wah wah wahhh
# meet
add(fx, whoosh(.5, .3, 300, 8000), T['rail'] - .15); add(fx, sparkle(1.0, .1), T['rail']); add(fx, ping(84, .14, 1.2) + ping(91, .1, 1.2), T['meet'])
# good ride
add(fx, whoosh(.4, .15), T['s7']); add(fx, ping(88, .15) + ping(93, .1), T['pick'])
for k in range(5): add(fx, whoosh(.25, .12, 1200, 8000), T['fly'] + k * .25)
add(fx, ping(84, .14), T['arrive']); add(fx, pop(800, .2), T['maya'])
add(fx, ping(84, .15, 1.2) + ping(88, .12, 1.2) + ping(91, .12, 1.2), T['res'])
for k in range(10): add(fx, pop(rng.uniform(600, 1400), .12), T['res'] + .1 + k * .06)
for k in range(40): add(fx, pop(rng.uniform(500, 1600), .08), T['s7b'] + .3 + rng.uniform(0, 1.6))   # pile turns happy
add(fx, sparkle(1.5, .1), T['s7b'] + .4)
# end
add(fx, whoosh(.35, .15), T['logo'] - .1); add(fx, pop(600, .25), T['logo']); add(fx, boing(330, .4, .12), T['logo'] + .1)
add(fx, click(.25), T['cta'] - .2)

# ---------------- VO (clean lines) ----------------
vo = z()
add(vo, load('vo/narr.wav', .78), T['narr']); add(vo, load('vo/maya.wav', .72), T['maya'])
add(vo, load('vo/e1.wav', .78), T['e1']); add(vo, load('vo/e2.wav', .78), T['e2']); add(vo, load('vo/cta.wav', .78), T['cta'])
dialog = fx * 0  # character lines are already in fx; build a ducking key from all speech
spk = z()
for f, t0, g in [('hold', T['hold'], .6), ('m1', T['p1'], .6), ('m2', T['p2'], .6), ('m3', T['p3'], .6), ('xfer1', T['x1'], .55), ('xfer2', T['x2'], .55), ('xfer3', T['x3'], .55), ('repeat', T['rep'], .55),
                 ('sam1', T['sam1'], .55), ('sam2', T['sam2'], .62)]: add(spk, load(f'vo/{f}.wav', g), t0)
spk += vo
# ---------------- MUSIC ----------------
mus = z(); kenv = z()
def kick(): s = tt(.35); f = 50 + 110 * np.exp(-s * 30); return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-s * 8) * 1.6)
KICK = kick()
def snare(): s = tt(.18); return bp(noise(len(s)), 1200, 7000) * np.exp(-s * 22) * .45 + np.sin(2 * np.pi * 190 * s) * np.exp(-s * 30) * .3
SN = snare()
def hat(): n = int(.04 * SR); return hp(noise(n), 8000) * np.exp(-np.arange(n) / SR * 90) * .25
HT = hat()
def pluck(m, d=.35, g=.08): s = tt(d); f = mid(m); return (np.sin(2 * np.pi * f * s) + .4 * np.sin(4 * np.pi * f * s) + .15 * np.sin(6 * np.pi * f * s)) * np.exp(-s * 9) * np.minimum(1, s / .002) * g
def bassn(m, d, g=.2): s = tt(d); f = mid(m); return lp(np.sign(np.sin(2 * np.pi * f * s)) * .4 + np.sin(2 * np.pi * f * s), 700) * np.exp(-s * 3) * np.minimum(1, s / .004) * g
beat = .5
# act 1 (bad ride): quirky minor bounce, more layers as it gets worse; stops dead at the snap
PROG1 = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 56, 59]]
k = 0
while True:
    tb = T['s2'] - 2.0 + k * beat
    if tb >= T['snap'] - .02: break
    if tb >= 2.3:
        bar = (k // 4) % 4; sub = k % 4; heat = np.clip((tb - 4) / 12, 0, 1)
        add(mus, KICK, tb, .6 + .3 * heat); add(kenv, np.exp(-tt(.25) * 14), tb)
        if sub in (1, 3): add(mus, SN, tb, .5 + .3 * heat)
        add(mus, HT, tb + beat / 2, .8);
        if heat > .4: add(mus, HT, tb + beat / 4, .5); add(mus, HT, tb + 3 * beat / 4, .5)
        add(mus, bassn(PROG1[bar][0] - 12, beat * .9), tb)
        for q in range(2):
            m = PROG1[bar][(k * 2 + q) % 3] + 12 + (12 if heat > .7 and q else 0); add(mus, pluck(m), tb + q * beat / 2)
    k += 1
# act 2 (good ride): bright major groove from the rail to the end
PROG2 = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
k = 0
while True:
    tb = T['s7'] + k * beat
    if tb > DUR - 1.2: break
    bar = (k // 4) % 4; sub = k % 4
    add(mus, KICK, tb, .85); add(kenv, np.exp(-tt(.25) * 14), tb)
    if sub in (1, 3): add(mus, SN, tb, .6)
    for h in range(4): add(mus, HT, tb + h * beat / 4, .5 if h % 2 else .8)
    add(mus, bassn(PROG2[bar][0] - 12, beat * .45), tb); add(mus, bassn(PROG2[bar][0], beat * .45, .12), tb + beat / 2)
    for q in range(4): add(mus, pluck(PROG2[bar][(k + q) % 3] + 12 + (12 if q == 3 else 0), .3, .07), tb + q * beat / 4)
    k += 1
for m in (48, 60, 64, 67, 72): add(mus, tone(mid(m), 2.5, 1.6, (1, .3, .1)) * .05, DUR - 1.6)
mus = reverb(mus, 1.2, 6000, .15)
music = mus * (1 - .45 * np.clip(kenv, 0, 1))
# ---------------- MIX ----------------
venv = np.abs(spk); kk = int(.25 * SR); venv = np.convolve(venv, np.ones(kk) / kk, 'same'); duck = 1 - .6 * np.clip(venv / .04, 0, 1)
full = vo * 1.0 + fx * .85 + hold * .5 + music * .38 * duck
fo = int(.5 * SR); full[-fo:] *= np.linspace(1, 0, fo) ** 2
full = np.tanh(full * 1.1) / np.tanh(1.1); full /= np.max(np.abs(full)) / .9
sf.write('audio.wav', np.stack([full, full], 1), SR, subtype='PCM_16')
m = spk != 0; r = lambda x: 20 * np.log10(np.sqrt(np.mean(x[m] ** 2)) + 1e-9)
print('speech', round(r(spk), 1), 'music', round(r(music * .38 * duck), 1))
for a_, b_, n in ((0, 4.3, 'hook'), (4.3, 8.3, 'ivr'), (8.3, 11.5, 'pong'), (11.5, 16, 'repeat'), (16, 19.7, 'drop'), (19.7, 21.7, 'meet'), (21.7, 29.6, 'ride'), (29.6, 36.5, 'end')):
    x = full[int(a_ * SR):int(b_ * SR)]; print(n, round(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9), 1))
