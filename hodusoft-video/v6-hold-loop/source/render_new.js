 // ---- LOOP
 const B0=L[3]-.25,B1=L[4]-.12;
 if(show(sL,L[2]+D[2]+.05,B0,t)){
  animHL(hLoop,t,TT.frz-.3);
  const tf=Math.min(t,TT.frz);const [ph,li,heat]=drawLoop(tf);
  const sh=t<TT.frz?heat*heat*16:0;const shx=(hash(Math.floor(t*30))-.5)*sh,shy=(hash(Math.floor(t*30)+3)-.5)*sh;
  const ca=P(t,L[2]+D[2]+.05,.5,'outExpo');
  T(lcv,LP.x+shx,LP.y+shy,(.8+.2*ca)*(1+.035*heat*Math.sin(t*22)),0,ca);
  ST.forEach(([n,a],i)=>{const r=a*Math.PI/180;const d=LP.r+(i%2?(PORT?95:120):62);T(stl[i],LP.x+Math.cos(r)*d+shx,LP.y+Math.sin(r)*d+shy,1,0,ca*(1-P(t,TT.frz,.3)*.6))});
  lapLbl.textContent=li>=0&&li<6?'LAP '+(li+1):'';T(lapLbl,LP.x+shx,LP.y+shy,1+.1*P(t,lapStart[Math.max(0,li)]||0,.15)*(1-P(t,(lapStart[Math.max(0,li)]||0)+.15,.2)),0,t<TT.frz&&t>=LAP0?1:0);
  const fz=P(t,TT.frz,.25);sL.style.filter=fz>0?`grayscale(${fz*.9}) brightness(${1-fz*.55})`:'none';
  red1.style.display=(t<TT.frz&&li>=3&&(t-lapStart[li])<.07)?'block':red1.style.display;
 }
 if(show(sQ,TT.frz,B0,t)){animHL(hFrz,t,B0-.18)}
 // ---- damage list (shared by loop + fix)
 const lOn=t>=LAP0&&t<L[12]-.12&&!(t>=B0&&t<B1);listBox.style.display=lOn?'block':'none';
 if(lOn){items.forEach((e,i)=>{const ta=lapStart[i]+LAPS[i]*.3;const a=P(t,ta,.3,'outBack');e.style.opacity=t>ta?1:0;
  const latest=(i===items.filter((_,j)=>t>lapStart[j]+LAPS[j]*.3).length-1);
  const tf=TT.flip0+i*.55;const st=P(t,tf,.16),fl=P(t,tf+.16,.3,'outExpo');
  const o=e.querySelector('.o'),n=e.querySelector('.n'),s=e.querySelector('.st');
  s.style.width=(st*o.offsetWidth)+'px';s.style.opacity=1-fl;o.style.opacity=1-fl;n.style.opacity=fl;
  n.style.transform=`translateY(${(1-fl)*30}px)`;o.style.color=t<TT.frz?(latest?'var(--red)':'rgba(242,240,234,.55)'):(t<B0?'rgba(242,240,234,.4)':'rgba(242,240,234,.6)');
  e.style.transform=`scale(${a*(latest&&t<TT.frz?1+.06*Math.sin(t*18):1)})`;});}
 // ---- S3 brand (unchanged from v3)
 if(show(s3,B0,B1,t)){
  const ey=PORT?cy+300:cy+340;const k=cl((t-B0)/1.2);let d='';
  for(let x=0;x<=W;x+=4){const px=x/W;const head=k*1.25;let y=200;const dd=px-head+.15;
   if(px<head){if(Math.abs(dd)<.05){const u=dd/.05;y=200-Math.exp(-u*u*6)*170*Math.cos(u*3)}else y=200+Math.sin(x*.02)*2}
   d+=(x?'L':'M')+x+' '+y.toFixed(1)}
  ecgp.setAttribute('d',d);T(ecg,cx,ey);
  T(meet,cx,(PORT?cy-230:cy-240)+(1-P(t,B0+.05,.35,'outExpo'))*30,1,0,P(t,B0+.05,.25));
  const b=P(t,B0+.12,.45,'outExpo');T(brand,cx,PORT?cy-70:cy-70,mix(1.25,1,b),0,b);
  T(by,cx,PORT?cy+110:cy+120,1,0,P(t,B0+.45,.35));
 }
 // ---- FIX
 if(show(sF,B1,L[12]-.12,t)){animHL(hFix,t,L[12]-.35);drawFix(t)}
 // ---- END
 if(show(s5,L[12]-.12,99,t)){const s=L[12];const endT=L[13]+.75;const ec=P(t,endT,.45,'outExpo');
  const ty=PORT?cy+140:cy+190;
  const rw=P(t,s,1.0,'inOut');timer5.textContent=mmss(892*(1-rw));const conn=rw>=1;
  timer5.style.color=conn?'var(--lime)':'var(--ink)';
  hold5.innerHTML=conn?'<span style="color:var(--lime)">● CONNECTED</span>':'<span style="color:#BDBDC4">◀◀ REWINDING HOLD TIME</span>';
  T(timer5,cx,mix(ty,PORT?cy-560:cy-330,ec),mix(1,.42,ec),0,P(t,s-.1,.2));
  T(hold5,cx,mix(ty-(PORT?200:180),PORT?cy-680:cy-420,ec),mix(1,.8,ec),0,P(t,s-.1,.2));
  animHL(e8,t,L[13]-.18);animHL(e9,t,endT-.05);
  const lg=P(t,endT+.25,.55,'outExpo');T(logo,cx,(PORT?cy-110:cy-120)+(1-lg)*50,1,0,lg);
  T(sub5,cx,PORT?cy+10:cy-10,1,0,P(t,endT+.4,.4));
  const ca=P(t,endT+.5,.5,'outBack');T(cta,cx,PORT?cy+190:cy+140,ca*(1+.025*Math.sin((t-endT)*5)*(t>endT+1)));
  T(url,cx,PORT?cy+330:cy+270,1,0,P(t,endT+.7,.4));
 }
 flash.style.display=(t>=B0&&t<B0+.1)?'block':'none';flash.style.opacity=.85;
}
