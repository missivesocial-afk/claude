from kokoro_onnx import Kokoro
import soundfile as sf, numpy as np
M='/tmp/claude-0/-home-user-claude/2ee6c3fa-a77f-5017-9307-4aa820a3fd09/scratchpad/v2/vo/'
k=Kokoro(M+'kokoro.onnx',M+'voices.bin')
def gen(name,text,voice,speed):
    a,sr=k.create(text,voice=voice,speed=speed,lang='en-us')
    idx=np.where(np.abs(a)>0.008)[0]; a=a[max(0,idx[0]-300):idx[-1]+1200]
    sf.write(name+'.wav',a,sr); print(name,voice,round(len(a)/sr,2)); return a
LINES={
 'pa':("Attention, passengers on SkyLine flight two fourteen to Denver. This flight has been cancelled.",'af_aoede',1.0),
 'luis':("Hi Emma, it's Luis, at SkyLine. I see you're traveling with your dad. I've held two seats up front on the six-ten, and wheelchair help will meet you at the gate.",'am_michael',1.05),
 'emma':("Oh... thank you. Thank you so much.",'af_bella',0.92),
}
for n,(t,v,s) in LINES.items(): gen(n,t,v,s)
# casting sampler: alternative voices for Luis and Emma
alts=[]
for v in ['am_michael','am_fenrir','am_puck','am_liam','am_eric']:
    alts.append(gen('cast_luis_'+v,"Hi Emma, it's Luis, at SkyLine. I see you're traveling with your dad.",v,1.05))
for v in ['af_bella','af_sarah','af_nicole','af_jessica']:
    alts.append(gen('cast_emma_'+v,"Oh... thank you. Thank you so much.",v,.92))
gap=np.zeros(int(24000*.7)); sf.write('casting_sampler.wav',np.concatenate([np.concatenate([a,gap]) for a in alts]),24000)
