from kokoro_onnx import Kokoro
import soundfile as sf, sys
k=Kokoro('kokoro.onnx','voices.bin')
L=["Every minute on hold, another customer hangs up.","Your agents? Juggling six screens.","Your supervisors? Flying blind.",
"Meet Hodoo See See, by Hodoo Soft.","Smart IVR sends every call to the right agent.","Predictive dialing keeps your team talking, not waiting.",
"Voice, WhatsApp, email and chat. One screen.","Supervisors can listen, whisper, or barge in. Live.","Nobody likes waiting.","Now, nobody has to."]
for i,l in enumerate(L):
    a,sr=k.create(l,voice=sys.argv[1],speed=float(sys.argv[2]),lang='en-us')
    sf.write(f'{sys.argv[1]}_{i}.wav',a,sr); print(i,round(len(a)/sr,2),l)
