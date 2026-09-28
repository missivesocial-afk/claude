from kokoro_onnx import Kokoro
import soundfile as sf, numpy as np
M='/tmp/claude-0/-home-user-claude/2ee6c3fa-a77f-5017-9307-4aa820a3fd09/scratchpad/v2/vo/'
k=Kokoro(M+'kokoro.onnx',M+'voices.bin')
S=["Do you know if there's another flight tonight?","I'm going to call my sister, she was picking us up.","They said the counter opens at five.","Is this line for rebooking?","We've been here since nine.","Can you watch the bags for a second?","I think the storm moved east.","My phone's almost dead, do you have a charger?","Honey, sit down, it's going to be a while.","They cancelled Boston too.","Excuse me, is gate B7 this way?","I just want to get home."]
V=['af_sarah','am_adam','af_nicole','am_eric','af_jessica','am_liam','af_river','am_echo','af_nova','am_onyx','af_sky','am_puck']
for i,(t,v) in enumerate(zip(S,V)):
    a,sr=k.create(t,voice=v,speed=1.0,lang='en-us'); sf.write(f'bab{i}.wav',a,sr)
print('ok')
