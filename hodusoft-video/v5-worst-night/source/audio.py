import numpy as np, soundfile as sf, json
from scipy.signal import butter, sosfilt, resample_poly, fftconvolve
SR = 44100; DUR = 60.0; N = int(SR * DUR)
rng = np.random.default_rng(11)
D = json.load(open('vo/durs.json'))
T = dict(n1=[1.2, 2.0, 2.7, 3.4, 4.4], s2=6.6, sh2b=9.4, click1=10.0, modal=10.35, sh2c=11.8, ivr=12.0, sh2d=14.8, sh2e=16.8,
         s3=18.8, ceo1=20.2, sup1=23.4, s4=26.0, sup2=27.75, s5=28.8, nb1=29.6, nb2=31.3, s6=33.2, sh6b=36.8, addClick=37.2, prov=37.5,
         sh6c=40.4, whClick=41.0, wh=41.3, fix=43.0, emma=43.6, sh6d=44.6, close=45.8, s7=47.2, ceo2=48.4, dana=51.1, react=52.9,
         s8=53.8, narr=54.3, logo=56.8, cta=57.4)
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
def reverb(x, secs, damp=3000, wet=.35):
    n = int(secs * SR); ir = noise(n) * np.exp(-np.arange(n) / SR * (6.9 / secs)); ir = lp(ir, damp); ir /= np.sqrt(np.sum(ir ** 2))
    return x * (1 - wet) + fftconvolve(x, ir)[:len(x)] * wet
def seg(a, b, fi=.3, fo=.3): return np.clip((t - a) / fi, 0, 1) * np.clip((b - t) / fo, 0, 1)

# ======================= AMBIENCE =======================
amb = z()
rain = bp(noise(N), 700, 6000) * .05 + lp(noise(N), 400) * .035
drops = np.zeros(N)
for i in rng.integers(0, N - 400, 5200): drops[i:i + 300] += noise(300) * np.exp(-np.arange(300) / 25) * rng.uniform(.1, .5)
rain += hp(drops, 1500) * .06
rain_env = seg(0, T['s4'], .8, .2) * 1.0 + seg(T['s5'], T['s7'], .6, .3) * .55     # heavier in act 1, softer in act 2
rain_env *= np.where((t > T['s3']) & (t < T['s4']), 0, 1)                        # board call: no rain
amb += lp(rain, 3500) * rain_env
for tl in (0.55, 5.4, 13.2):                                                       # thunder follows the lightning
    s = tt(4.5); th = lp(noise(len(s)), 140) * (np.exp(-s * 1.1) * (1 - np.exp(-s * 12))) * 1.4 + lp(noise(len(s)), 600) * np.exp(-s * 5) * .3
    add(amb, th, tl + .7, .5)
fridge = (np.sin(2 * np.pi * 60 * t) * .01 + np.sin(2 * np.pi * 180 * t) * .004 + lp(noise(N), 300) * .012)
amb += fridge * (seg(T['s2'], T['s3'], .1, .1) + seg(T['s6'], T['s7'], .1, .1))
roomtone = lp(noise(N), 250) * .006 * (seg(T['s3'], T['s4'], .05, .1) + seg(T['s7'], T['s8'], .05, .2))
amb += roomtone

# ======================= SFX =======================
fx = z()
def click(g=.25, f=2500): n = int(.018 * SR); return hp(noise(n), f) * np.exp(-np.arange(n) / SR * 380) * g
def ding(ms, g=.15, d=1.0, dec=4.5): return sum(np.sin(2 * np.pi * mid(m) * tt(d)) * np.exp(-tt(d) * dec) + .25 * np.sin(4 * np.pi * mid(m) * tt(d)) * np.exp(-tt(d) * dec * 2) for m in ms) * g
def buzz_on_wood(d=.42):
    s = tt(d); m = (np.sin(2 * np.pi * 9 * s) > -.2).astype(float)
    x = (np.sign(np.sin(2 * np.pi * 150 * s)) * .5 + np.sin(2 * np.pi * 90 * s)) * m * np.minimum(1, s / .01) * np.minimum(1, (d - s) / .03)
    return lp(x, 900) * .5 + hp(x * noise(len(s)) * .2, 2000) * .15
