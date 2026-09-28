const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const {spawn}=require('child_process');const path=require('path');
const [,,mode,W,H,arg]=process.argv;
(async()=>{
 const b=await chromium.launch({args:['--allow-file-access-from-files']});
 const p=await b.newPage({viewport:{width:+W,height:+H}});
 p.on('pageerror',e=>console.error('ERR',e.message));p.on('console',m=>console.log('LOG',m.text()));
 await p.goto('file://'+path.resolve('page.html')+`?w=${W}&h=${H}`);await p.evaluate(()=>window.ready);
 if(mode==='stills'){for(const t of arg.split(',')){await p.evaluate(t=>render(t),+t);await p.screenshot({path:`st/${W}x${H}_${t}.jpg`,type:'jpeg',quality:80})}}
 else{const fps=30,dur=32.4,N=Math.round(fps*dur);
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',''+fps,'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',arg],{stdio:['pipe','inherit','inherit']});
  for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:94});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%120==0)console.log('frame',i)}
  ff.stdin.end();await new Promise(r=>ff.on('close',r));}
 await b.close();})();
