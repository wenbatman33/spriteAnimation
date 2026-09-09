import {ads} from './ads.js?v=mp4-5';
import {safeDestination} from './url.js';
const params=new URLSearchParams(location.search),ad=ads.find(a=>a.id===params.get('id')),message=document.querySelector('#message');
if(!ad){message.textContent='找不到這款廣告，請重新取得嵌入碼。';}else{
 const video=document.querySelector('#image'),target=document.querySelector('#target'),button=document.querySelector('#pause'),motion=matchMedia('(prefers-reduced-motion: reduce)');let paused=motion.matches;
 const raw=params.get('url'),destination=safeDestination(raw);document.title=ad.name+'廣告';video.setAttribute('aria-label',ad.name+'廣告');
 if(destination)target.href=destination;else if(raw)message.textContent='活動連結格式不正確，請重新取得嵌入碼。';
 video.muted=true;video.poster=new URL(`../assets/${ad.id}-poster.webp?v=${ad.bytes}`,import.meta.url).href;
 document.querySelector('#ad').hidden=false;if(!raw||destination)message.hidden=true;
 function updateButton(){button.textContent=paused?'播放':'暫停';button.setAttribute('aria-pressed',String(paused));}
 async function render(){updateButton();if(paused){video.pause();return;}if(!video.src)video.src=new URL(`../assets/${ad.id}.mp4?v=${ad.mp4Bytes}`,import.meta.url).href;try{await video.play();if(paused)video.pause();}catch{paused=true;updateButton();}}
 video.onerror=()=>{paused=true;updateButton();message.hidden=false;message.textContent='影片載入失敗，請稍後重新整理。';};
 button.onclick=()=>{paused=!paused;render();};motion.addEventListener('change',()=>{paused=motion.matches;render();});render();
}
