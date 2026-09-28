// =========== THE HOLD LOOP ===========
const LP=PORT?{x:cx,y:1010,r:300,lx:80,ly:1360,lf:62,lh:80,cyH:330,hf:130}:{x:700,y:610,r:285,lx:1200,ly:300,lf:56,lh:78,cyH:150,hf:110};
const LAPS=[1.5,1.25,1.02,.84,.7,.58], LAP0=T.laps;
const lapStart=[];{let a=LAP0;LAPS.forEach(d=>{lapStart.push(a);a+=d})}
const LAPEND=lapStart[5]+LAPS[5];
const DOTS=[1,3,8,18,40,80];
const sL=el('div','scene');
const hLoop=headline(sL,['Every dropped call','calls|red back.|red'],PORT?960:1500,LP.hf);hLoop._center=true;hLoop._cy=LP.cyH;
const lcv=el('canvas','c',null,sL);const CS=2*LP.r+260;lcv.width=CS;lcv.height=CS;const lx=lcv.getContext('2d');
const ST=[['ON HOLD',-90],['DROPPED',0],['CALLS BACK',90],['ON HOLD AGAIN',180]];
const stl=ST.map(([n,a])=>el('div','c',n,sL,`font-family:Mono;font-size:${PORT?26:24}px;letter-spacing:.14em;color:#BDBDC4;white-space:nowrap`));
const lapLbl=el('div','c','',sL,`font-family:Anton;font-size:${PORT?90:84}px;color:var(--ink)`);
const hFrz=headline(sL,['So how do you','get off|lime the loop?|lime'],PORT?960:1500,PORT?140:130);hFrz._center=true;hFrz._cy=PORT?LP.y:LP.y;
// damage list (shared by loop + fix)
const LIST=[['1 DROPPED CALL','0 DROPPED CALLS'],['38 CALLBACKS','0 CALLBACKS'],['412 IN QUEUE','0 IN QUEUE'],['★☆☆☆☆ “NEVER AGAIN”','★★★★★ “THAT WAS FAST”'],['CUSTOMER LOST','CUSTOMER KEPT'],['REVENUE ↓','REVENUE ↑']];
const listBox=el('div','a',null,stage,`left:0;top:0;width:${W}px;height:${H}px;pointer-events:none`);
const items=LIST.map((it,i)=>{const e=el('div','a',`<span class="o">${it[0]}</span><span class="n" style="position:absolute;left:0;top:0;color:var(--lime);opacity:0">${it[1]}</span><span class="st" style="position:absolute;left:0;top:52%;height:6px;background:var(--red);width:0"></span>`,listBox,`left:${LP.lx}px;top:${LP.ly+i*LP.lh}px;font-family:Anton;font-size:${LP.lf}px;white-space:nowrap;color:var(--ink);transform-origin:0 50%`);return e});
// =========== THE FIX: loop unravels into a line ===========
const sF=el('div','scene');
const hFix=headline(sF,['Every call.','answered.|lime'],PORT?960:1500,LP.hf);hFix._center=true;hFix._cy=LP.cyH;
const fcv=el('canvas','c',null,sF);fcv.width=W;fcv.height=H;const fx_=fcv.getContext('2d');
const lbCall=el('div','c','CALL',sF,`font-family:Mono;font-size:${PORT?30:28}px;letter-spacing:.14em;color:#BDBDC4`);
const lbAns=el('div','c','ANSWERED ✓',sF,`font-family:Anton;font-size:${PORT?64:60}px;color:var(--lime);white-space:nowrap`);
const lineEnd=PORT?{x0:90,x1:990,y:LP.y}:{x0:110,x1:1120,y:LP.y};

function lapPhase(t){ // total laps travelled (float) and current lap index
 if(t<LAP0)return [0,-1];let acc=0;for(let i=0;i<6;i++){const a=lapStart[i],d=LAPS[i];if(t<a+d)return [i+(t-a)/d,i]}return [6+(t-LAPEND)/.5,6]}
function drawLoop(t,frozen){
 const [ph,li]=lapPhase(t);const heat=cl(ph/6);
 lx.clearRect(0,0,CS,CS);const c0=CS/2;
 const col=`rgb(${mix(242,255,heat)|0},${mix(100,46,heat)|0},${mix(34,85,heat)|0})`;
 lx.lineWidth=6+heat*6;lx.strokeStyle=col;lx.globalAlpha=.35+.35*heat;lx.beginPath();lx.arc(c0,c0,LP.r,0,6.283);lx.stroke();lx.globalAlpha=1;
 // station ticks
 ST.forEach(([n,a])=>{const r=a*Math.PI/180;lx.fillStyle='#F2F0EA';lx.beginPath();lx.arc(c0+Math.cos(r)*LP.r,c0+Math.sin(r)*LP.r,9,0,6.283);lx.fill()});
 // dots with motion trails
 const n=li<0?0:DOTS[Math.min(5,li)];const spd=li<0?1:1/LAPS[Math.min(5,li)];
 for(let j=0;j<n;j++){const ang=-Math.PI/2+(ph*2*Math.PI)-j*(2*Math.PI/Math.max(n,1))*(n>1?1:0)-j*.0;
  const trail=Math.min(1.4,.12*spd*2.2);
  lx.strokeStyle=col;lx.lineCap='round';lx.lineWidth=14;lx.globalAlpha=.35;lx.beginPath();lx.arc(c0,c0,LP.r,ang-trail,ang);lx.stroke();lx.globalAlpha=1;
  lx.shadowColor=col;lx.shadowBlur=24;lx.fillStyle='#fff';lx.beginPath();lx.arc(c0+Math.cos(ang)*LP.r,c0+Math.sin(ang)*LP.r,11,0,6.283);lx.fill();lx.shadowBlur=0}
 return [ph,li,heat];
}
function drawFix(t){
 const k=P(t,T.fix0,1.0,'inOut');fx_.clearRect(0,0,W,H);
 const pts=[];const Np=240;
 for(let i=0;i<=Np;i++){const u=i/Np;const ang=-Math.PI/2+u*2*Math.PI;
  const c=[LP.x+Math.cos(ang)*LP.r,LP.y+Math.sin(ang)*LP.r],l=[mix(lineEnd.x0,lineEnd.x1,u),lineEnd.y];pts.push([mix(c[0],l[0],k),mix(c[1],l[1],k)])}
 fx_.strokeStyle='#F26422';fx_.lineWidth=8;fx_.shadowColor='#F26422';fx_.shadowBlur=20;fx_.beginPath();pts.forEach((p,i)=>i?fx_.lineTo(p[0],p[1]):fx_.moveTo(p[0],p[1]));fx_.stroke();fx_.shadowBlur=0;
 // dots zip along the straightened line and land on ANSWERED
 if(k>=1){for(let j=0;j<14;j++){const u=((t-T.fix0-1)*.9+j/14)%1;const p=pts[Math.floor(u*Np)];fx_.fillStyle='#fff';fx_.shadowColor='#F26422';fx_.shadowBlur=18;fx_.beginPath();fx_.arc(p[0],p[1],9,0,6.283);fx_.fill();fx_.shadowBlur=0}}
 T(lbCall,lineEnd.x0+40,lineEnd.y-60,1,0,P(t,T.fix0+.9,.3));
 const aa=P(t,T.fix0+1.0,.45,'outBack');T(lbAns,PORT?lineEnd.x1-170:lineEnd.x1-150,lineEnd.y+(PORT?80:75),aa,0,aa>0?1:0);
}
