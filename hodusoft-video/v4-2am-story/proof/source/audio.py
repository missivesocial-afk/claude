import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly, fftconvolve
SR = 44100; DUR = 27.0; N = int(SR * DUR)
rng = np.random.default_rng(7)
T = dict(pa=1.0, notif=2.4, shotB=5.0, type2=5.7, send=6.05, sys=6.45, shotC=7.2, card=7.35, click=8.8, split=9.15,
         accept=9.8, luis=10.2, seats=14.3, wheel=17.1, bp=18.7, emma=19.6, bpNotif=20.3, die=22.3, sup=23.2, logo=24.7)
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
    y = fftconvolve(x, ir)[:len(x)]; return x * (1 - wet) + y * wet
def env_seg(a, b, fade=.25):  # 1 inside [a,b] with fades
    t = np.arange(N) / SR; e = np.clip((t - a) / fade, 0, 1) * np.clip((b - t) / fade, 0, 1); return e

# ---------------- AIRPORT (Emma's world) ----------------
air = z()
air += lp(noise(N), 350) * .05 + bp(noise(N), 80, 200) * .05                       # HVAC / hall rumble
bab = z()
for rep in range(3):
    for i in range(12):
        a = load(f'vo/bab{i}.wav', .5); a = lp(bp(a, 200, 3500), 2500)
        add(bab, a, rng.uniform(-1, DUR - 1), rng.uniform(.25, .6))
bab = reverb(bab, 1.6, 2500, .55) * .55
air += bab
for k in range(8):                                                                   # rolling suitcase passes
    t0 = rng.uniform(0, 20); d = rng.uniform(1.8, 3.2); s = tt(d); clicks = np.zeros(len(s))
    for c in np.arange(0, d, rng.uniform(.09, .13)):
        i = int(c * SR); clicks[i:i + 200] += noise(200) * np.exp(-np.arange(200) / 30)
    add(air, lp(clicks, 1800) * np.sin(np.pi * s / d) ** 2 * .12, t0)
# PA: chime + reverberant announcement
chime = np.concatenate([np.sin(2 * np.pi * mid(m) * tt(.55)) * np.exp(-tt(.55) * 4) for m in (76, 72, 67)])
pa = z(); add(pa, chime * .25, T['pa'] - .75)
add(pa, bp(load('vo/pa.wav', .55), 250, 5000), T['pa'] + .3)
pa = reverb(pa, 2.4, 3500, .5)
# ---------------- KITCHEN (Luis's world) ----------------
kit = z(); t = np.arange(N) / SR
kit += (np.sin(2 * np.pi * 60 * t) * .012 + np.sin(2 * np.pi * 120 * t) * .008) + lp(noise(N), 500) * .02
# ---------------- world mix by shot ----------------
e_air = np.clip(1 - env_seg(T['shotC'], T['split'], .05), 0, 1)
e_air = np.where(t < T['split'], e_air, .45)                     # split: both worlds, quieter
e_kit = env_seg(T['shotC'], 99, .05); e_kit = np.where(t >= T['split'], .6, e_kit)
cut = (t < T['die']).astype(float)                                # phone dies -> silence
room = (air * e_air + pa * np.where(t < T['split'], 1, .5) + kit * e_kit) * cut
# ---------------- SFX ----------------
fx = z()
def ding(ms, g=.18, d=.9): return sum(np.sin(2 * np.pi * mid(m) * tt(d)) * np.exp(-tt(d) * 5) + .2 * np.sin(4 * np.pi * mid(m) * tt(d)) * np.exp(-tt(d) * 9) for m in ms) * g
def buzz(d=.35): s = tt(d); return np.sin(2 * np.pi * 170 * s) * (np.sin(2 * np.pi * 7 * s) > 0) * .18 * np.minimum(1, s / .01)
def click(g=.25, f=2500): n = int(.02 * SR); return hp(noise(n), f) * np.exp(-np.arange(n) / SR * 350) * g
def swoosh(d=.3, g=.12): s = tt(d); k = s / d; return bp(noise(len(s)), 1200, 7000) * np.sin(np.pi * k) ** 2 * g
add(fx, buzz(), T['notif']); add(fx, ding([83, 88], .16), T['notif'] + .02)
add(fx, click(.3, 3000), T['type2']); add(fx, swoosh(.35, .15), T['send']); add(fx, ding([88], .06, .4), T['sys'])
add(fx, ding([79, 84], .07, .6), T['card']); add(fx, click(.35, 1500), T['click'])
ring = np.concatenate([ding([m], .12, .16) for m in (79, 83, 86, 83)] * 2)                # original ringtone
add(fx, ring, T['click'] + .35); add(fx, buzz(.6), T['click'] + .35)
add(fx, click(.3, 1800), T['accept'])
for k in ('seats', 'wheel', 'bp'): add(fx, click(.25, 1500), T[k] - .02); add(fx, ding([88], .05, .35), T[k] + .05)
add(fx, buzz(), T['bpNotif']); add(fx, ding([83, 88], .14), T['bpNotif'] + .02)
add(fx, ding([76, 69], .12, .7), T['die'] - 1.2)                                          # low battery
add(fx, lp(noise(int(.12 * SR)), 300) * np.exp(-tt(.12) * 30) * .4, T['die'])            # phone dies
# ---------------- VOICES ----------------
vo = z()
luis = load('vo/luis.wav', .8); luis = reverb(luis, .35, 6000, .08); add(vo, luis, T['luis'])
emma = load('vo/emma.wav', .7); emma = reverb(bp(emma, 150, 7000), .5, 5000, .12); add(vo, emma, T['emma'])
# ---------------- SCORE: piano from the pickup ----------------
mus = z()
def piano(m, d=3.5, g=.1):
    s = tt(d); f = mid(m); x = sum(h * np.sin(2 * np.pi * f * (i + 1) * s * (1 + .0004 * i)) * np.exp(-s * (1.2 + i * .9)) for i, h in enumerate([1, .45, .22, .1, .05]))
    return x * np.minimum(1, s / .004) * g
