const fs=require('node:fs'), path=require('node:path'), vm=require('node:vm'), assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'), source=fs.readFileSync(path.join(root,'js/liquid-text.js'),'utf8');
function fixture({words=['anime.','motive.','engage.'],reduced=false,observer=true}={}) {
 let now=0,id=0,observe;
 const frames=new Map(),events={},attrs={},from={style:{}},to={style:{}},stage={style:{}},fallback={hidden:false};
 const button={hidden:true,setAttribute:(k,v)=>attrs[k]=v,addEventListener:(k,fn)=>events[k]=fn};
 const element={dataset:{liquidWords:JSON.stringify(words)},querySelector:s=>s==='[data-liquid-switch]'?button:s==='.liquid-static'?fallback:s==='.liquid-stage'?stage:s==='[data-liquid-from]'?from:to};
 const motion={matches:reduced,addEventListener:(k,fn)=>motion[k]=fn};
 const document={hidden:false,querySelectorAll:()=>[element],addEventListener:(k,fn)=>document[k]=fn};
 const context={document,matchMedia:()=>motion,requestAnimationFrame:fn=>{frames.set(++id,fn);return id},cancelAnimationFrame:n=>frames.delete(n)};
 if(observer)context.IntersectionObserver=class{constructor(fn){observe=fn}observe(){}};
 context.window=context;vm.runInNewContext(source,context);
 const flush=ms=>{now+=ms;const callbacks=[...frames.values()];frames.clear();callbacks.forEach(fn=>fn(now));};
 return {words,element,button,from,to,stage,fallback,motion,document,events,attrs,frames,flush,visible:v=>observe([{isIntersecting:v}])};
}
let f=fixture();assert.equal(f.frames.size,0);f.visible(true);f.flush(0);f.flush(500);
assert.equal(f.from.textContent,'anime.');assert.equal(f.from.style.opacity,'1');
assert.equal(f.stage.style.filter,'none');
f.flush(750);assert.equal(f.from.style.filter,'blur(8px)');assert.equal(f.to.style.filter,'blur(8px)');assert.ok(Number(f.to.style.opacity)>.7);assert.equal(f.stage.style.filter,'');
f.flush(750);assert.equal(f.from.textContent,'motive.');assert.equal(f.from.style.filter,'none');assert.equal(f.to.style.opacity,'0');assert.equal(f.stage.style.filter,'none');
f.flush(2000);assert.equal(f.from.textContent,'engage.');f.flush(2000);assert.equal(f.from.textContent,'anime.');
for(const list of [['passionnée.','engagée.'],['projets.','fiertés.'],['Christelle','Girl Boss'],['collaborer.','créer.','réussir.']]){
 const g=fixture({words:list,observer:false});g.flush(0);
 for(let i=1;i<=list.length;i++){g.flush(2000);assert.equal(g.from.textContent,list[i%list.length]);}
}
f.events.click();assert.equal(f.frames.size,0);assert.equal(f.attrs['aria-pressed'],'true');assert.equal(f.from.style.opacity,'1');
f.events.click();assert.equal(f.frames.size,1);
f.events.focus();assert.equal(f.frames.size,0);f.events.blur();assert.equal(f.frames.size,1);
f.events.pointerenter({pointerType:'mouse'});assert.equal(f.frames.size,0);f.events.pointerleave();assert.equal(f.frames.size,1);
f.document.hidden=true;f.document.visibilitychange();assert.equal(f.frames.size,0);f.document.hidden=false;f.document.visibilitychange();assert.equal(f.frames.size,1);
f.visible(false);assert.equal(f.frames.size,0);f.visible(true);assert.equal(f.frames.size,1);
f.motion.matches=true;f.motion.change();assert.equal(f.frames.size,0);assert.equal(f.button.hidden,true);assert.equal(f.fallback.hidden,false);
f.motion.matches=false;f.motion.change();assert.equal(f.button.hidden,false);assert.equal(f.fallback.hidden,true);assert.equal(f.frames.size,1);
const g=fixture({reduced:true});g.visible(true);assert.equal(g.frames.size,0);assert.equal(g.button.hidden,true);
const single=fixture({words:['Un mot']});assert.equal(single.button.hidden,true);assert.equal(single.frames.size,0);
const css=fs.readFileSync(path.join(root,'css/manifesto.css'),'utf8');assert.doesNotMatch(css,/min-height:600px/);
console.log(JSON.stringify({passed:true,covers:['five word lists','500ms pause + 1500ms morph','liquid blur and opacity','loop','pause and resume','hover','focus','offscreen','hidden document','reduced motion','no observer fallback','single word fallback','compact last manifesto conviction']}));
