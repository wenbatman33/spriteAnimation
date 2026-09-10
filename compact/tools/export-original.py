"""Rasterize sampled Spine layers into matching JS, WebP and MP4 exports."""
from pathlib import Path
from PIL import Image
import cv2,numpy as np,json,subprocess,sys,math
STAGE=Path('/Users/batman_work/codex-archives/five-original-production')
IDS=['crown','thunder','app','line','duel']
def render(id,only_preview=False):
 p=STAGE/id;sp=p/'spine-original';images={};page=None;name=None;regions={}
 for line in (sp/'banner.atlas').read_text().splitlines():
  if not line:continue
  if not line.startswith(' '):
   if line.endswith('.webp'):page=Image.open(sp/line).convert('RGBA');name=None
   elif ':' not in line:name=line;regions[name]={'page':page}
  elif name:
   k,v=line.strip().split(':',1);regions[name][k]=v.strip()
 for name,r in regions.items():
  x,y=map(int,r['xy'].split(','));w,h=map(int,r['size'].split(','));a=np.array(r['page'].crop((x,y,x+w,y+h))).astype(np.float32)/255;a[:,:,:3]*=a[:,:,3:4];images[name]=a
 poses=json.loads((p/'poses.json').read_text());small=[];frames=p/'rendered';frames.mkdir(exist_ok=True)
 indices=[0,30,60,90] if only_preview else range(120)
 for i in indices:
  canvas=np.zeros((320,730,4),np.float32)
  for item in poses[i]:
   src=images[item['name']];h,w=src.shape[:2];a,b,c,d,tx,ty=item['matrix'];sx=item['width']/w;sy=item['height']/h;lx=-item['width']/2;ly=item['height']/2
   m=np.array([[a*sx,-b*sy,a*lx+b*ly+tx],[-c*sx,d*sy,320-c*lx-d*ly-ty]],np.float32)
   part=cv2.warpAffine(src,m,(730,320),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)*item['alpha'];alpha=part[:,:,3:4]
   if item['add']:canvas[:,:,:3]=np.minimum(1,canvas[:,:,:3]+part[:,:,:3]);canvas[:,:,3:4]=np.maximum(canvas[:,:,3:4],alpha)
   else:canvas=part+canvas*(1-alpha)
  im=Image.fromarray(np.uint8(np.clip(canvas[:,:,:3],0,1)*255),'RGB');im.save(frames/f'{i:03}.png');small.append(im.resize((365,160),Image.Resampling.LANCZOS))
 if only_preview:
  review=Image.new('RGB',(730,320))
  for j,im in enumerate(small):review.paste(im,((j%2)*365,(j//2)*160))
  review.save(p/'preview.jpg');return
 small[0].save(p/'poster.webp',quality=90,method=5)
 small[0].save(p/'animation.webp',save_all=True,append_images=small[1:],duration=[33,34,33]*40,loop=0,quality=78,method=4,minimize_size=True)
 for n in range(8):
  sheet=Image.new('RGB',(1825,480))
  for j,im in enumerate(small[n*15:n*15+15]):sheet.paste(im,((j%5)*365,(j//5)*160))
  sheet.save(p/f'frames-{n}.webp',quality=83,method=5)
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-loglevel','error','-framerate','30','-i',str(frames/'%03d.png'),'-c:v','libx264','-preset','slow','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(p/'animation.mp4')],check=True)
 print(id,'exported',flush=True)
if __name__=='__main__':
 preview='--preview' in sys.argv;ids=[x for x in sys.argv[1:] if x!='--preview'] or IDS
 for id in ids:render(id,preview)
