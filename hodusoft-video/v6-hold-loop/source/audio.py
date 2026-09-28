import numpy as np, json, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
SR=44100; TL=json.load(open('timeline.json')); TM=TL['timing']; TT=TL['TT']; DU=TL['dur']; L=TM['L']; D=TM['D']; DUR=TM['end']; N=int(SR*DUR)
rng=np.random.default_rng(5)
z=lambda:np.zeros(N)
def add(b,s,t0,g=1.0):
    i=int(t0*SR); j=min(N,i+len(s))
    if 0<=i<N: b[i:j]+=s[:j-i]*g
def bp(x,lo,hi,o=4): return sosfilt(butter(o,[lo,hi],'band',fs=SR,output='sos'),x)
def lpf(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hpf(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def tt(d): return np.arange(int(d*SR))/SR
noise=lambda n:rng.standard_normal(n)
mid=lambda m:440*2**((m-69)/12)
def tone(f,d,dec=6,a=.004,h=(1,.3,.1)):
    t=tt(d); return sum(g*np.sin(2*np.pi*f*(k+1)*t) for k,g in enumerate(h))*np.exp(-t*dec)*np.minimum(1,t/a)
# ---------- VO ----------
def load(f):
    a,sr=sf.read(f); a=resample_poly(a,SR,sr) if sr!=SR else a; return a/np.max(np.abs(a))
vo=z(); ivr=z()
iv=load('vo/IVR.wav'); iv=bp(iv,320,3300,3); iv=np.tanh(iv*2.2)/np.tanh(2.2); add(ivr,iv,TM['ivr'],.55)
for f,t0 in [('L0',L[0]),('L1',L[1]),('L2',L[2]),('loop',TT['loopVO']),('freeze',TT['frzVO']),('meet',L[3]),('fix',TT['fixVO']),('e1',L[12]),('e2',L[13]),('cta',TT['ctaVO'])]: add(vo,load(f'vo/{f}.wav'),t0,.9)
# presence / de-mud on VO
vo=vo+0.25*hpf(vo,2500)-0.15*lpf(vo,180)
env=np.abs(vo); k=int(.08*SR); env=np.convolve(env,np.ones(k)/k,'same'); k2=int(.25*SR); env=np.convolve(env,np.ones(k2)/k2,'same'); duck=1-0.8*np.clip(env/0.04,0,1)
# ---------- HOLD MUZAK 0 - 3.55 ----------
DROP=3.55; hold=z(); bpm=108; b=60/bpm
mel=[72,76,79,76,74,77,81,77,72,76,79,84,83,79,76,74]
for i,m in enumerate(mel):
    t0=0.05+i*b/2
    if t0>DROP: break
    add(hold,tone(mid(m),b/2*1.6,5,.01,(1,.5,.2,.1)),t0,.22)
for i,(c) in enumerate([[60,64,67],[62,65,69],[60,64,67],[59,62,67]]):
    t0=i*b*2
    if t0>DROP: break
    for m in c: add(hold,tone(mid(m-12),b*2,1.5,.02,(1,.2)),t0,.12)
t=np.arange(N)/SR; wob=np.sin(2*np.pi*.7*t)*.0025
idx=np.clip((t*(1+wob))*SR,0,N-1).astype(int); hold=hold[idx]
hold=bp(hold,400,3000,3)*1.6; hold[int(DROP*SR):]=0
# ---------- SFX ----------
fx=z()
def busy():
    x=np.zeros(int(.75*SR))
    for k in range(3):
        s=tt(.14); b_=(np.sin(2*np.pi*480*s)+np.sin(2*np.pi*620*s))*np.minimum(1,s/.004)*np.minimum(1,(.14-s)/.004)
        add_=int(k*.25*SR); x[add_:add_+len(b_)]+=b_
    return bp(x,300,3400,2)*.28
def click(g=.3,f=3000): n=int(.015*SR); s=np.arange(n)/SR; return hpf(noise(n),f)*np.exp(-s*500)*g
def blip(f,d=.08,g=.15): return tone(f,d*3,3/d,.002,(1,))*g
def whoosh(d,g=.3,f0=300,f1=6000,up=True):
    s=tt(d); k=s/d; e=np.sin(np.pi*k)**2 if not up else k**2*np.minimum(1,(1-k)/.06)
    y=noise(len(s)); out=np.zeros(len(s)); seg=int(.02*SR)
    for a in range(0,len(s),seg):
        fc=f0+(f1-f0)*(k[a] if up else 1-k[a]); out[a:a+seg]=lpf(y[max(0,a-500):a+seg],max(80,fc))[-len(out[a:a+seg]):]
    return out*e*g*2
def impact(g=1):
    s=tt(1.8); f=38+100*np.exp(-s*12); x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-s*2.2)
    return (np.tanh(x*2.5)*.8+lpf(noise(len(s)),2500)*np.exp(-s*7)*.4)*g
def dtmf(d,dur=.1,g=.12):
    lo={'1':697,'2':697,'3':697,'4':770,'5':770,'6':770,'7':852,'8':852,'9':852,'0':941}[d];hi={'1':1209,'2':1336,'3':1477,'4':1209,'5':1336,'6':1477,'7':1209,'8':1336,'9':1477,'0':1336}[d]
    s=tt(dur); return (np.sin(2*np.pi*lo*s)+np.sin(2*np.pi*hi*s))*np.minimum(1,s/.004)*np.minimum(1,(dur-s)/.006)*g
def chime(ms,g=.14,d=1.0): return sum(tone(mid(m),d,4,.003,(1,.25,.08)) for m in ms)*g
def drop_blip(): s=tt(.18); f=700*np.exp(-s*9)+120; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-s*14)*.14
def static(d,g=.12): s=tt(d); return bp(noise(len(s)),800,9000,2)*g*np.minimum(1,s/.05)*np.minimum(1,(d-s)/.1)
def riser(d,g=.3): s=tt(d); k=s/d; return (hpf(noise(len(s)),200)*.5*k**3 + np.sin(2*np.pi*np.cumsum(150+1200*k**2)/SR)*.25*k**2)*g

