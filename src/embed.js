import {ads} from './ads.js?v=js-8';
import {createWestern} from './western.js';
import {createFramePlayer} from './frame-player.js';
import {safeDestination} from './url.js';
const params=new URLSearchParams(location.search),ad=ads.find(a=>a.id===params.get('id')),message=document.querySelector('#message');
async function start(){
 if(!ad){message.textContent='找不到這款廣告，請重新取得嵌入碼。';return;}
 const target=document.querySelector('#target'),button=document.querySelector('#pause'),motion=matchMedia('(prefers-reduced-motion: reduce)');
 const raw=params.get('url'),destination=safeDestination(raw);document.title=ad.name+' · JS 動畫';if(destination)target.href=destination;
 const host=document.createElement('div');host.className=ad.id==='western'?'western-host':'frames-host';host.setAttribute('aria-label',ad.name+' JS 動畫');target.append(host);
 let scene,alive=true,paused=motion.matches||params.get('paused')==='1',elapsed=0,last=0,raf=0;
 window.addEventListener('pagehide',()=>{alive=false;cancelAnimationFrame(raf);scene?.destroy();},{once:true});
 try{
  scene=ad.id==='western'?createWestern(host):await createFramePlayer(host,ad.id);
  if(ad.id==='western')await Promise.all([...host.querySelectorAll('img')].map(img=>img.decode()));
 }catch{scene?.destroy();message.textContent='JS 動畫素材載入失敗，請重新整理。';return;}
 if(!alive){scene.destroy();return;}
 function render(){button.textContent=paused?'播放':'暫停';button.setAttribute('aria-pressed',String(paused));
  if(ad.id==='western')scene.update({frame:Math.floor(elapsed*7)%6,playing:!paused,flip:false,zoom:1});else scene.update(elapsed);
 }
 function tick(now){if(last&&!paused&&!document.hidden)elapsed+=Math.min((now-last)/1000,.08);last=now;render();raf=requestAnimationFrame(tick);}
 button.onclick=()=>{paused=!paused;render();};motion.addEventListener('change',()=>{paused=motion.matches;render();});render();raf=requestAnimationFrame(tick);
 document.querySelector('#ad').hidden=false;message.hidden=!raw||Boolean(destination);if(!message.hidden)message.textContent='活動連結格式不正確，請重新取得嵌入碼。';
}
start();