def whoosh(d, g=.2, lo=400, hi=6000): s = tt(d); k = s / d; return bp(noise(len(s)), lo, hi) * np.sin(np.pi * k) ** 2 * g
# act 1: phone buzzes like an alarm
for tn in T['n1']: add(fx, buzz_on_wood(), tn, .9); add(fx, ding([76], .05, .5), tn + .02)
for tn in (T['sh2b'], T['sh2c'], T['sh2d'], T['sh2e']): add(fx, whoosh(.35, .08, 800, 7000), tn - .15)
add(fx, click(.3), T['click1']); add(fx, ding([58, 57], .12, .6, 8), T['modal'])          # dull error tone
add(fx, click(.25), T['sh2c'] - .15)
for k in range(12): add(fx, click(.12, 4000), 7.0 + k * .31 + rng.uniform(0, .1))           # typing
for k in range(8): add(fx, click(.08, 3000), T['sh2d'] + k * .25)                           # scroll ticks
# IVR over the softphone (phone band)
ivr = bp(load('vo/ivr.wav', .55), 300, 3400); ivr = np.tanh(ivr * 2) * .6
add(fx, ivr, T['ivr'] + .25)
ring = np.concatenate([np.sin(2 * np.pi * 440 * tt(.5)) + np.sin(2 * np.pi * 480 * tt(.5)), np.zeros(int(.3 * SR))]) * .05
add(fx, bp(ring, 300, 3400), T['ivr'] - .5)
# clock ticks through act 1, accelerating
tk = T['s2'] + .2
while tk < T['s3'] - .1:
    add(fx, hp(click(.18, 1500), 1200), tk); tk += max(.45, 1.0 - (tk - T['s2']) * .045)
