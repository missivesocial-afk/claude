import numpy as np, wave
SR=44100; DUR=28.0; N=int(SR*DUR)
rng=np.random.default_rng(3)
def z(): return np.zeros(N)
def env(n,a=0.005,d=0.2,sus=0.0,rel=0.05):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))*np.exp(-t/max(d,1e-4))
    return e
def add(buf,sig,t0,g=1.0):
    i=int(t0*SR); j=min(N,i+len(sig))
    if i<N: buf[i:j]+=sig[:j-i]*g
def lp(x,fc):  # one-pole lowpass, fc scalar or array
    a=np.exp(-2*np.pi*np.asarray(fc)/SR)*np.ones(len(x)); y=np.zeros_like(x); s=0.0
    for k in range(len(x)): s=(1-a[k])*x[k]+a[k]*s; y[k]=s
    return y
def lpf(x,fc,order=2):
    for _ in range(order): x=lp(x,fc)
    return x
def hp(x,fc): return x-lpf(x,fc,1)
def noise(n): return rng.standard_normal(n)
def saw(f,n,ph=0): t=np.arange(n)/SR; return 2*((f*t+ph)%1)-1
def sine(f,n): t=np.arange(n)/SR; return np.sin(2*np.pi*np.cumsum(np.ones(n)*f)/SR) if np.isscalar(f) else np.sin(2*np.pi*np.cumsum(f)/SR)
mid=lambda m:440*2**((m-69)/12)
BPM=120; B=60/BPM
# ---------------- MUSIC ----------------
drums=z(); bass=z(); pad=z(); pl=z(); kickenv=z()
def kick(g=1):
    n=int(.4*SR); t=np.arange(n)/SR; f=45+110*np.exp(-t*28); s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7)
    s+=0.4*noise(n)*np.exp(-t*300)*.3; return np.tanh(s*1.6)*g
def clap():
    n=int(.25*SR); t=np.arange(n)/SR; e=np.exp(-t*25)
    for d in (0.0,0.011,0.022): e+=np.where(t>d,np.exp(-(t-d)*120),0)*.6
    x=hp(noise(n),900); return lpf(x,5000,1)*e*.5
def hat(open_=False):
    n=int((.18 if open_ else .05)*SR); t=np.arange(n)/SR; x=hp(hp(noise(n),6000),6000); return x*np.exp(-t*(18 if open_ else 90))*.35
KICK=kick(); CLAP=clap(); HAT=hat(); OHAT=hat(True)
CH={'Am':[57,60,64,69],'F':[53,57,60,65],'C':[48,55,60,64],'G':[55,59,62,67]}
ROOT={'Am':45,'F':41,'C':36,'G':43}
PROG=['Am','F','C','G']
def section(t):
    if t<4: return 'intro'
    if t<21: return 'main'
    if t<23.5: return 'break'
    return 'outro'
# drums
for i in range(int(DUR/B*4)):
    t=i*B/4; sec=section(t); beat=i//4; sub=i%4
    if t>=27.5: break
    if sec=='intro':
        if sub==0 and t>=2.0: add(drums,HAT,t,.35+.2*(t-2))
        continue
    if sec in('main','outro'):
        if sub==0: add(drums,KICK,t,.95); add(kickenv,np.exp(-np.arange(int(.3*SR))/SR*12),t)
        if sub==0 and beat%2==1: add(drums,CLAP,t,.8)
        if sub==2: add(drums,OHAT,t,.5)
        elif sub in(1,3): add(drums,HAT,t,.45)
        if 20.5<=t<21 and sub%1==0: add(drums,CLAP,t,.35+.8*(t-20.5))  # fill
    if sec=='break':
        if sub==0 and beat%2==0 and t<22.8: add(drums,KICK,t,.7); add(kickenv,np.exp(-np.arange(int(.3*SR))/SR*12),t)
        if sub in(1,3): add(drums,HAT,t,.3)
        if t>=22.75: add(drums,CLAP,t,.15+.6*(t-22.75)/0.75)
