# Rebuild frames from the AE data (plate + text drawn from keyframes) to compare with the original render
import json,sys,subprocess
from PIL import Image,ImageDraw,ImageFont
s=open('HoduSoft_TheHold_BUILD.jsx').read(); D=json.loads(s[s.index('var DATA = ')+11:s.index(';\n    var ROOT')])
def val(keys,t):
    if len(keys)==1 or t<=keys[0][0]: return keys[0][1]
    for i in range(1,len(keys)):
        if t<=keys[i][0]:
            a,b=keys[i-1],keys[i]; return a[1]+(b[1]-a[1])*(t-a[0])/(b[0]-a[0])
    return keys[-1][1]
FONTS={}
def font(name,sz): 
    k=(name,round(sz,1))
    if k not in FONTS: FONTS[k]=ImageFont.truetype(f'fonts/{name}.ttf',max(1,int(round(sz))))
    return FONTS[k]
def draw_text(img,u,t,ox=0,oy=0,extra_o=1):
    if not(u['in']<=t<u['out']): return
    o=val(u['k']['o'],t)/100*extra_o; 
    if o<=0: return
    x,y,sc=val(u['k']['x'],t),val(u['k']['y'],t),val(u['k']['s'],t)/100
    layer=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(layer)
    col=tuple(int(c*255) for c in u['col'])+(int(255*o),)
    d.text((ox+x,oy+y),u['text'],font=font(u['font'],u['fs']*sc),fill=col,anchor='ls')
    img.alpha_composite(layer)
def frame(fi,t):
    fm=D['formats'][fi]; W,H=fm['W'],fm['H']
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',fm['plate'].replace('footage/',''),'-frames:v','1','/tmp/claude-0/pf.png'])
    img=Image.open('/tmp/claude-0/pf.png').convert('RGBA')
    for sh in fm['shapes']:
        if not(sh['in']<=t<sh['out']): continue
        o=val(sh['k']['o'],t)/100
        if o<=0: continue
        x,y,sc=val(sh['k']['x'],t),val(sh['k']['y'],t),val(sh['k']['s'],t)/100; w,h=sh['w']*sc,sh['h']*sc
        lay=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(lay); box=[x-w/2,y-h/2,x+w/2,y+h/2]
        if sh['kind']=='ellipse': d.ellipse(box,fill=tuple(int(c*255) for c in sh['fill'])+(int(255*o),))
        elif sh['fill']: d.rounded_rectangle(box,radius=h/2,fill=tuple(int(c*255) for c in sh['fill'])+(int(255*o),))
        else: d.rounded_rectangle(box,radius=h/2,outline=tuple(int(c*255) for c in sh['stroke'])+(int(255*o),),width=2)
        img.alpha_composite(lay)
    for c in fm['clips']:
        if not(c['in']<=t<c['out']): continue
        o=val(c['k']['o'],t)/100
        if o<=0: continue
        pc=Image.new('RGBA',(c['w'],c['h']),(0,0,0,0))
        for w in c['words']: draw_text(pc,w,t)
        sc=val(c['k']['s'],t)/100; pc=pc.resize((max(1,int(c['w']*sc)),max(1,int(c['h']*sc))))
        if o<1: a=pc.split()[3].point(lambda v:int(v*o)); pc.putalpha(a)
        x,y=val(c['k']['x'],t),val(c['k']['y'],t); img.alpha_composite(pc,(int(round(x-pc.width/2)),int(round(y-pc.height/2))))
    for u in fm['texts']: draw_text(img,u,t)
    return img.convert('RGB')
fi=int(sys.argv[1]); ts=[float(x) for x in sys.argv[2].split(',')]
ims=[frame(fi,t) for t in ts]; W,H=ims[0].size; sc=360/H if fi==1 else 480/H
row=Image.new('RGB',(int(W*sc)*len(ims),int(H*sc)))
for i,im in enumerate(ims): row.paste(im.resize((int(W*sc),int(H*sc))),(i*int(W*sc),0))
row.save(sys.argv[3])
