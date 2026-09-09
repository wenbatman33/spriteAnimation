// Three static sprite sheets, 45 forward frames and a reverse loop. No video decoder.
export async function createFramePlayer(host, id) {
 const images=await Promise.all([0,1,2].map(async page=>{
  const img=new Image();img.src=new URL(`../assets/frames/${id}/${page}.webp`,import.meta.url).href;
  await img.decode();return img;
 }));
 const window=document.createElement('div');window.className='frame-window';window.setAttribute('role','img');window.setAttribute('aria-label','JS 影格動畫');
 for(const img of images){img.alt='';img.className='frame-sheet';img.draggable=false;window.append(img);}
 host.replaceChildren(window);let previous=-1;
 return {
  update(seconds){const step=Math.floor(seconds*24)%88,frame=step<45?step:88-step;if(frame===previous)return;previous=frame;
   const page=Math.floor(frame/15),local=frame%15;
   images.forEach((img,i)=>{img.hidden=i!==page;});
   images[page].style.left=`-${local%5*100}%`;images[page].style.top=`-${Math.floor(local/5)*100}%`;window.dataset.frame=String(frame);
  },
  destroy(){host.replaceChildren();}
 };
}