# harmony
def chord_at(t):
    if t<4: return 'Am'
    return PROG[int((t-4)//2)%4]
bar_ts=np.arange(0,28,2.0)
for bt in bar_ts:
    c=chord_at(bt+0.01); n=int(2.0*SR); tt=np.arange(n)/SR
    # pad: detuned saws
    s=np.zeros(n)
    for m in CH[c]:
        for det in (-0.08,0.0,0.08): s+=saw(mid(m+12)*2**(det/12),n,rng.random())
    a=np.minimum(1,tt/0.25)*np.minimum(1,(2.0-tt)/0.1+0.0)
    cut=1400 if bt>=4 else 500+ (bt/4)*900
    add(pad,lpf(s,cut,2)*a*.05,bt)
    if bt>=4 and bt<27.5 and not (21<=bt<23):
        # bass 8ths
        for k in range(8):
            t0=bt+k*B/2; nn=int(B/2*SR); tb=np.arange(nn)/SR
            f=mid(ROOT[c]+(12 if k%2 else 0)); x=saw(f,nn)+0.5*np.sin(2*np.pi*f/2*tb)
            add(bass,lpf(x,900,2)*np.exp(-tb*6)*np.minimum(1,tb/.004)*.32,t0)
    if bt>=4 and bt<27.5:
        # pluck arp 8ths
        pat=[0,1,2,3,2,1,3,2] if bt%4 else [0,2,1,3,1,2,3,0]
        for k in range(8):
            t0=bt+k*B/2
            if 21<=t0<23.5 and k%2: continue
            m=CH[c][pat[k]]+24 - (12 if CH[c][pat[k]]>62 else 0); nn=int(.4*SR); tp=np.arange(nn)/SR; f=mid(m)
            x=(np.sin(2*np.pi*f*tp)+.35*np.sin(2*np.pi*2*f*tp)+.12*np.sin(2*np.pi*3*f*tp))*np.exp(-tp*9)*np.minimum(1,tp/.003)
            add(pl,x*.11,t0)
# intro: sub drone + tension riser
n=int(4*SR); tt=np.arange(n)/SR
add(pad,np.sin(2*np.pi*mid(33)*tt)*.18*np.minimum(1,tt/1)*(1-np.clip((tt-3.7)/.3,0,1)),0)
# delay on plucks
d=int(B*0.75*SR); pl2=pl.copy(); pl2[d:]+=pl[:-d]*.35; pl2[2*d:]+=pl[:-2*d]*.15; pl=pl2
duck=1-0.6*np.clip(kickenv,0,1)
music=drums*0.9+bass*duck+pad*duck*1.1+pl*duck
# ---------------- SFX ----------------
fx=z()
def ring(dur=.55):
    n=int(dur*SR); t=np.arange(n)/SR; am=(np.sin(2*np.pi*22*t)>0).astype(float)*.7+.3
    x=(np.sin(2*np.pi*440*t)+np.sin(2*np.pi*480*t)+.3*np.sin(2*np.pi*960*t))*am
    return x*np.minimum(1,t/.01)*np.minimum(1,(dur-t)/.04)*.22
def thud():
    n=int(.3*SR); t=np.arange(n)/SR; f=70+120*np.exp(-t*40); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*12)*.7+lpf(noise(n),2000,1)*np.exp(-t*40)*.25
def blip(f=1800,d=.06,g=.18):
    n=int(d*SR*3); t=np.arange(n)/SR; return np.sin(2*np.pi*f*t)*np.exp(-t/d*3)*g
def pop(f=600,g=.35):
    n=int(.12*SR); t=np.arange(n)/SR; fr=f*(1+2*np.exp(-t*60)); return np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-t*35)*g
def whoosh(d=.45,up=True,g=.35,f0=300,f1=4000):
    n=int(d*SR); t=np.arange(n)/SR; k=t/d; e=np.sin(np.pi*k)**2 if not up else k**2*np.minimum(1,(1-k)/.08)
    fc=f0+(f1-f0)*(k if up else 1-k)*1.0; return lpf(noise(n),fc,2)*e*g*2.2
def swoosh(d=.35,g=.3):
    n=int(d*SR); t=np.arange(n)/SR; k=t/d; e=np.sin(np.pi*k)**3; fc=500+5000*np.sin(np.pi*k)
    return hp(lpf(noise(n),fc,2),300)*e*g*2
def slide(f0,f1,d,g=.2):
    n=int(d*SR); t=np.arange(n)/SR; f=f0*(f1/f0)**(t/d); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.minimum(1,t/.01)*np.minimum(1,(d-t)/.05)*g
def chime(fs,g=.18,d=.9):
    n=int(d*SR); t=np.arange(n)/SR; x=sum(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2.01*f*t) for f in fs)
    return x*np.exp(-t*4)*np.minimum(1,t/.004)*g
def dtmf(k,d=.16,g=.16):
    lo={'1':697,'2':697,'3':697,'4':770,'5':770,'6':770,'7':852,'8':852,'9':852,'0':941}[k]; hi={'1':1209,'2':1336,'3':1477,'4':1209,'5':1336,'6':1477,'7':1209,'8':1336,'9':1477,'0':1336}[k]
    n=int(d*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*lo*t)+np.sin(2*np.pi*hi*t))*np.minimum(1,t/.005)*np.minimum(1,(d-t)/.01)*g
def click(g=.12):
    n=int(.02*SR); t=np.arange(n)/SR; return hp(noise(n),2500)*np.exp(-t*400)*g
def impact(g=1):
    n=int(1.6*SR); t=np.arange(n)/SR; f=40+90*np.exp(-t*10); b=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.2)
    return (np.tanh(b*2)*.8+lpf(noise(n),3000,1)*np.exp(-t*6)*.35)*g
