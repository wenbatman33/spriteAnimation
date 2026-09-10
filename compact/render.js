let spineReady;
function disposeSpine(p){
 if(!p)return;
 p.pause();p.stopRendering();clearTimeout(p.cancelId);
 // Spine 3.8 has no player.dispose(); allow its already queued draw to finish.
 requestAnimationFrame(()=>requestAnimationFrame(()=>{p.assetManager.dispose();p.sceneRenderer.dispose();}));
}
export const asset=(id,file)=>new URL(`./assets/${id}/${file}?v=${id==='casino18'?'luck18-rhythm3':id==='shield18'?'luck18-rhythm2':'web15'}`,import.meta.url).href;
function loadSpine(){return spineReady??=new Promise((resolve,reject)=>{if(globalThis.spine){resolve();return;}const script=document.createElement('script');script.src=new URL('./vendor/spine-player.js',import.meta.url);script.onload=resolve;script.onerror=()=>reject(Error('Spine 播放器載入失敗'));document.head.append(script);});}
export async function renderBanner(host,ad,format,{paused=false,onReady=()=>{},onError=()=>{}}={}){
 let alive=true,raf=0,player=null,v=null,elapsed=0,last=0,stopped=paused,bonesVisible=false,hasReported=false;
 const controller={bones(value){bonesVisible=value;if(player)player.config.debug.bones=value;},pause(value){stopped=value;if(v){if(value)v.pause();else v.play().catch(onError);}if(player){if(value)player.pause();else player.play();}},destroy(){alive=false;cancelAnimationFrame(raf);if(v){v.pause();v.removeAttribute('src');v.load();}disposeSpine(player);host.replaceChildren();}};
 host.replaceChildren();for(const key of ['animationTime','animationPose','playback'])delete host.dataset[key];host.dataset.format=format;host.dataset.state='loading';
 const ready=()=>{if(!alive||hasReported)return;hasReported=true;host.dataset.state='ready';onReady();};
 const fail=e=>{if(!alive)return;host.dataset.state='error';onError(e);};
 (async()=>{try{
  if(format==='mp4'){
   v=document.createElement('video');v.width=365;v.height=160;v.muted=true;v.loop=true;v.playsInline=true;v.controls=false;v.preload='auto';v.setAttribute('aria-label',ad.name+' MP4');host.append(v);v.onloadeddata=ready;v.onerror=()=>fail(Error('MP4 載入或解碼失敗'));v.src=asset(ad.id,'animation.mp4');if(!stopped)v.play().catch(()=>fail(Error('自動播放受限，請按播放')));
  }else if(format==='webp'){
   const img=new Image();img.alt=ad.name+' 動畫 WebP';img.width=365;img.height=160;img.onload=ready;img.onerror=()=>fail(Error('WebP 載入失敗'));img.src=asset(ad.id,stopped?'poster.webp':'animation.webp');host.append(img);controller.pause=value=>{stopped=value;img.src=asset(ad.id,value?'poster.webp':'animation.webp');};
  }else if(format==='js'){
   const images=await Promise.all(Array.from({length:ad.pages},(_,n)=>n).map(async n=>{const img=new Image();img.src=asset(ad.id,`frames-${n}.webp`);await img.decode();return img;}));if(!alive)return;
   const clip=document.createElement('div');clip.className='sprite-clip';clip.setAttribute('role','img');clip.setAttribute('aria-label',ad.name+' JS 逐格動畫');
   images.forEach(img=>{img.className='sprite-sheet';img.alt='';clip.append(img);});host.append(clip);
   let previous=-1;
   function tick(now){if(!alive)return;if(last&&!stopped&&!document.hidden)elapsed+=Math.max(0,Math.min((now-last)/1000,.1));last=now;const step=Math.floor(elapsed*ad.fps)%ad.loopFrames,frame=step<ad.forwardFrames?step:ad.loopFrames-step;
    if(previous!==frame){const page=Math.floor(frame/15),cell=frame%15;images.forEach((img,n)=>img.hidden=n!==page);images[page].style.left=`-${cell%5*100}%`;images[page].style.top=`-${Math.floor(cell/5)*100}%`;clip.dataset.frame=frame;previous=frame;}
    raf=requestAnimationFrame(tick);
   }raf=requestAnimationFrame(tick);ready();
  }else if(format==='spine'){
   await loadSpine();if(!alive)return;const viewport=ad.spineViewport||{x:0,y:0,width:730,height:320};
   player=new spine.SpinePlayer(host,{jsonUrl:asset(ad.id,`${ad.spinePath}/banner.json`),atlasUrl:asset(ad.id,`${ad.spinePath}/banner.atlas`),animation:'idle',loop:true,alpha:true,premultipliedAlpha:false,backgroundColor:'#00000000',showControls:false,showLoading:false,viewport:{...viewport,padLeft:'0%',padRight:'0%',padTop:'0%',padBottom:'0%'},success(p){if(!alive){disposeSpine(p);return;}player=p;p.config.debug.bones=bonesVisible;Object.assign(p.config.viewport,viewport);p.setAnimation('idle',true);p.previousViewport=null;if(stopped)p.pause();else p.play();let reported=false;function monitor(){if(!alive)return;host.dataset.animationTime=p.animationState.getCurrent(0).trackTime.toFixed(3);host.dataset.animationPose=p.skeleton.slots.map(s=>s.attachment?.name||'-').join('|');host.dataset.playback=p.paused?'paused':'playing';if(!reported){reported=true;ready();}raf=requestAnimationFrame(monitor);}raf=requestAnimationFrame(monitor);},error(p,error){fail(Error(String(error)));}});
   if(player.loadingScreen)player.loadingScreen.draw=()=>{};
  }else throw Error('未知格式');
 }catch(e){fail(e);}})();
 return controller;
}
