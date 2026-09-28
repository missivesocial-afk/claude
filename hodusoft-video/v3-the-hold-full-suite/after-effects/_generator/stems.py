import numpy as np, json, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
SR=44100; TM=json.load(open('timing.json')); L=TM['L']; D=TM['D']; DUR=TM['end']; N=int(SR*DUR)
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
for i in range(14): add(vo,load(f'vo/L{i}.wav'),L[i],.9)
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
# S1
add(fx,click(.4,1500),DROP); add(fx,busy(),DROP+.08)
add(fx,lpf(noise(int(.3*SR)),400)*np.exp(-tt(.3)*10)*.5,DROP)
for j in range(27): add(fx,drop_blip(),L[0]+.25+j*(D[0]-.1)/27, .7+.3*rng.random())
for i in range(6): add(fx,blip(500+i*80,.05,.14),L[1]+i*.12); add(fx,click(.15,1500),L[1]+i*.12)
tq=L[1]+.7
while tq<L[2]-.1: add(fx,click(.25,2500),tq); add(fx,blip(1800,.02,.05),tq); tq+=.22
add(fx,static(1.2,.10),L[2])
for i in range(9): add(fx,blip(220,.06,.12),L[2]+.9+i*.11)
B0=L[3]-.25
add(fx,riser(1.1,.35),B0-1.1)
add(fx,impact(1.0),B0); add(fx,whoosh(.5,.25,4000,200,False),B0)
add(fx,tone(1000,.25,14,.002,(1,.15))*.22,B0+.6)
def wt(lines,s0,d,off=0):
    ws=[w for l in lines for w in l.split(' ')]; wts=[len(w.split('|')[0])+2 for w in ws]; tot=sum(wts); acc=0; out=[]
    for w in wts: out.append(s0+off+(d-off)*.9*acc/tot); acc+=w
    return out
# slates
for st in (L[4]-.12,L[9]-.12,L[11]-.12):
    add(fx,whoosh(.45,.3,300,6000),st-.3); add(fx,impact(.55),st+.05); add(fx,hpf(noise(int(1.2*SR)),5000)*np.exp(-tt(1.2)*3)*.12,st+.05)
# F1 routing
s=L[5]
for k,dt in enumerate([0,.6,1.25]): add(fx,blip(900+k*200,.05,.13),s+dt)
add(fx,dtmf('2',.14,.14),s+.6); add(fx,whoosh(.55,.12,800,5000),s+.1); add(fx,whoosh(.55,.12,800,5000),s+.7)
add(fx,chime([79,84],.12,.9),s+1.85)
# F2 dialer
s=L[6]; digs='71935028461'
for k in range(12):
    t0=s+k*.25
    if t0>L[7]-.2: break
    add(fx,dtmf(digs[k%11],.06,.08),t0); add(fx,dtmf(digs[(k+4)%11],.06,.07),t0+.08)
for i in range(6): add(fx,blip(mid(76+[0,3,5,7,10,12][i]),.05,.10),s+.5+i*.28)
# F3 omni
s=L[7]; h6=wt(['Voice. WhatsApp.','Email. Chat.','one screen.'],L[7],D[7])
add(fx,whoosh(.6,.3,300,5000),s+.1); add(fx,impact(.35),s+.75); add(fx,blip(1400,.03,.1),s+.75)
for k in range(4): add(fx,blip(1100+k*120,.04,.1),h6[k]+.1)
add(fx,chime([84],.08,.6),h6[4]+.1)
# F4 AI scoring
h7=wt(['AI scores','every call.','Supervisors','see it live.'],L[8],D[8])
for i in range(9): add(fx,blip(mid(79+[0,2,4,7,9,12,14,16,19][i]),.03,.09),h7[1]+i*.11); add(fx,click(.1,4000),h7[1]+i*.11+.18)
for k in range(3): add(fx,blip(1250,.05,.1),h7[5]+k*.16)
# PBX tenants
s=L[9]+1.0; add(fx,impact(.3),s-.05)
for i in range(12): add(fx,blip(500+i*70,.04,.12),s+.1+i*.1); add(fx,click(.12,2500),s+.1+i*.1)
add(fx,chime([81,88],.1,.9),s+1.5)
# PBX features
h10=wt(['SIP trunking.','Auto provisioning.','call recording.'],L[10],D[10])
for k in range(10): add(fx,blip(1800+(k%3)*400,.015,.05),h10[0]+k*.07)
add(fx,whoosh(.4,.1,1000,6000),h10[0])
for i in range(6): add(fx,blip(1000+i*90,.03,.09),h10[2]+i*.1)
add(fx,blip(880,.12,.13),h10[4]); add(fx,blip(880,.12,.13),h10[4]+.2)
# BLAST
s=L[11]+.9; ts=s+.4
add(fx,click(.45,1200),ts-.1); add(fx,blip(600,.05,.15),ts-.1)
add(fx,impact(.8),ts); add(fx,whoosh(1.0,.28,6000,300,False),ts)
for k in range(60): add(fx,blip(2000+rng.random()*3000,.01,.035),ts+.05+k*.018+rng.random()*.02)
# END
s=L[12]
for k in range(40): add(fx,blip(2000-k*35+rng.random()*200,.012,.05),s+k*.025)
add(fx,whoosh(1.0,.15,6000,500,False),s)
add(fx,chime([76,83],.13,1.0),s+1.0)
endT=L[13]+.75+.25
add(fx,impact(.7),endT); add(fx,chime([69,76,81,88],.08,1.6),endT)
add(fx,blip(700,.06,.14),endT+.25)
# ---------- MUSIC ----------
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
# tension bed 4.1 -> B0: drone + ticking pulses at 120bpm grid anchored on B0
beat=.5; t0=B0-16*beat
dr_s=4.0; n=int((B0-dr_s)*SR); s=np.arange(n)/SR
drone=(np.sin(2*np.pi*mid(33)*s)+.5*np.sin(2*np.pi*mid(45)*s*1.003)+.25*np.sin(2*np.pi*mid(52)*s))*np.minimum(1,s/1.5)*(0.6+0.4*s/s[-1])
add(mus,lpf(drone,400)*.22,dr_s)
k=0
while t0+k*beat<B0-.01:
    tb=t0+k*beat
    if tb>=4.2:
        add(mus,KICK,tb,.35+.25*(tb-4.2)/(B0-4.2)); add(kickenv,np.exp(-tt(.3)*12),tb)
        add(mus,click(.12,5000),tb+beat/2)
    k+=1
