# Synthesized (royalty-free) 5s soundtrack: whoosh riser -> lock-in hit -> shimmer -> big hit at 4.05s
import numpy as np, wave
SR=44100; DUR=5.0; N=int(SR*DUR); rng=np.random.default_rng(5); T=np.arange(N)/SR
def onepole(x,fc):
    a=np.exp(-2*np.pi*np.asarray(fc)/SR)*np.ones(len(x)); y=np.empty_like(x); s=0.0
    for k in range(len(x)): s=(1-a[k])*x[k]+a[k]*s; y[k]=s
    return y
def add(buf,sig,t0,g=1): i=int(t0*SR); j=min(N,i+len(sig)); buf[i:j]+=sig[:j-i]*g
L=np.zeros(N); R=np.zeros(N)
# 1) riser whoosh 0-1.5s (filtered noise sweeping up)
n=int(1.55*SR); t=np.arange(n)/SR; fc=200+6000*(t/1.55)**2
w=onepole(rng.standard_normal(n),fc); w-=onepole(w,150); w*=(t/1.55)**2*0.5
add(L,w,0); add(R,np.roll(w,90),0)
# 2) deep sub drone swelling in
d=np.sin(2*np.pi*55*T)*0.18*np.clip((T-0.3)/1.2,0,1)*np.exp(-np.clip(T-4.2,0,None)*1.5); L+=d; R+=d
def hit(g):
    n=int(1.6*SR); t=np.arange(n)/SR; f=40+120*np.exp(-t*20)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.5)+0.5*onepole(rng.standard_normal(n),3000)*np.exp(-t*18)
    return np.tanh(s*1.5)*g
add(L,hit(.8),1.5); add(R,hit(.8),1.5)
# 3) gold shimmer: bell partials (A major-ish) with arpeggio
def bell(f,dur=2.2):
    n=int(dur*SR); t=np.arange(n)/SR
    return sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*(2+m)) for m,a in [(1,1),(2.01,.4),(3.0,.2),(4.2,.1)])*0.12
for i,m in enumerate([81,85,88,93,97,100]):
    f=440*2**((m-69)/12); b=bell(f); t0=1.55+i*.09
    add(L,b,t0,1-(i%2)*.4); add(R,b,t0,.6+(i%2)*.4)
# sparkle ticks during sweep
for k in range(22):
    t0=2.5+rng.random()*1.3; f=3000+rng.random()*3000; n=int(.15*SR); t=np.arange(n)/SR
    s=np.sin(2*np.pi*f*t)*np.exp(-t*40)*.05; p=rng.random(); add(L,s,t0,p); add(R,s,t0,1-p)
# 4) big hit + chord at 4.05
add(L,hit(1.0),4.02); add(R,hit(1.0),4.02)
for m in [57,64,69,73,76,81]:
    f=440*2**((m-69)/12); n=N-int(4.02*SR); t=np.arange(n)/SR
    s=(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2*f*t))*np.exp(-t*1.2)*.07; add(L,s,4.02); add(R,s,4.02,.9)
rev=lambda x: x+0.3*np.roll(onepole(x,4000),int(.07*SR))+0.2*np.roll(onepole(x,3000),int(.13*SR))
L,R=rev(L),rev(R); fade=np.clip((DUR-T)/0.3,0,1); L*=fade; R*=fade
pk=max(abs(L).max(),abs(R).max()); L,R=L/pk*.89,R/pk*.89
with wave.open('soundtrack.wav','wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((np.stack([L,R],1)*32767).astype('<i2').tobytes())
