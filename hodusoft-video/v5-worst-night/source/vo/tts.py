from kokoro_onnx import Kokoro
import soundfile as sf, numpy as np, json
M='/tmp/claude-0/-home-user-claude/2ee6c3fa-a77f-5017-9307-4aa820a3fd09/scratchpad/v2/vo/'
k=Kokoro(M+'kokoro.onnx',M+'voices.bin')
L={
 'ivr':("All of our agents are currently assisting other customers. Your estimated wait time is... forty-seven minutes.",'af_kore',1.0),
 'ceo1':("Dana. Walk me through last night.",'am_onyx',0.95),
 'whisper':("Offer her lounge access.",'af_heart',0.92),
 'ceo2':("Dana... how did we get through last night?",'am_onyx',0.95),
 'dana':("Honestly? I went back to sleep.",'af_heart',0.98),
 'narr':("Built for the nights nobody plans for.",'am_michael',0.95),
}
out={}
for n,(t,v,s) in L.items():
    a,sr=k.create(t,voice=v,speed=s,lang='en-us')
    idx=np.where(np.abs(a)>0.008)[0]; a=a[max(0,idx[0]-300):idx[-1]+1500]
    sf.write(n+'.wav',a,sr); out[n]=round(len(a)/sr,3); print(n,v,out[n])
json.dump(out,open('durs.json','w'))