def riser(d,g=.3):
    n=int(d*SR); t=np.arange(n)/SR; k=t/d; return (lpf(noise(n),300+8000*k**2,2)*1.5+ .3*np.sin(2*np.pi*np.cumsum(200+900*k**2)/SR))*k**2.2*g
def boing(g=.3):
    n=int(.5*SR); t=np.arange(n)/SR; f=300+220*np.sin(2*np.pi*14*t)*np.exp(-t*6); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6)*g
# S1
for i,t0 in enumerate([.3,1.1,1.9]): add(fx,ring(),t0); add(fx,thud(),t0,.8)
add(fx,pop(500,.3),1.5)
for k in range(2,13): add(fx,blip(1500+k*40,.04,.12),1.9+ (k-1)/12*1.1)
add(fx,slide(900,260,.4,.16),3.15)
add(fx,riser(.9,.35),3.1); add(fx,whoosh(.4,True,.4),3.7)
add(fx,impact(.8),4.0)
# S2 chips
for k in range(10): add(fx,pop(420+k*55,.22),4.1+k*.06)
add(fx,slide(180,1400,.6,.12),5.95); add(fx,whoosh(.6,True,.45,200,6000),5.95)
add(fx,pop(160,.55),6.62); add(fx,chime([mid(76),mid(81)],.12),7.0)
for i in range(5): add(fx,click(.2),7.1+i*.11); add(fx,blip(1200+i*120,.03,.06),7.1+i*.11)
add(fx,chime([mid(84),mid(88)],.14,.7),8.15)
for tt in (8.8,11.8,14.8,17.8): add(fx,swoosh(.38,.32),tt)
# S4
add(fx,blip(1000,.12,.1),9.3)
for i in range(3): add(fx,pop(700+i*90,.16),9.6+i*.1)
add(fx,dtmf('2',.18,.2),10.2); add(fx,slide(600,1500,.3,.07),10.4)
add(fx,chime([mid(79),mid(84)],.14,.8),10.75)
# S5
digs='4071938265'
for i in range(10):
    ta=12.25+i*.26
    if ta>14.85: break
    add(fx,dtmf(digs[i],.07,.1),ta); add(fx,dtmf(digs[(i+3)%10],.06,.08),ta+.09)
    add(fx,pop(900 if ST!=0 else 800,.12),ta+.45) if False else add(fx,pop(850,.12),ta+.45)
# S6
add(fx,pop(900,.22),15.35); add(fx,pop(650,.22),16.15); add(fx,pop(900,.22),16.6); add(fx,pop(650,.22),17.25)
for tt in np.arange(15.65,16.1,.07): add(fx,click(.08),tt)
for tt in np.arange(16.85,17.2,.07): add(fx,click(.08),tt)
add(fx,chime([mid(88)],.08,.5),17.3)
# S7
for i in range(7): add(fx,blip(mid(72+[0,2,4,5,7,9,12][i]),.05,.11),18.4+i*.09)
add(fx,slide(300,1200,1.1,.05),18.9)
# S8
add(fx,whoosh(.5,False,.45,200,3000),20.75); add(fx,impact(.5),21.2)
for k in range(24): add(fx,click(.1),21.3+ (1-(1-k/24)**(1/3))*1.1)
add(fx,chime([mid(81),mid(88)],.15,.9),22.4)
for i in range(3): add(fx,pop(600+i*120,.22),22.3+i*.1)
add(fx,riser(1.0,.4),22.5)
# S9
add(fx,impact(1.0),23.5); add(fx,chime([mid(69),mid(76),mid(81),mid(88)],.1,1.6),23.5)
add(fx,boing(.28),23.55)
for i in range(8): add(fx,pop(500+i*60,.12),23.6+i*.05)
for i in range(8): add(fx,click(.12),24.15+i*.05)
add(fx,swoosh(.4,.2),24.75)
add(fx,pop(520,.3),25.2); add(fx,chime([mid(84),mid(91)],.12,1.0),25.4)
add(fx,blip(2400,.03,.05),25.1); add(fx,blip(2400,.03,.05),27.2)
# final chord hit
n=int(0.9*SR); tt=np.arange(n)/SR
fin=sum(saw(mid(m+12),n) for m in [48,55,60,64]); add(music,lpf(fin,2500,2)*np.exp(-tt*3)*.07,27.5); add(music,KICK,27.5,.9)
# ---------------- MIX ----------------
mix=music*0.62+fx*0.9
fade=np.ones(N); fo=int(.35*SR); fade[-fo:]=np.linspace(1,0,fo)**2; mix*=fade
mix=np.tanh(mix*1.25)/np.tanh(1.25)
mix/=np.max(np.abs(mix))/0.89
# stereo: slight width via delayed copy on pad
L=mix.copy(); R=mix.copy(); w=pad*duck*0.07; R[300:]+=w[:-300]; L+=w
st=np.stack([L,R],1); st/=np.max(np.abs(st))/0.89
with wave.open('soundtrack.wav','wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((st*32767).astype('<i2').tobytes())
print('ok',st.shape)