# main groove B0 -> end
CH=[[57,60,64],[53,57,60],[48,55,64],[55,59,62]]; ROOT=[45,41,36,43]
nb=int((DUR-B0)/beat)+1
for k in range(nb):
    tb=B0+k*beat
    if tb>DUR-.9: break
    bar=(k//4)%4; sub=k%4
    add(mus,KICK,tb,.9); add(kickenv,np.exp(-tt(.3)*12),tb)
    if sub in (1,3): add(mus,CLAP,tb,.55)
    add(mus,HAT,tb+beat/2,.9); add(mus,HAT,tb+beat/4,.35); add(mus,HAT,tb+3*beat/4,.35)
    # bass 8ths
    for h in range(2):
        f=mid(ROOT[bar]+(12 if h else 0)); s=tt(beat/2); x=np.sign(np.sin(2*np.pi*f*s))*.5+np.sin(2*np.pi*f/2*s)
        add(mus,lpf(x,700)*np.exp(-s*5)*np.minimum(1,s/.004)*.22,tb+h*beat/2)
    # pluck arp 16ths every beat
    for q in range(2):
        m=CH[bar][(k*2+q)%3]+12; add(mus,tone(mid(m),.3,11,.002,(1,.4,.15))*.07,tb+q*beat/2)
    if sub==0:
        s=tt(beat*4); pad=sum(np.sin(2*np.pi*mid(m)*s*(1+d))  for m in CH[bar] for d in (-.003,.003))
        add(mus,lpf(pad,1200)*np.minimum(1,s/.3)*np.minimum(1,(beat*4-s)/.2)*.035,tb)
for st in (L[4]-.12,L[9]-.12,L[11]-.12): add(mus,hpf(noise(int(1.5*SR)),3000)*np.exp(-tt(1.5)*2.5)*.18,st+.05)
# final chord ring
s=tt(1.6); add(mus,sum(np.sin(2*np.pi*mid(m)*s) for m in [45,57,60,64,69])*np.exp(-s*1.8)*.06,endT)
sc=1-.5*np.clip(kickenv,0,1)
music=mus*sc

# ---------- STEMS (for After Effects) ----------
import os
os.makedirs('stems/vo',exist_ok=True)
full=vo*1.0+ivr*1.0+hold*.55+music*.5*duck+fx*.6*(1-.35*(1-duck))
fo=int(.4*SR); fade=np.ones(N); fade[-fo:]=np.linspace(1,0,fo)**2
G=.9/np.max(np.abs(np.tanh(full*fade*1.1)/np.tanh(1.1)))  # same loudness target as final mix
def w(name,x,stereo=True):
    x=np.clip(x*G,-1,1); sf.write(name,np.stack([x,x],1) if stereo else x,48000 if False else SR,subtype='PCM_24')
w('stems/01_music_ducked.wav',music*.5*duck*fade)
w('stems/02_sfx.wav',fx*.6*(1-.35*(1-duck))*fade)
w('stems/03_hold_music.wav',hold*.55)
w('stems/04_ivr_phone_voice.wav',ivr)
w('stems/05_voiceover_full.wav',vo)
# individual VO lines, same processing, trimmed to their own length
for i in range(14):
    a=load(f'vo/L{i}.wav')*.9; a=a+0.25*hpf(a,2500)-0.15*lpf(a,180)
    w(f'stems/vo/VO_{i+1:02d}.wav',a)
mix=np.tanh(full*fade*1.1)/np.tanh(1.1)*G
sf.write('stems/00_full_mix_reference.wav',np.stack([mix,mix],1),SR,subtype='PCM_24')
json.dump({'vo_starts':L,'ivr':TM['ivr']},open('stems/cues.json','w'))
print('stems ok')