t=np.arange(N)/SR
LAPS=[1.5,1.25,1.02,.84,.7,.58]; lapStart=[]; a=TT['laps']
for d_ in LAPS: lapStart.append(a); a+=d_
FRZ=TT['frz']; B0=L[3]-.25; B1=L[4]-.12; FIX=TT['fix0']
# ---------------- SFX ----------------
add(fx,click(.4,1500),DROP); add(fx,busy(),DROP+.08)
add(fx,lpf(noise(int(.3*SR)),400)*np.exp(-tt(.3)*10)*.5,DROP)
for j in range(27): add(fx,drop_blip(),L[0]+.25+j*(D[0]-.1)/27, .7+.3*rng.random())
for i in range(6): add(fx,blip(500+i*80,.05,.14),L[1]+i*.12); add(fx,click(.15,1500),L[1]+i*.12)
tq=L[1]+.7
while tq<L[2]-.1: add(fx,click(.25,2500),tq); add(fx,blip(1800,.02,.05),tq); tq+=.22
add(fx,static(1.2,.10),L[2])
for i in range(9): add(fx,blip(220,.06,.12),L[2]+.9+i*.11)
# loop: dot launch, a whoosh per lap (shorter + higher each lap), an alarm stab per damage item
add(fx,whoosh(.5,.25,300,5000),L[2]+D[2]-.2)
for i,(s0,d) in enumerate(zip(lapStart,LAPS)):
    add(fx,whoosh(d*.95,.18+.03*i,400+200*i,5000+800*i,False),s0)
    ta=s0+d*.3; add(fx,impact(.25+.06*i),ta); add(fx,tone(mid(76+i),.25,9,.002,(1,.5,.25))*.12,ta)
    add(fx,tone(mid(88+i),.12,20,.002,(1,))*.08,ta+.05)
add(fx,riser(FRZ-lapStart[3],.35),lapStart[3])
# freeze: hard stop + tinnitus ring
add(fx,lpf(noise(int(.15*SR)),600)*np.exp(-tt(.15)*25)*.6,FRZ)
ring_=np.sin(2*np.pi*3800*tt(1.6))*np.exp(-tt(1.6)*1.4)*.035; add(fx,ring_,FRZ)
# heartbeat into the reveal
for k,tb in enumerate([B0-1.0,B0-.72,B0-.35]):
    s_=tt(.25); hb=np.sin(2*np.pi*np.cumsum(55+40*np.exp(-s_*25))/SR)*np.exp(-s_*14); add(fx,hb,tb,.55)
add(fx,riser(.9,.3),B0-.9)
add(fx,impact(1.0),B0); add(fx,whoosh(.5,.25,4000,200,False),B0)
add(fx,tone(1000,.25,14,.002,(1,.15))*.22,B0+.6)
# fix: unravel sweep, dot zips, flip clicks with rising pitch
add(fx,whoosh(1.0,.25,300,7000),FIX)
add(fx,chime([84,91],.12,.9),FIX+1.0)
for i in range(6):
    tf=TT['flip0']+i*.55; add(fx,click(.35,2000),tf); add(fx,blip(mid(79+[0,2,4,7,9,12][i]),.05,.13),tf+.16)
add(fx,chime([76,83,88],.1,1.2),TT['flip0']+5*.55+.25)
# end: rewind + connect + final
s0=L[12]
for k in range(40): add(fx,blip(2000-k*35+rng.random()*200,.012,.05),s0+k*.025)
add(fx,whoosh(1.0,.15,6000,500,False),s0)
add(fx,chime([76,83],.13,1.0),s0+1.0)
endT=L[13]+.75+.25
add(fx,impact(.7),endT); add(fx,chime([69,76,81,88],.08,1.6),endT)
add(fx,blip(700,.06,.14),endT+.25)
# ---------------- MUSIC ----------------
mus=z(); kickenv=z()
def kick():
    s=tt(.45); f=42+120*np.exp(-s*30); return np.tanh(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-s*6)*1.8)
