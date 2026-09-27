from kokoro_onnx import Kokoro
import soundfile as sf, numpy as np, sys
M='/tmp/claude-0/-home-user-claude/2ee6c3fa-a77f-5017-9307-4aa820a3fd09/scratchpad/v2/vo/'
k=Kokoro(M+'kokoro.onnx',M+'voices.bin')
LINES=[
 "Every minute on hold, another customer hangs up.",          #0 pain
 "Your agents? Juggling six screens.",                         #1
 "Your supervisors? Flying blind.",                            #2
 "Meet Hodoo Soft.",                                           #3 brand
 "Hodoo See See. The AI contact center.",              #4 CC slate
 "Smart routing sends every call to the right agent.",         #5
 "Predictive dialers keep agents talking, not waiting.",       #6
 "Voice, WhatsApp, email and chat. One screen.",               #7
 "AI scores every call. Supervisors see it live.",        #8
 "Hodoo P B X. One phone system, unlimited brands.",           #9 PBX
 "SIP trunking. Auto provisioning. Call recording.",           #10
 "Hodoo Blast. Voice and SMS, to thousands at once.",#11 Blast
 "Nobody likes waiting.",                                      #12
 "Now, nobody has to.",                                        #13
]
sp=float(sys.argv[1]) if len(sys.argv)>1 else 1.12
for i,l in enumerate(LINES):
    a,sr=k.create(l,voice='af_heart',speed=sp,lang='en-us')
    idx=np.where(np.abs(a)>0.01)[0]; a=a[max(0,idx[0]-200):idx[-1]+800]
    sf.write(f'L{i}.wav',a,sr); print(i,round(len(a)/sr,2),l)
