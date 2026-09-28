// Minimal mock of the After Effects ExtendScript DOM to execute the builder and validate every call.
const fs=require('fs'),vm=require('vm'),path=require('path');
let stats={comps:0,layers:0,texts:0,shapes:0,keys:0,imports:0,markers:0,errors:[]};
const bad=(m)=>{stats.errors.push(m)};
const fin=v=>Array.isArray(v)?v.every(fin):(typeof v==='number'?isFinite(v):v!==undefined);
class TextDocument{constructor(t){this.text=t;this.font='ArialMT';}resetCharStyle(){}resetParagraphStyle(){}}
class Prop{constructor(name,kind){this.name=name;this.kind=kind;this.kids={};this._v=kind==='text'?new TextDocument(''):0;this.dimensionsSeparated=false;this.nkeys=0}
 property(n){if(typeof n!=='string')bad('property() with non-string '+n);if(!this.kids[n])this.kids[n]=new Prop(n,n==='ADBE Text Document'?'text':'p');return this.kids[n]}
 addProperty(n){const p=new Prop(n,'p');this.kids[n+'#'+Object.keys(this.kids).length]=p;return p}
 get value(){return this._v} 
 setValue(v){if(!fin(v)&&!(v instanceof TextDocument)&&!(v&&v.vertices))bad(`setValue ${this.name} ${JSON.stringify(v)}`);if(this.name==='ADBE Position'&&this.dimensionsSeparated)bad('Position set while separated');this._v=v}
 setValuesAtTimes(t,v){stats.keys+=t.length;if(t.length!==v.length)bad('len mismatch '+this.name);for(let i=0;i<t.length;i++){if(!isFinite(t[i]))bad('bad time');if(i&&t[i]<=t[i-1])bad(`non-increasing times on ${this.name}: ${t[i-1]} ${t[i]}`);if(!fin(v[i]))bad(`bad value ${this.name} ${v[i]}`)}
  if(/Scale/.test(this.name)&&!v.every(x=>Array.isArray(x)&&x.length===2))bad('scale needs [x,y]');if(/Position_|Opacity/.test(this.name)&&!v.every(x=>typeof x==='number'))bad('1D prop needs numbers '+this.name)}
}
class Layer{constructor(src,name){this.name=name;this.source=src;this.root=new Prop('root');this._in=0;this._out=0;this.startTime=0;this.audioEnabled=true;stats.layers++}
 property(n){return this.root.property(n)} moveToEnd(){} 
 set inPoint(v){if(!isFinite(v)||v<0)bad('inPoint '+v);this._in=v} get inPoint(){return this._in}
 set outPoint(v){if(!isFinite(v)||v<=this._in)bad(`outPoint ${v} <= in ${this._in} on ${this.name}`);this._out=v} get outPoint(){return this._out}}
class Layers{constructor(c){this.c=c;this.list=[]}
 add(item){if(!item)bad('add null item');const l=new Layer(item,item.name);this.list.push(l);return l}
 addText(t){if(typeof t!=='string'||!t.length)bad('addText empty');stats.texts++;const l=new Layer(null,t);l.property('ADBE Text Properties').property('ADBE Text Document')._v=new TextDocument(t);this.list.push(l);return l}
 addShape(){stats.shapes++;const l=new Layer(null,'Shape');this.list.push(l);return l}}
class Comp{constructor(n,w,h,pa,d,f){if(!(w>=4&&h>=4&&w<=30000&&h<=30000))bad(`comp size ${n} ${w}x${h}`);if(!Number.isInteger(w)||!Number.isInteger(h))bad(`comp size non-int ${n}`);if(!(d>0&&f>0))bad('comp dur/fps');this.name=n;this.width=w;this.height=h;this.layers=new Layers(this);this.markerProperty={setValueAtTime:(t,m)=>{if(!isFinite(t)||!(m instanceof MarkerValue))bad('marker');stats.markers++}};stats.comps++}openInViewer(){}}
class Folder{constructor(n){this.name=n}}
const ROOT=process.argv[2];
function File(p){if(!(this instanceof File))return new File(p);this.fsName=p;this.exists=fs.existsSync(p);this.parent={fsName:path.dirname(p)}}
class ImportOptions{constructor(f){if(!f.exists)bad('import missing '+f.fsName);this.file=f}}
class MarkerValue{constructor(c){this.comment=c}}
class Shape{}
const project={items:{addFolder:n=>new Folder(n),addComp:(...a)=>new Comp(...a)},importFile:io=>{stats.imports++;return {name:path.basename(io.file.fsName)}}};
const ctx={app:{project,beginUndoGroup(){},endUndoGroup(){},newProject(){}},File,ImportOptions,MarkerValue,Shape,
 ParagraphJustification:{LEFT_JUSTIFY:7413},$:{fileName:path.join(ROOT,'HoduSoft_TheHold_BUILD.jsx')},alert:m=>console.log('ALERT:',m),Math,JSON};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(ROOT,'HoduSoft_TheHold_BUILD.jsx'),'utf8'),ctx,{filename:'jsx'});
console.log(JSON.stringify({...stats,errors:stats.errors.slice(0,15),nErrors:stats.errors.length},null,1));
