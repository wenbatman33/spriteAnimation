"""Compress published images; keep lossless production inputs outside the web root.

Run after exports and catalog updates. Already optimized catalog entries are skipped
to avoid successive lossy recompression. Does not alter animation timing or poses.
"""
from pathlib import Path
from PIL import Image
import json,shutil,hashlib
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=Path('/Users/batman_work/codex-archives/banner-compression-inputs')
ads=json.loads((ROOT/'catalog.json').read_text());report=[]
for ad in ads:
 if ad.get('imageCompression')=='web15':continue
 p=ROOT/'assets'/ad['id'];original=ARCHIVE/ad['id']/ad['revision'];original.parent.mkdir(parents=True,exist_ok=True)
 if not original.exists():shutil.copytree(p,original)
 before=dict(ad['bytes']);old=original/ad['spinePath'];out=p/'spine-web15';out.mkdir(exist_ok=True)
 page=None;name=None;regions={}
 for line in (old/'banner.atlas').read_text().splitlines():
  if not line:continue
  if not line.startswith(' '):
   if line.endswith('.webp'):page=Image.open(old/line).convert('RGBA');name=None
   elif ':' not in line:name=line;regions[name]={'page':page}
  elif name:
   k,v=line.strip().split(':',1);regions[name][k]=v.strip()
 images={};aliases={};hashes={}
 for name,r in regions.items():
  x,y=map(int,r['xy'].split(','));w,h=map(int,r['size'].split(','));im=r['page'].crop((x,y,x+w,y+h))
  # Texture density ~1.4x display pixels; keep type at original resolution.
  ratio=1 if name in ['headline','cta'] else .7
  im=im.resize((max(1,round(w*ratio)),max(1,round(h*ratio))),Image.Resampling.LANCZOS)
  # APP uses held source poses. Share equivalent regions; keep all timeline keys.
  group=None
  if ad['id']=='app' and ad['revision']=='clean14' and name.startswith('character-'):
   n=int(name.split('-')[-1]);group=0 if n<15 or n>=90 else min(9,(n-15)//3) if n<45 else 9 if n<60 else 9-(n-60)//3
  key=('app-pose',group) if group is not None else ('exact',im.size,hashlib.sha256(im.tobytes()).hexdigest())
  if key in hashes:aliases[name]=hashes[key]
  else:images[name]=im;hashes[key]=name;aliases[name]=name
 sheet=Image.new('RGBA',(2048,2048));x=y=2;row=0;number=0;packed={};pages=[]
 def save_page():
  height=y+row+2;filename=f'texture-{number}.webp';sheet.crop((0,0,2048,height)).save(out/filename,quality=80,method=6,exact=True);pages.append((filename,2048,height))
 for name,im in images.items():
  if x+im.width+2>2048:x=2;y+=row+4;row=0
  if y+im.height+2>2048:save_page();number+=1;sheet=Image.new('RGBA',(2048,2048));x=y=2;row=0
  sheet.alpha_composite(im,(x,y));packed[name]=(number,x,y,im.width,im.height);x+=im.width+4;row=max(row,im.height)
 save_page();atlas=''
 for i,(filename,w,h) in enumerate(pages):
  atlas+=f'\n{filename}\nsize: {w},{h}\nformat: RGBA8888\nfilter: Linear,Linear\nrepeat: none\n'
  for name,target in aliases.items():
   n,x,y,rw,rh=packed[target]
   if n!=i:continue
   atlas+=f'{name}\n  rotate: false\n  xy: {x}, {y}\n  size: {rw}, {rh}\n  orig: {rw}, {rh}\n  offset: 0, 0\n  index: -1\n'
 (out/'banner.atlas').write_text(atlas);shutil.copy2(old/'banner.json',out/'banner.json')
 # Raster exports are encoded from pre-compression PNGs, not existing WebP files.
 source=Path('/Users/batman_work/codex-archives/five-original-production')/ad['id']/'rendered'
 frames=[Image.open(source/f'{i:03}.png').convert('RGB').resize((365,160),Image.Resampling.LANCZOS) for i in range(120)]
 frames[0].save(p/'poster.webp',quality=80,method=6)
 frames[0].save(p/'animation.webp',save_all=True,append_images=frames[1:],duration=[33,34,33]*40,loop=0,quality=68,method=6,minimize_size=True)
 for n in range(8):
  im=Image.new('RGB',(1825,480))
  for i,f in enumerate(frames[n*15:n*15+15]):im.paste(f,((i%5)*365,(i//5)*160))
  im.save(p/f'frames-{n}.webp',quality=70,method=6)
 shutil.rmtree(p/ad['spinePath']);ad['spinePath']='spine-web15';ad['revision']='web15';ad['imageCompression']='web15'
 ad['bytes'].update(webp=(p/'animation.webp').stat().st_size,js=sum((p/f'frames-{i}.webp').stat().st_size for i in range(8)),spine=sum(f.stat().st_size for f in out.iterdir()))
 report.append({'id':ad['id'],'before':before,'after':ad['bytes'],'spineRegions':len(regions),'uniqueRegions':len(images)})
 print(ad['id'],report[-1],flush=True)
(ROOT/'catalog.json').write_text(json.dumps(ads,ensure_ascii=False,indent=2))
if report:(ROOT/'COMPRESSION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