# board call 1
add(fx, ding([72, 79], .09, .9), T['s3'] + .1)
# rewind
s = tt(1.5); f = 300 * np.exp(s * 2.2); rw = np.sin(2 * np.pi * np.cumsum(f) / SR) * .06 + bp(noise(len(s)), 1500, 8000) * .08 * (s / 1.5)
rw *= (np.sin(2 * np.pi * 18 * s) > 0) * .7 + .3
add(fx, rw, T['s4']); add(fx, lp(noise(int(.25 * SR)), 500) * np.exp(-tt(.25) * 12) * .5, T['s4'] + 1.45)  # tape stop thud
add(fx, whoosh(1.0, .06, 2000, 9000) * np.linspace(0, 1, int(1.0 * SR)), T['s5'] - 1.0)          # reverse swell into act 2
# act 2: one warm chime each, no buzzing
add(fx, ding([79, 84, 88], .10, 1.6, 2.5), T['nb1']); add(fx, ding([84, 88], .07, 1.2, 3), T['nb2'])
add(fx, click(.25), T['addClick'])
for i in range(30): add(fx, ding([[84, 86, 88, 91, 93][i % 5] + 12 * (i // 15)], .025, .4, 9), T['prov'] + i * (2.0 / 30))
add(fx, ding([91, 96], .06, .8), T['prov'] + 2.05)
add(fx, click(.25), T['whClick'])
add(fx, ding([76, 81], .07, .9), T['fix']); add(fx, ding([84], .05, .8), T['emma'])
s = tt(.6); hinge = bp(noise(len(s)), 300, 1500) * np.sin(np.pi * s / .6) * .05; add(fx, hinge, T['close'])
add(fx, lp(noise(int(.2 * SR)), 350) * np.exp(-tt(.2) * 20) * .45, T['close'] + .58)
add(fx, ding([72, 79], .09, .9), T['s7'] + .1)
for i in range(5): add(fx, ding([88 + i % 3], .03, .3, 10), T['react'] + i * .15 + .1)
# ======================= VOICES =======================
vo = z()
def callvoice(a): return reverb(bp(a, 110, 7500), .25, 6000, .06)
add(vo, callvoice(load('vo/ceo1.wav', .7)), T['ceo1'])
add(vo, callvoice(load('vo/ceo2.wav', .7)), T['ceo2'])
add(vo, callvoice(load('vo/dana.wav', .72)), T['dana'])
wh = load('vo/whisper.wav', .42); wh = hp(wh, 180) + .2 * hp(wh, 3000); add(vo, wh, T['wh'])
nr = reverb(load('vo/narr.wav', .78), .6, 7000, .12); add(vo, nr, T['narr'])
# ======================= SCORE =======================
mus = z()
def saw(f, d): s = tt(d); return 2 * ((f * s) % 1) - 1
# act 1: low drone swelling to a string cluster, hard cut at the board call
drone = z()
for m, g in ((33, 1), (40, .6), (45, .4)):
    for det in (-.004, .004): drone += np.sin(2 * np.pi * mid(m) * (1 + det) * t) * g
dr_env = np.clip(t / 3, 0, 1) * (0.5 + .5 * np.clip((t - 6) / 12, 0, 1)) * (t < T['s3'])
mus += lp(drone, 300) * .05 * dr_env
cluster = z(); s = t
for m in (57, 58, 64, 65, 69):
    cluster += lp(saw(mid(m) * 1.0, DUR) + saw(mid(m) * 1.006, DUR), 1400) * .5
cl_env = np.clip((t - 13.0) / 5.8, 0, 1) ** 2 * (t < T['s3'])
mus += cluster * .018 * cl_env
# board call 1: the silence, then one low piano note under the title
def piano(m, d=4, g=.1):
    s = tt(d); f = mid(m)
    x = sum(h * np.sin(2 * np.pi * f * (i + 1) * s * (1 + .0004 * i)) * np.exp(-s * (1.0 + i * .8)) for i, h in enumerate([1, .5, .25, .12, .06]))
    return x * np.minimum(1, s / .004) * g
add(mus, piano(26, 5, .22) + piano(38, 5, .1), T['sup1'] - .05)
# act 2: warm piano, pad and a soft pulse, building to the board call
CH = [[53, 60, 64, 69], [52, 59, 64, 67], [50, 57, 62, 65], [46, 58, 62, 65]]    # Fmaj7 Em7 Dm7 Bbmaj7
bpm = 76; beat = 60 / bpm; t0 = T['s5'] + .2
i = 0
while t0 + i * beat < T['dana'] - .3:
    tb = t0 + i * beat; c = CH[(i // 4) % 4]
    if i % 4 == 0:
        for m in c[:2]: add(mus, piano(m - 12, 4.5, .06), tb)
    add(mus, piano(c[(i * 2) % 4] + 12, 2.4, .04), tb); add(mus, piano(c[(i * 2 + 1) % 4] + 12, 2.4, .028), tb + beat / 2)
    if tb > T['s6']:   # soft heartbeat pulse
        s_ = tt(.35); kk = np.sin(2 * np.pi * np.cumsum(45 + 60 * np.exp(-s_ * 30)) / SR) * np.exp(-s_ * 9)
        add(mus, kk, tb, .12 + .1 * cl_env[0] if False else .12 + .08 * min(1, (tb - T['s6']) / 12))
    i += 1
pad = z()
for m in (53, 60, 64, 69, 72): pad += np.sin(2 * np.pi * mid(m) * t) + np.sin(2 * np.pi * mid(m) * 1.003 * t)
pad_env = seg(T['s5'], T['dana'] - .2, 2.5, .3) * (0.6 + .4 * np.clip((t - T['s6']) / 12, 0, 1))
mus += lp(pad, 1200) * .010 * pad_env
# punchline: music drops out on Dana's line, returns with the resolve
for m in (41, 53, 60, 64, 69, 72, 76): add(mus, piano(m, 6, .055), T['dana'] + D['dana'] + .25)
add(mus, lp(pad, 1500) * .012 * seg(T['dana'] + D['dana'] + .25, DUR - .2, 1.5, 2.5), 0)
for m in (65, 72, 77): add(mus, piano(m, 3.5, .05), T['logo'])
s = tt(2.5); add(mus, np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-s * 6)) / SR) * np.exp(-s * 1.6) * .25, T['logo'])   # sub under logo
mus = reverb(mus, 2.2, 5000, .3)
# ======================= MIX =======================
venv = np.abs(vo + fx * (t > T['ivr']) * (t < T['ivr'] + D['ivr'] + .5)); k = int(.25 * SR); venv = np.convolve(venv, np.ones(k) / k, 'same')
duck = 1 - .5 * np.clip(venv / .04, 0, 1)
fade = np.clip(t / .6, 0, 1) * np.clip((DUR - t) / 1.0, 0, 1)
mix = (vo * 1.0 + amb * .9 * duck + fx * .85 + mus * 1.0 * duck) * fade
mix = np.tanh(mix * 1.15) / np.tanh(1.15); mix /= np.max(np.abs(mix)) / .9
Lc = mix + .025 * np.roll(amb * duck * fade, 500); Rc = mix + .025 * np.roll(amb * duck * fade, -500)
st = np.stack([Lc, Rc], 1); st /= np.max(np.abs(st)) / .9
sf.write('film_audio.wav', st, SR, subtype='PCM_16')
m = vo != 0; r = lambda x: 20 * np.log10(np.sqrt(np.mean(x[m] ** 2)) + 1e-9)
print('VO', round(r(vo), 1), 'amb', round(r(amb * .9 * duck), 1), 'music', round(r(mus * duck), 1), 'fx', round(r(fx * .85), 1))
for a, b, n in ((0, 6.6, 'night'), (6.6, 18.8, 'kitchen1'), (22.3, 23.3, 'SILENCE'), (33, 47, 'kitchen2'), (54, 60, 'end')):
    x = st[int(a * SR):int(b * SR), 0]; print(n, round(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9), 1))
