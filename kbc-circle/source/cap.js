// node cap.js stills 1920 1080 0.5,1,2   |  node cap.js video 1920 1080 out.mp4
const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const {spawn}=require('child_process');const path=require('path');
const FF=process.env.FFMPEG||'ffmpeg';
const [,,mode,W,H,arg]=process.argv;
(async()=>{
 const b=await chromium.launch();
 const p=await b.newPage({viewport:{width:+W,height:+H}});
 p.on('pageerror',e=>console.error('ERR',e.message));
 await p.goto('file://'+path.resolve(__dirname,'index.html')+`?w=${W}&h=${H}&cap=1`);await p.evaluate(()=>window.ready);
 if(mode==='stills'){require('fs').mkdirSync('stills',{recursive:true});
  for(const t of arg.split(',')){await p.evaluate(t=>render(t),+t);await p.screenshot({path:`stills/${W}x${H}_${t}.jpg`,type:'jpeg',quality:85})}}
 else{const fps=30,N=fps*5;
  const ff=spawn(FF,['-y','-v','error','-f','image2pipe','-framerate',''+fps,'-c:v','png','-i','-','-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',arg],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/fps);const buf=await p.screenshot({type:'png'});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));}
 await b.close();})();
