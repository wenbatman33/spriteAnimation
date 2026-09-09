import {ads} from './ads.js?v=mp4-5';
import {safeDestination} from './url.js';
const $=s=>document.querySelector(s),dialog=$('#delivery'),motion=matchMedia('(prefers-reduced-motion: reduce)');
const requestedFormat=new URLSearchParams(location.search).get('format');
const defaultFormat=['iframe','mp4','webp'].includes(requestedFormat)?requestedFormat:'mp4';
let paused=motion.matches,selected=null,mode='iframe';
for(const button of document.querySelectorAll('[data-default-format]')){button.setAttribute('aria-pressed',String(button.dataset.defaultFormat===defaultFormat));button.onclick=()=>{const url=new URL(location.href);url.searchParams.set('format',button.dataset.defaultFormat);location.assign(url.href);};}
$('#default-format-note').textContent=`本次預設：${defaultFormat==='iframe'?'iframe / JS':defaultFormat.toUpperCase()}。切換會重新載入；卡片仍可個別切換。`;
const media=(id,poster=false)=>new URL(`../assets/${id}${poster?'-poster':''}.webp?v=${ads.find(ad=>ad.id===id)?.bytes}`,import.meta.url).href;
const videoMedia=id=>new URL(`../assets/${id}.mp4?v=${ads.find(ad=>ad.id===id)?.mp4Bytes}`,import.meta.url).href;
const size=n=>n<1e6?`${Math.round(n/1000)} KB`:`${(n/1e6).toFixed(2)} MB`;
$('#count').textContent=`${ads.length} 款`;
const cards=[];
function mountPreview(host,ad,format,stopped=false){
 const old=host.querySelector('video');if(old)old.pause();host.replaceChildren();
 const status=document.createElement('p');status.className='playback-status';status.setAttribute('role','status');
 const labels={iframe:ad.id==='western'?'iframe · JS 分層動畫':'iframe · JS 影格動畫',mp4:'MP4 · 原生影片',webp:'WebP · 原生圖片'};
 status.textContent=labels[format]+' · 載入中';
 let element;
 if(format==='iframe'){
  element=document.createElement('iframe');element.title=ad.name+' iframe 預覽';
  const url=new URL('../embed.html',import.meta.url);url.searchParams.set('id',ad.id);if(stopped)url.searchParams.set('paused','1');
  if(selected===ad&&host.id==='preview-host'){const destination=safeDestination($('#destination').value);if(destination)url.searchParams.set('url',destination);}
  element.onload=()=>{status.textContent=labels[format]+' · 頁面已載入，請確認動畫有播放';};element.src=url.href;
 }else if(format==='mp4'){
  element=document.createElement('video');element.muted=true;element.loop=true;element.playsInline=true;element.controls=false;element.poster=media(ad.id,true);element.setAttribute('aria-label',ad.name+' MP4 預覽');
  element.onloadeddata=()=>{status.textContent=labels[format]+' · 已解碼';};element.onplaying=()=>{status.textContent=labels[format]+' · 播放中';};element.onpause=()=>{status.textContent=labels[format]+' · 已暫停';};element.src=videoMedia(ad.id);
  if(!stopped)element.play().catch(()=>{if(host.contains(element))status.textContent=labels[format]+' · 尚未自動播放，請使用上方播放預覽按鈕';});
 }else{
  element=document.createElement('img');element.alt=ad.name+' WebP 預覽';element.onload=()=>{status.textContent=labels[format]+(stopped?' · 靜態預覽':' · 圖片已載入，請確認動畫有播放');};element.src=media(ad.id,stopped);
 }
 element.onerror=()=>{status.textContent=labels[format]+' · 載入失敗，可能是格式不支援或網路問題';};
 const art=document.createElement('div');art.className='art';art.append(element);host.append(art,status);
}
for(const ad of ads){
 const card=document.createElement('article');card.className='card';card.innerHTML='<div class="card-preview"></div><div class="info"><div class="title-row"><h3></h3><span class="badge">格式比較</span></div><p class="facts"></p><div class="card-actions" role="group" aria-label="切換預覽格式"><button type="button" data-format="iframe">iframe</button><button type="button" data-format="mp4">MP4</button><button type="button" data-format="webp">WebP</button></div><button class="primary obtain" type="button">取得此格式廣告</button></div>';
 card.querySelector('h3').textContent=ad.name;card.querySelector('.facts').textContent=`600 × 400 · MP4 ${size(ad.mp4Bytes)} · WebP ${size(ad.bytes)}`;
 const entry={card,ad,format:defaultFormat,visible:false};cards.push(entry);
 for(const button of card.querySelectorAll('[data-format]')){button.setAttribute('aria-pressed',String(button.dataset.format===defaultFormat));button.onclick=()=>{entry.format=button.dataset.format;for(const b of card.querySelectorAll('[data-format]'))b.setAttribute('aria-pressed',String(b===button));mountPreview(card.querySelector('.card-preview'),ad,entry.format,paused);};}
 card.querySelector('.obtain').onclick=()=>openAd(ad,entry.format);$('#gallery').append(card);
 const art=document.createElement('div');art.className='art';card.querySelector('.card-preview').append(art);
}
const observer=new IntersectionObserver(entries=>{for(const e of entries){const item=cards.find(c=>c.card===e.target);item.visible=e.isIntersecting;if(item.visible)mountPreview(item.card.querySelector('.card-preview'),item.ad,item.format,paused);else{const host=item.card.querySelector('.card-preview');const v=host.querySelector('video');if(v)v.pause();const f=host.querySelector('iframe');if(f)f.src='about:blank';}}},{rootMargin:'100px'});
for(const item of cards)observer.observe(item.card);
function renderMotion(){for(const item of cards)if(item.visible)mountPreview(item.card.querySelector('.card-preview'),item.ad,item.format,paused);$('#motion').textContent=paused?'播放預覽':'暫停預覽';$('#motion').setAttribute('aria-pressed',String(paused));}
$('#motion').onclick=()=>{paused=!paused;renderMotion();};motion.addEventListener('change',()=>{paused=motion.matches;renderMotion();});renderMotion();
function saved(id){try{return localStorage.getItem('banner-destination:'+id)||'';}catch{return '';}}
function remember(id,value){try{localStorage.setItem('banner-destination:'+id,value);}catch{}}
function setMode(next){mode=next;$('#iframe-panel').hidden=mode!=='iframe';$('#webp-panel').hidden=mode!=='webp';$('#mp4-panel').hidden=mode!=='mp4';for(const button of document.querySelectorAll('[data-mode]'))button.setAttribute('aria-pressed',String(button.dataset.mode===mode));$('#status').textContent='';if(selected)mountPreview($('#preview-host'),selected,mode,paused);}
function makeURL(){const url=new URL('../embed.html',import.meta.url);url.searchParams.set('id',selected.id);const destination=safeDestination($('#destination').value);if(destination)url.searchParams.set('url',destination);return url;}
function refresh(){const value=$('#destination').value.trim(),destination=safeDestination(value);$('#url-error').hidden=!value||Boolean(destination);$('#url-error').textContent='請填寫完整的 https:// 或 http:// 活動網址。';const url=makeURL();if(mode==='iframe')mountPreview($('#preview-host'),selected,mode,paused);const escape=s=>s.replaceAll('&','&amp;').replaceAll('"','&quot;').replaceAll('<','&lt;');$('#code').value=`<iframe src="${escape(url.href)}" title="${selected.name}廣告" width="600" height="400" style="display:block;width:100%;max-width:600px;height:auto;aspect-ratio:3/2;border:0" loading="lazy"></iframe>`;if(destination||!value)remember(selected.id,destination||'');$('#status').textContent='';}
function openAd(ad,next){selected=ad;$('#dialog-title').textContent=ad.name;$('#facts').textContent=`600 × 400 · MP4 ${size(ad.mp4Bytes)} · WebP ${size(ad.bytes)} · ${ad.seconds} 秒循環 · ${ad.id==='western'?'iframe 使用 JS 分層動畫；MP4／WebP 為輸出檔':'iframe 使用 JS 影格動畫；MP4／WebP 為輸出檔'}`;$('#destination').value=saved(ad.id);$('#download-mp4').href=videoMedia(ad.id);$('#download-mp4').download=`${ad.id}-600x400.mp4`;$('#download-mp4').textContent=`↓ 下載 MP4（${size(ad.mp4Bytes)}）`;$('#download').href=media(ad.id);$('#download').download=`${ad.id}-600x400.webp`;$('#download').textContent=`↓ 下載動畫 WebP（${size(ad.bytes)}）`;const local=['127.0.0.1','localhost','[::1]'].includes(location.hostname);$('#hosting').textContent=local?'目前為本機測試。正式投放前，請將此系統上傳到公開 HTTPS 網址，再從該網址複製嵌入碼。':'嵌入碼會從本站載入動畫；廣告點擊後另開活動頁。';setMode(next);refresh();dialog.showModal();}
$('#destination').addEventListener('change',refresh);
for(const b of document.querySelectorAll('[data-mode]'))b.onclick=()=>setMode(b.dataset.mode);
$('#close').onclick=()=>dialog.close();dialog.addEventListener('close',()=>{const value=$('#destination').value.trim(),destination=safeDestination(value);if(selected&&(destination||!value))remember(selected.id,destination||'');const video=$('#preview-host').querySelector('video');if(video)video.pause();$('#preview-host').replaceChildren();});
$('#copy').onclick=async()=>{const destination=safeDestination($('#destination').value);if(!destination){$('#url-error').hidden=false;$('#url-error').textContent='先填入活動網址，客戶點廣告才有地方可以前往。';$('#destination').focus();return;}refresh();try{await navigator.clipboard.writeText($('#code').value);$('#status').textContent='已複製！貼到網站的 HTML 區塊即可。';}catch{$('#code').focus();$('#code').select();$('#status').textContent='已選取嵌入碼，請按 Command+C 或 Ctrl+C 複製。';}};
