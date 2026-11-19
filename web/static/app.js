"use strict";
const $ = id => document.getElementById(id);
let state, result, currentJob, upload, bounds, audioUrls=[], revision=0;
const pause = ms => new Promise(r=>setTimeout(r,ms));
const fmt = (n,d=1) => Number(n).toLocaleString("ru",{maximumFractionDigits:d});
const query = obj => new URLSearchParams(obj).toString();
async function api(path, options) {
  const r=await fetch("/api/"+path,options);
  const body=await r.json();
  if (!r.ok) throw Error(body.error || r.statusText);
  return body;
}
const post=(path,data)=>api(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
function bind(id,event,fn) {
  $(id).addEventListener(event,async e=>{
    $("error").textContent="";
    try {await fn(e)} catch(err){$("error").textContent=err.message}
  });
}
function options(select,rows,placeholder) {
  select.replaceChildren(new Option(placeholder,""),...rows.map(r=>new Option(r.role+" · "+r.name+" · "+r.stage,r.id)));
}
function clearAudio(){
  $("players").replaceChildren();audioUrls.forEach(URL.revokeObjectURL);audioUrls=[];
}
function profile(){return state.profiles.find(p=>p.id===$("profile").value)}
function setup(){
  const p=profile(); $("profileinfo").textContent=p.object+". "+p.calibration+". "+p.hardware+".";
  $("rate").value=p.rate;$("center").value=p.center/1e6;$("mode").value=p.audio;
  $("lo").value=(p.frequency-4000)/1e6;$("hi").value=(p.frequency+4000)/1e6;
  sourceChanged();describeAudio();
}
function sourceChanged(){
  const s=$("source").value;
  $("filewrap").hidden=s!=="import";$("usb").hidden=s!=="live";
  $("seconds").disabled=s==="import";$("seconds").value=s==="demo"?2:profile().seconds;
  if(s==="import"){$("params").open=true;$("gain").value="";$("receiver").value="";$("chain").value=""}
  else {if(!$("gain").value)$("gain").value="28";if(!$("receiver").value)$("receiver").value="RTL-SDR Blog V3";if(!$("chain").value)$("chain").value="Рупор + МШУ"}
  if(s==="live")probe();
}
async function probe(){$("device").textContent=(await api("device")).message}
async function refresh(pick){
  const old=$("record").value, ref=$("off").value;
  state=await api("state");
  $("disk").textContent="Свободно "+fmt(state.free/1024**3)+" ГиБ";
  const records=state.records.filter(r=>r.profile===$("profile").value);
  options($("record"),records,"Выбрать запись");
  $("record").value=pick || (records.some(r=>r.id===old)?old:records[0]?.id || "");
  options($("off"),records.filter(r=>r.id!==$("record").value),"Без сравнения");
  $("off").value=!pick && records.some(r=>r.id===ref && r.id!==$("record").value)?ref:"";
  await loadResult();
}
async function loadResult(){
  const version=++revision;clearAudio();bounds=null;result=null;draw();
  const key=$("record").value;
  if(!key)return;
  const res=await api("result?"+query({id:key,off:$("off").value}));
  if(version!==revision)return;
  result=res;
  const p=profile(), low=(p.frequency-p.band/2)/1e6, high=(p.frequency+p.band/2)/1e6;
  if(p.view==="spectrum" && low>=res.freq[0]/1e6 && high<=res.freq.at(-1)/1e6)bounds=[low,high];
  draw();
}
async function watch(id){
  currentJob=id;$("jobbox").hidden=false;$("start").disabled=true;
  try {
    for(;;){
      const j=await api("job?id="+id);
      $("phase").textContent=j.phase+" · "+Math.round(100*j.progress)+"%";$("progress").value=j.progress;
      if(j.state!=="running"){
        if(j.state==="done")await refresh(id);
        if(j.state==="error")throw Error(j.phase);
        break;
      }
      await pause(150);
    }
  }finally{currentJob=null;$("start").disabled=false;$("stop").disabled=true}
}
async function start(){
  const source=$("source").value;
  const m={profile:profile().id,source,name:$("name").value || profile().name+" "+$("role").value,
    origin:$("origin").value,role:$("role").value,seconds:Number($("seconds").value),center:Math.round(Number($("center").value)*1e6),
    rate:$("rate").value,gain:$("gain").value,ppm:$("ppm").value,receiver:$("receiver").value,chain:$("chain").value,notes:$("notes").value};
  $("stop").disabled=false;
  if(source!=="import"){await watch((await post("start",m)).id);return}
  const file=$("file").files[0];if(!file)throw Error("Выберите файл IQ");
  if(file.size>state.limit)throw Error("Файл превышает настроенный предел");
  m.id=Array.from(crypto.getRandomValues(new Uint8Array(16)),b=>b.toString(16).padStart(2,"0")).join("");
  currentJob=m.id;upload=new AbortController();
  $("start").disabled=true;$("jobbox").hidden=false;$("phase").textContent="Передача IQ";$("progress").value=0;
  const timer=setInterval(async()=>{try{const j=await api("job?id="+m.id);$("phase").textContent=j.phase;$("progress").value=j.progress}catch{}},200);
  try{
    await api("import?"+query(m),{method:"POST",body:file,signal:upload.signal});
    await watch(m.id);
  }catch(e){if(e.name!=="AbortError")throw e;$("phase").textContent="Остановлено"}
  finally{clearInterval(timer);upload=null;currentJob=null;$("start").disabled=false}
}
function axes(){
  const time=profile().view==="time"; const r=result;
  const power=a=>a.map(v=>10*Math.log10(Math.max(1e-30,v)));
  return time?{x:r.times,y:power(r.power),xo:r.offTimes,yo:power(r.offPower),unit:"дБFS",label:"Время, с"}
    :{x:r.freq.map(f=>f/1e6),y:r.values,xo:[],yo:[],unit:r.unit,label:"Частота, МГц"};
}
function draw(){
  const canvas=$("plot"),box=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
  const w=box.width,h=box.height;canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);
  const c=canvas.getContext("2d");c.scale(dpr,dpr);c.fillStyle="#101819";c.fillRect(0,0,w,h);
  $("empty").hidden=!!result;
  ["csv","png","metadata","listen","reset","confirmObs"].forEach(id=>$(id).disabled=!result);
  if(!result){$("meta").textContent="";$("stage").textContent="";return}
  const r=result,a=axes(),time=profile().view==="time";
  $("chartname").textContent=time?"Мощность рабочей полосы":$("off").value?"Превышение ON/OFF":"Спектр мощности";
  $("stage").textContent=r.meta.stage;
  $("meta").textContent=fmt(r.meta.center/1e6,6)+" МГц · "+fmt(r.meta.rate/1e6,4)+" Мвыб/с · усиление "+(r.meta.gain??"не задано")+" дБ · "+fmt(r.meta.elapsed,3)+" с · шаг "+fmt(r.df)+" Гц · предельные коды АЦП "+fmt(100*r.clip,4)+"%";
  const span=bounds||[Math.min(a.x[0],a.xo[0]??Infinity),Math.max(a.x.at(-1),a.xo.at(-1)??-Infinity)];
  const [left,right]=span, x0=60,x1=w-15,y0=28,y1=h-42;
  const select=(x,y)=>y.filter((v,i)=>v!==null&&x[i]>=left&&x[i]<=right);
  const ys=select(a.x,a.y).concat(select(a.xo,a.yo));
  const min=ys.length?Math.min(...ys):0,max=ys.length?Math.max(...ys):1,pad=Math.max((max-min)*.08,.001);
  const xp=x=>x0+(x-left)/(right-left||1)*(x1-x0),yp=y=>y1-(y-min+pad)/(max-min+2*pad)*(y1-y0);
  c.font="11px system-ui";c.fillStyle="#acbcb8";c.fillText(a.unit,8,15);
  for(let i=0;i<5;i++){const y=y0+(y1-y0)*i/4;c.strokeStyle="#2d3b3d";c.beginPath();c.moveTo(x0,y);c.lineTo(x1,y);c.stroke();c.fillText(fmt(max+pad-(max-min+2*pad)*i/4,2),4,y+3)}
  for(let i=0;i<=4;i++){const x=x0+(x1-x0)*i/4;c.textAlign="center";c.fillText(fmt(left+(right-left)*i/4,time?2:4),Math.min(w-30,x),y1+16)}
  c.fillText(a.label,(x0+x1)/2,h-5);c.textAlign="left";
  function trace(xs,ys,color){c.beginPath();let pen=false;xs.forEach((x,i)=>{let v=ys[i];if(x<left||x>right||v===null){pen=false;return}if(pen)c.lineTo(xp(x),yp(v));else c.moveTo(xp(x),yp(v));pen=true});c.strokeStyle=color;c.lineWidth=1.4;c.stroke()}
  trace(a.x,a.y,"#9be7b7");trace(a.xo,a.yo,"#f5b87b");
  if(a.xo.length){c.fillStyle="#f5b87b";c.fillText("OFF",w-56,15)}
  canvas.range={left,right,x0,x1};
}
function graphX(e){const canvas=$("plot"),g=canvas.range;
  return g.left+(e.clientX-canvas.getBoundingClientRect().left-g.x0)/(g.x1-g.x0)*(g.right-g.left)}
