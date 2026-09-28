const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const {spawn}=require('child_process');const fs=require('fs');const path=require('path');
const [,,mode,W,H,out]=process.argv;const PAGE=path.resolve('../v3/page.html');
(async()=>{
 const b=await chromium.launch({args:['--allow-file-access-from-files']});
 const p=await b.newPage({viewport:{width:+W,height:+H}});
 p.on('pageerror',e=>console.error('ERR',e.message));
 await p.goto('file://'+PAGE+`?w=${W}&h=${H}`);await p.evaluate(()=>window.ready);
 await p.addScriptTag({content:fs.readFileSync('sampler.js','utf8')});
 console.log(await p.evaluate(()=>AE.setup()));
 const fps=30,dur=39.91,N=Math.round(fps*dur);
 if(mode==='data'){
  const frames=[];
  for(let i=0;i<N;i++){frames.push(await p.evaluate(t=>AE.sample(t),i/fps));if(i%200==0)console.log('f',i)}
  fs.writeFileSync(out,JSON.stringify({W:+W,H:+H,fps,dur,N,meta:await p.evaluate(()=>AE.meta()),frames}));
 }else{
  await p.evaluate(()=>AE.hideForPlate());
  if(mode==='still'){for(const t of out.split(',')){await p.evaluate(t=>render(t),+t);await p.screenshot({path:`plate_${W}x${H}_${t}.jpg`,type:'jpeg',quality:80})}}
  else{const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',''+fps,'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',out],{stdio:['pipe','inherit','inherit']});
   for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:95});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%200==0)console.log('p',i)}
   ff.stdin.end();await new Promise(r=>ff.on('close',r));}
 }
 await b.close();})();