CH = [[53, 60, 64, 69], [52, 59, 64, 67], [50, 57, 62, 65], [46, 58, 62, 65]]            # Fmaj7 - Em7 - Dm7 - Bbmaj7
beat = .75
for i in range(16):
    t0 = T['accept'] + .1 + i * beat
    if t0 > T['die'] - .2: break
    c = CH[(i // 4) % 4]
    if i % 4 == 0: [add(mus, piano(m - 12, 4, .07), t0) for m in c[:2]]
    add(mus, piano(c[(i * 2) % 4] + 12, 2.2, .045), t0); add(mus, piano(c[(i * 2 + 1) % 4] + 12, 2.2, .03), t0 + beat / 2)
pad = z(); s = np.arange(N) / SR
for m in (53, 60, 64, 69): pad += np.sin(2 * np.pi * mid(m) * s) + np.sin(2 * np.pi * mid(m) * s * 1.003)
pad = lp(pad, 900) * .012 * env_seg(T['accept'], T['die'], 1.5)
mus = reverb(mus, 2.0, 5000, .35) + pad
# end: resolve chord under the supers
for m in (41, 53, 60, 64, 69, 72): add(mus, piano(m, 4.5, .06), T['sup'])
add(mus, piano(77, 3.5, .05), T['logo'])
# low tension drone before pickup
dr = lp(noise(N), 120) * .06 * env_seg(0.3, T['accept'], 1.0); mus += dr
# ---------------- MIX ----------------
venv = np.abs(vo); k = int(.2 * SR); venv = np.convolve(venv, np.ones(k) / k, 'same'); duck = 1 - .45 * np.clip(venv / .05, 0, 1)
fade = np.clip(t / .8, 0, 1) * np.clip((DUR - t) / .8, 0, 1)
mix = (vo * 1.0 + room * .9 * duck + fx * .9 + mus * .9 * duck) * fade
mix = np.tanh(mix * 1.2) / np.tanh(1.2); mix /= np.max(np.abs(mix)) / .9
# gentle stereo: room slightly decorrelated
L = mix + .03 * np.roll(room * duck * fade, 400); R = mix + .03 * np.roll(room * duck * fade, -400)
st = np.stack([L, R], 1); st /= np.max(np.abs(st)) / .9
sf.write('proof_audio.wav', st, SR, subtype='PCM_16')
m = vo != 0; r = lambda x: 20 * np.log10(np.sqrt(np.mean(x[m] ** 2)) + 1e-9)
print('VO', round(r(vo), 1), 'room', round(r(room * .9 * duck), 1), 'music', round(r(mus * .9 * duck), 1))
