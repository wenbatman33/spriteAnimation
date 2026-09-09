// 原生 ESM 多圖層動畫。所有畫面素材都載自 PNG；不生成圖案貼圖。
const PERIOD = 5.4;
export function reelPosition(seconds, column, once = false) {
  const cycle = once ? 0 : Math.floor(Math.max(0, seconds) / PERIOD);
  const phase = once ? Math.max(0, seconds) : Math.max(0, seconds) % PERIOD;
  const duration = 2.6 + column * 0.24;
  const delay = column * 0.08;
  const progress = Math.min(1, Math.max(0, (phase - delay) / duration));
  const ease = progress * progress * (3 - 2 * progress);
  const distance = 24 + column * 3;
  const position = column + (cycle + ease) * distance;
  return { offset: ((position % 6) + 6) % 6, moving: progress > 0 && progress < 1, stopped: phase >= duration + delay };
}

export function createWestern(host, gunnerSource) {
  host.innerHTML = `<div class="western-art"><img class="western-backdrop" src="./assets/western/background.webp" alt="夕陽西部城鎮與黃金老虎機"><div class="western-reels" aria-label="五列動畫轉輪">${Array.from({length:5},(_,column)=>`<div class="western-reel"><div class="western-strip">${Array.from({length:12},(_,i)=>`<div class="western-symbol"><div class="symbol-crop"><img src="./assets/western/symbols.webp" alt="${['警徽','牛仔帽','左輪','炸藥','馬蹄鐵','寶石'][i%6]}" style="top:${-(i%6)*100}%"></div></div>`).join('')}</div></div>`).join('')}</div><div class="western-gunner"><img src="${gunnerSource}" alt="牛仔猴子開槍動畫" draggable="false"></div></div><div class="western-controls"><label><input type="checkbox" data-shoot checked>連續開槍</label><label><input type="checkbox" data-reels checked>循環轉輪</label><button type="button" data-spin>轉動一次</button><span class="western-state">轉輪準備中</span></div>`;
  const scene=host.querySelector('.western-art'),gun=host.querySelector('.western-gunner'),img=gun.querySelector('img'),strips=[...host.querySelectorAll('.western-strip')],status=host.querySelector('.western-state');
  let alive=true,playing=true,autoShoot=true,autoReels=true,once=false,elapsed=0,last=0,lastFrame=-1,frame=0,raf=0;
  function setFrame(n){img.style.left=`-${n%3*100}%`;img.style.top=`-${Math.floor(n/3)*100}%`;gun.dataset.frame=String(n);gun.style.translate=n===2?'1.1% -0.7%':'0 0';}
  function drawReels(){let stopped=0;strips.forEach((strip,i)=>{const sample=reelPosition(elapsed,i,once);strip.style.transform=`translateY(-${sample.offset/12*100}%)`;strip.style.filter=playing&&sample.moving?'blur(.65px)':'none';strip.dataset.offset=sample.offset.toFixed(4);if(sample.stopped)stopped++;});status.textContent=!playing?'已暫停':stopped===5?'轉輪已停妥':autoReels||once?'轉輪滾動中':'轉輪已暫停';}
  host.querySelector('[data-shoot]').onchange=e=>{autoShoot=e.target.checked;setFrame(autoShoot?frame:0);};
  host.querySelector('[data-reels]').onchange=e=>{autoReels=e.target.checked;once=false;drawReels();};
  host.querySelector('[data-spin]').onclick=()=>{elapsed=0;once=true;host.dispatchEvent(new CustomEvent('western-resume',{bubbles:true}));drawReels();};
  function tick(now){if(!alive)return;const dt=last?Math.min((now-last)/1000,.08):0;last=now;if(playing&&(autoReels||once))elapsed+=dt;if(once&&elapsed>=4){elapsed=4;once=false;autoReels=false;host.querySelector('[data-reels]').checked=false;}drawReels();raf=requestAnimationFrame(tick);}
  raf=requestAnimationFrame(tick);
  return {
    update({frame:next,playing:active,flip,zoom}){if(!active&&next!==lastFrame)elapsed=next/5*(PERIOD-.1);playing=active;frame=next;lastFrame=next;setFrame(autoShoot?frame:0);scene.style.transform=`scale(${zoom}) scaleX(${flip?-1:1})`;drawReels();},
    destroy(){alive=false;cancelAnimationFrame(raf);host.innerHTML='';}
  };
}