KICK=kick()
def hat(o=False): n=int((.16 if o else .04)*SR); s=np.arange(n)/SR; return hpf(hpf(noise(n),7000),7000)*np.exp(-s*(20 if o else 100))*.3
HAT,OHAT=hat(),hat(True)
def clap():
    s=tt(.22); e=np.exp(-s*28)
    for dd in (0,.01,.02): e=e+np.where(s>dd,np.exp(-(s-dd)*140),0)*.5
    return bp(noise(len(s)),900,6000,2)*e*.5
CLAP=clap()
# pain section: low drone + slow pulse
n_=int((L[2]+D[2]+.1-4.0)*SR); s=np.arange(n_)/SR
drone=(np.sin(2*np.pi*mid(33)*s)+.5*np.sin(2*np.pi*mid(45)*s*1.003))*np.minimum(1,s/1.2)
add(mus,lpf(drone,400)*.2,4.0)
for tb in np.arange(4.3,L[2]+D[2],.5): add(mus,KICK,tb,.3); add(kickenv,np.exp(-tt(.3)*12),tb)
# loop: pulse locked to laps, 4 kicks per lap -> accelerating; bass on each hit; hats double later
for i,(s0,d) in enumerate(zip(lapStart,LAPS)):
    for q in range(4):
        tb=s0+q*d/4; add(mus,KICK,tb,.75+.04*i); add(kickenv,np.exp(-tt(.3)*12),tb)
        f=mid(33+[0,0,3,5,7,8][i]); sb=tt(d/4); add(mus,lpf(np.sign(np.sin(2*np.pi*f*sb))*.5+np.sin(2*np.pi*f/2*sb),600)*np.exp(-sb*4)*.2,tb)
        for h in range(2 if i<3 else 4): add(mus,HAT,tb+h*d/(4*(2 if i<3 else 4)),.55)
        if q%2==1: add(mus,CLAP,tb,.5)
# rising string cluster over the loop
cl_=z()
for m in (57,58,64,65,69):
    cl_+=lpf((2*((mid(m)*t)%1)-1)+(2*((mid(m)*1.006*t)%1)-1),1500)*.5
env_c=np.clip((t-TT['laps'])/(FRZ-TT['laps']),0,1)**2*(t<FRZ)
mus+=cl_*.02*env_c
# groove from the reveal to the end (v3 groove)
CH=[[57,60,64],[53,57,60],[48,55,64],[55,59,62]]; ROOT=[45,41,36,43]; beat=.5
k=0
while True:
    tb=B0+k*beat
    if tb>DUR-.9: break
    bar=(k//4)%4; sub=k%4
    add(mus,KICK,tb,.9); add(kickenv,np.exp(-tt(.3)*12),tb)
    if sub in (1,3): add(mus,CLAP,tb,.55)
    add(mus,HAT,tb+beat/2,.9); add(mus,HAT,tb+beat/4,.35); add(mus,HAT,tb+3*beat/4,.35)
    for h in range(2):
        f=mid(ROOT[bar]+(12 if h else 0)); s_=tt(beat/2); x=np.sign(np.sin(2*np.pi*f*s_))*.5+np.sin(2*np.pi*f/2*s_)
        add(mus,lpf(x,700)*np.exp(-s_*5)*np.minimum(1,s_/.004)*.22,tb+h*beat/2)
    for q in range(2):
        m=CH[bar][(k*2+q)%3]+12; add(mus,tone(mid(m),.3,11,.002,(1,.4,.15))*.07,tb+q*beat/2)
    if sub==0:
        s_=tt(beat*4); pad=sum(np.sin(2*np.pi*mid(m)*s_*(1+d_)) for m in CH[bar] for d_ in (-.003,.003))
        add(mus,lpf(pad,1200)*np.minimum(1,s_/.3)*np.minimum(1,(beat*4-s_)/.2)*.035,tb)
    k+=1
s_=tt(1.6); add(mus,sum(np.sin(2*np.pi*mid(m)*s_) for m in [45,57,60,64,69])*np.exp(-s_*1.8)*.06,endT)
# freeze: music cut to silence until the heartbeat
mute=np.ones(N); mute[(t>=FRZ)&(t<B0)]=0.0
music=mus*(1-.5*np.clip(kickenv,0,1))*mute
# ---------------- MIX ----------------
full=vo*1.0+ivr*1.0+hold*.55+music*.3*duck+fx*.55*(1-.35*(1-duck))
fo=int(.4*SR); full[-fo:]*=np.linspace(1,0,fo)**2
full=np.tanh(full*1.1)/np.tanh(1.1); full/=np.max(np.abs(full))/.9
sf.write('audio.wav',np.stack([full,full],1),SR,subtype='PCM_16')
m=vo!=0; r=lambda x:20*np.log10(np.sqrt(np.mean(x[m]**2))+1e-9)
print('VO',round(r(vo),1),'music',round(r(music*.3*duck),1),'fx',round(r(fx*.55),1))
for a_,b_,n in ((0,4,'hook'),(4,10.8,'pain'),(11.3,17.3,'loop'),(17.35,18.3,'freeze'),(19,21,'reveal'),(21,26,'fix'),(26,32,'end')):
    x=full[int(a_*SR):int(b_*SR)]; print(n,round(20*np.log10(np.sqrt(np.mean(x**2))+1e-9),1))
