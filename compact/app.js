import{renderBanner,asset}from'./render.js';import{safeDestination}from'../src/url.js';
const ads=await(await fetch('./catalog.json')).json(),labels={js:'JS iframe',mp4:'MP4',webp:'WebP',spine:'Spine 2D'},q=new URLSearchParams(location.search),initial=Object.hasOwn(labels,q.get('format'))?q.get('format'):'mp4',motion=matchMedia('(prefers-reduced-motion: reduce)');let paused=motion.matches,selection=null,showBones=false;
const bytes=n=>n<1e6?`${Math.round(n/1000)} KB`:`${(n/1e6).toFixed(2)} MB`,cards=[];const $=s=>document.querySelector(s);
let choices={};try{choices=JSON.parse(localStorage.getItem('compact-choices')||'{}');}catch{}
function tabs(parent,value,action){for(const [id,label]of Object.entries(labels)){const b=document.createElement('button');b.type='button';b.textContent=label;b.dataset.format=id;b.setAttribute('aria-pressed',String(id===value));b.onclick=()=>action(id);parent.append(b);}}
tabs($('#global-formats'),initial,id=>{const url=new URL(location.href);url.searchParams.set('format',id);location.assign(url);});
async function mount(item){
 const token=++item.token;item.controller?.destroy();item.controller=null;const start=performance.now();item.status.textContent='載入中…';item.host.replaceChildren();item.host.dataset.format=item.format;for(const key of ['animationTime','animationPose','playback'])delete item.host.dataset[key];
 const ready=()=>{if(token!==item.token)return;item.status.textContent=`已就緒 · ${Math.round(performance.now()-start)} ms${item.format==='webp'?' · 請確認圖片有動':''}`;item.card.dataset.state='ready';};
 const error=e=>{if(token!==item.token)return;item.status.textContent='載入失敗 · '+e.message;item.card.dataset.state='error';};
 item.card.dataset.state='loading';item.facts.textContent=`素材 ${bytes(item.ad.bytes[item.format])} · ${item.format==='spine'?`${item.ad.spineLayers||0} 圖層 · ${item.ad.spineBones} 根骨骼 · 另需共用 runtime`:`${item.ad.seconds} 秒循環 · ${item.ad.fps} FPS`}`;
 for(const button of item.card.querySelectorAll('.tabs button'))button.setAttribute('aria-pressed',String(button.dataset.format===item.format));
 if(item.format==='js'){
  const f=document.createElement('iframe');f.title=item.ad.name+' JS iframe';const url=new URL('./play.html',import.meta.url);url.searchParams.set('id',item.ad.id);url.searchParams.set('format','js');if(paused)url.searchParams.set('paused','1');
  const handler=e=>{if(e.source!==f.contentWindow||e.origin!==location.origin||e.data?.source!=='compact-banner')return;if(e.data.type==='ready')ready();if(e.data.type==='error')error(Error(e.data.message));};addEventListener('message',handler);f.src=url;item.host.append(f);item.controller={pause(value){f.contentWindow.postMessage({source:'compact-studio',type:'pause',value},location.origin);},destroy(){removeEventListener('message',handler);f.remove();}};
 }else{
  const controller=await renderBanner(item.host,item.ad,item.format,{paused,onReady:ready,onError:error});if(token!==item.token)controller.destroy();else{item.controller=controller;controller.bones?.(showBones);}
 }
 updatePick(item);
}
function updatePick(item){item.pick.setAttribute('aria-pressed',String(choices[item.ad.id]===item.format));item.pick.textContent=choices[item.ad.id]===item.format?'✓ 已選此格式':'選擇此格式';}
for(const [index,ad]of ads.entries()){
 const card=document.createElement('article');card.className='card';card.innerHTML='<div class="card-head"><h2></h2><span class="kind">365 × 160</span></div><div class="stage-wrap"><div class="banner-surface"></div></div><p class="status" role="status">捲動至此載入</p><div class="card-body"><div class="tabs" role="group" aria-label="切換格式"></div><p class="facts"></p><div class="actions"><button class="quiet pick" aria-pressed="false">選擇此格式</button><button class="quiet deliver">下載／嵌入</button></div></div>';
 card.querySelector('h2').textContent=`0${index+1}  ${ad.name}`;const item={ad,card,host:card.querySelector('.banner-surface'),status:card.querySelector('.status'),facts:card.querySelector('.facts'),pick:card.querySelector('.pick'),format:initial,token:0,controller:null,visible:false};cards.push(item);
 tabs(card.querySelector('.tabs'),initial,id=>{item.format=id;mount(item);});item.pick.onclick=()=>{choices[ad.id]=item.format;try{localStorage.setItem('compact-choices',JSON.stringify(choices));}catch{}updatePick(item);};card.querySelector('.deliver').onclick=()=>openDelivery(item);item.facts.textContent=`素材 ${bytes(ad.bytes[initial])}`;updatePick(item);$('#cards').append(card);
}
const rigButton=document.createElement('button');rigButton.className='quiet';rigButton.textContent='顯示骨骼';rigButton.setAttribute('aria-pressed','false');document.querySelector('.toolbar').append(rigButton);rigButton.onclick=()=>{showBones=!showBones;rigButton.setAttribute('aria-pressed',String(showBones));rigButton.textContent=showBones?'隱藏骨骼':'顯示骨骼';cards.forEach(c=>c.controller?.bones?.(showBones));};
const observer=new IntersectionObserver(entries=>{for(const e of entries){const item=cards.find(c=>c.card===e.target);item.visible=e.isIntersecting;if(e.isIntersecting){if(!item.controller)mount(item);else item.controller.pause(paused);}else item.controller?.pause(true);}},{rootMargin:'50px'});cards.forEach(c=>observer.observe(c.card));
function updatePause(){ $('#pause').textContent=paused?'全部播放':'全部暫停';for(const c of cards)c.controller?.pause(paused||!c.visible);}
$('#pause').onclick=()=>{paused=!paused;updatePause();};motion.addEventListener('change',()=>{paused=motion.matches;updatePause();});updatePause();
function escape(s){return s.replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');}
function updateCode(){if(!selection)return;const{ad,format}=selection,url=safeDestination($('#url').value);let code;
 if(['js','spine'].includes(format)){const src=new URL('./play.html',import.meta.url);src.searchParams.set('id',ad.id);src.searchParams.set('format',format);if(url)src.searchParams.set('url',url);code=`<iframe src="${escape(src.href)}" title="${ad.name}" width="365" height="160" style="border:0;display:block" loading="lazy"></iframe>`;
 }else if(format==='mp4'){code=`<video src="${escape(asset(ad.id,'animation.mp4'))}" width="365" height="160" autoplay muted loop playsinline></video>`;}else code=`<img src="${escape(asset(ad.id,'animation.webp'))}" width="365" height="160" alt="${ad.name}">`;
 if(url&&!['js','spine'].includes(format))code=`<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${code}</a>`;$('#code').value=code;
}
function openDelivery(item){selection={ad:item.ad,format:item.format};$('#delivery-title').textContent=item.ad.name+' · '+labels[item.format];$('#delivery-note').textContent=['js','spine'].includes(item.format)?'可複製 iframe，或下載獨立素材包。素材包解壓縮上傳後，將 src 改成包內 index.html 的公開網址；本機網址僅供測試。':'下載單一檔案，或複製以下語法。正式投放請改用公開網址。';$('#delivery-links').replaceChildren();
 const files=item.format==='spine'?['spine-package.zip']:item.format==='js'?['js-package.zip']:[`animation.${item.format}`];
 for(const file of files){const a=document.createElement('a');a.href=asset(item.ad.id,file);a.download=item.ad.id+'-'+file;a.textContent='↓ 下載 '+(file.endsWith('zip')?'完整素材包':labels[item.format]);a.className='download';$('#delivery-links').append(a);}
 $('#url').value='';$('#copy-status').textContent='';updateCode();$('#delivery').showModal();
}
$('#url').oninput=updateCode;$('#close').onclick=()=>$('#delivery').close();$('#copy').onclick=async()=>{if($('#url').value.trim()&&!safeDestination($('#url').value)){$('#copy-status').textContent='活動網址請填完整 http:// 或 https://';return;}try{await navigator.clipboard.writeText($('#code').value);$('#copy-status').textContent='已複製';}catch{$('#code').select();$('#copy-status').textContent='請按 Command+C 或 Ctrl+C 複製';}};
$('#export').onclick=()=>{const data={createdAt:new Date().toISOString(),choices:ads.map(a=>({id:a.id,name:a.name,format:choices[a.id]||null}))};const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='banner-format-choices.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
