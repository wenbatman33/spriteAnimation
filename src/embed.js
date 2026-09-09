import {ads} from './ads.js?v=motion-correction-4';
import {safeDestination} from './url.js';
const params=new URLSearchParams(location.search),ad=ads.find(a=>a.id===params.get('id')),message=document.querySelector('#message');
if(!ad){message.textContent='找不到這款廣告，請重新取得嵌入碼。';}else{
 const img=document.querySelector('#image'),target=document.querySelector('#target'),button=document.querySelector('#pause'),motion=matchMedia('(prefers-reduced-motion: reduce)');let paused=motion.matches;
 const raw=params.get('url'),destination=safeDestination(raw);document.title=ad.name+'廣告';img.alt=ad.name+'，點擊了解活動';
 if(destination)target.href=destination;else{img.alt=ad.name+'廣告預覽';if(raw)message.textContent='活動連結格式不正確，請重新取得嵌入碼。';}
 img.onload=()=>{document.querySelector('#ad').hidden=false;if(!raw||destination)message.hidden=true;};img.onerror=()=>{message.hidden=false;message.textContent='廣告素材載入失敗，請稍後重新整理。';};
 function render(){img.src=new URL(`../assets/${ad.id}${paused?'-poster':''}.webp?v=${ad.bytes}`,import.meta.url).href;button.textContent=paused?'播放':'暫停';button.setAttribute('aria-pressed',String(paused));}
 button.onclick=()=>{paused=!paused;render();};motion.addEventListener('change',()=>{paused=motion.matches;render();});render();
}
