"""Export the last two banners at 531x200 from archived lossless frames."""
from pathlib import Path
from PIL import Image,ImageOps
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
STAGE=Path('/Users/batman_work/codex-archives/five-original-production')
ads=json.loads((ROOT/'catalog.json').read_text())
for ad in ads:
 if ad['id'] not in ['shield18','casino18']:continue
 p=ROOT/'assets'/ad['id'];source=STAGE/ad['id']/'rendered';work=STAGE/ad['id']/'delivery-531';work.mkdir(exist_ok=True)
 small=[]
 for i in range(120):
  with Image.open(source/f'{i:03}.png') as image:
   # Uniform cover resize; less than 0.2px is cropped, never stretch characters.
   frame=ImageOps.fit(image.convert('RGB'),(1062,400),method=Image.Resampling.LANCZOS)
   frame.save(work/f'{i:03}.png');small.append(ImageOps.fit(image.convert('RGB'),(531,200),method=Image.Resampling.LANCZOS))
 small[75].save(p/'poster.webp',quality=85,method=6)
 small[0].save(p/'animation.webp',save_all=True,append_images=small[1:],duration=[33,34,33]*40,loop=0,quality=72,method=6,minimize_size=True)
 for n in range(8):
  sheet=Image.new('RGB',(2655,600))
  for j,im in enumerate(small[n*15:n*15+15]):sheet.paste(im,((j%5)*531,(j//5)*200))
  sheet.save(p/f'frames-{n}.webp',quality=74,method=6)
 subprocess.run(['ffmpeg','-y','-v','error','-framerate','30','-i',str(work/'%03d.png'),'-c:v','libx264','-preset','slow','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(p/'animation.mp4')],check=True)
 spine=p/ad['spinePath']/'banner.json';data=json.loads(spine.read_text());root=data['bones'][0];assert root['name']=='root'
 scale=531/764;root.update(scaleX=scale,scaleY=scale,x=0,y=(200-288*scale)/2)
 data['skeleton'].update(x=0,y=0,width=531,height=200);spine.write_text(json.dumps(data,separators=(',',':')))
 ad.update(width=531,height=200,sourceFrame=[1062,400],spineViewport={'x':0,'y':0,'width':531,'height':200},revision='luck18-531-v1')
 for fmt in ['mp4','webp']:ad['bytes'][fmt]=(p/f'animation.{fmt}').stat().st_size
 ad['bytes']['js']=sum((p/f'frames-{i}.webp').stat().st_size for i in range(8))
 print(ad['id'],ad['bytes'],flush=True)
(ROOT/'catalog.json').write_text(json.dumps(ads,ensure_ascii=False,indent=2))