function describeAudio(){
  $("audioinfo").textContent=$("mode").value==="noise"?"Первые до 5 с выбранного участка IQ с указанного момента. Полоса переносится к 500 Гц. Обе записи используют один коэффициент усиления.":"За 3 с частота тона проходит спектр слева направо. Уровню от −120 до −40 дБFS/Гц соответствует высота от 200 до 2000 Гц. Шкала одинакова для обеих записей.";
  clearAudio();
}
function download(url,name){const a=document.createElement("a");a.href=url;a.download=name;a.click()}
async function audio(){
  clearAudio();const version=revision;
  for(const [role,id] of [["Основная",$("record").value],["Опорная",$("off").value]]){
    if(!id)continue;
    const q=query({id,mode:$("mode").value,lo:Math.round($("lo").value*1e6),hi:Math.round($("hi").value*1e6),start:$("offset").value,volume:$("volume").value});
    const resp=await fetch("/api/audio?"+q);if(!resp.ok)throw Error((await resp.json()).error);
    const blob=await resp.blob();if(revision!==version)return;
    const url=URL.createObjectURL(blob);audioUrls.push(url);
    const row=document.createElement("p"),player=document.createElement("audio"),link=document.createElement("a");
    player.controls=true;player.src=url;link.textContent="Скачать WAV";link.download=id+".wav";link.href=url;
    row.append(role+" ",player,link);$("players").append(row);
  }
}
bind("profile","change",async()=>{setup();await post("settings",{profile:profile().id,volume:$("volume").value});await refresh()});
bind("source","change",sourceChanged);bind("start","click",start);bind("probe","click",probe);
bind("sidecar","change",async()=>{
  const file=$("sidecar").files[0];if(!file)return;
  if(file.size>65536)throw Error("Метаданные должны помещаться в 64 КиБ");
  const m=JSON.parse(await file.text());
  if(!state.profiles.some(p=>p.id===m.profile)||!Number.isFinite(m.center)||!Number.isFinite(m.rate))throw Error("Требуются профиль, центральная частота и частота дискретизации");
  $("profile").value=m.profile;setup();$("center").value=m.center/1e6;
  for(const key of ["role","name","rate","gain","ppm","receiver","chain","notes"])$(key).value=m[key]??"";
  $("origin").value=m.synthetic?"model":"physical";await refresh();
});
bind("record","change",()=>refresh($("record").value));bind("off","change",loadResult);
bind("stop","click",async()=>{try{if(currentJob)await post("job",{id:currentJob})}finally{upload?.abort()}});
bind("reset","click",()=>{bounds=null;draw()});bind("mode","change",describeAudio);
bind("volume","change",async()=>{clearAudio();await post("settings",{profile:profile().id,volume:$("volume").value})});
bind("listen","click",audio);
bind("plot","mousemove",e=>{if(!result)return;const a=axes(),x=graphX(e),i=a.x.reduce((k,f,j)=>Math.abs(f-x)<Math.abs(a.x[k]-x)?j:k,0);$("cursor").textContent=fmt(a.x[i],6)+(profile().view==="time"?" с":" МГц")+" · "+(a.y[i]===null?"маска":fmt(a.y[i],3)+" "+a.unit)});
$("plot").addEventListener("wheel",e=>{if(!result)return;e.preventDefault();const a=axes(),g=$("plot").range,x=graphX(e),k=e.deltaY<0?.7:1.4;
  const lo=Math.max(Math.min(a.x[0],a.xo[0]??Infinity),x+(g.left-x)*k),hi=Math.min(Math.max(a.x.at(-1),a.xo.at(-1)??-Infinity),x+(g.right-x)*k);
  if(hi-lo>2*(a.x[1]-a.x[0]))bounds=[lo,hi];draw()},{passive:false});
bind("png","click",()=>download($("plot").toDataURL("image/png"),"observation.png"));
bind("csv","click",()=>download("/api/csv?"+query({id:$("record").value,off:$("off").value}),"observation.csv"));
bind("metadata","click",()=>download("/api/meta?id="+$("record").value,"metadata.json"));
bind("confirmObs","click",async()=>{await post("confirm",{id:$("record").value,repeat:$("repeat").value.trim(),evidence:$("evidence").value.trim()});await refresh($("record").value)});
window.addEventListener("resize",draw);
(async()=>{state=await api("state");$("profile").replaceChildren(...state.profiles.map(p=>new Option(p.name,p.id)));
  if(state.profiles.some(p=>p.id===state.settings.profile))$("profile").value=state.settings.profile;
  $("volume").value=state.settings.volume??1;setup();await refresh();if(state.active)await watch(state.active)
})().catch(e=>$("error").textContent=e.message);
