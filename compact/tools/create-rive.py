"""Experimental .riv 7.0 writer for image layers and linear keyframe tracks.

Uses Rive's published runtime object/property schema (rive-app/rive-cpp).
Embeds WebP assets once; writes real Rive image objects and animation keyframes.
This is a narrowly scoped authoring tool, not a general Spine-to-Rive converter.
"""
from pathlib import Path
from PIL import Image
import json,struct,io,math,hashlib
ROOT=Path(__file__).resolve().parents[1]
STAGE=Path('/Users/batman_work/codex-archives/five-original-production')
def uint(n):
 n=int(n);out=bytearray()
 while n>127:out.append((n&127)|128);n>>=7
 out.append(n);return bytes(out)
def value(v):
 if isinstance(v,float):return struct.pack('<f',v)
 if isinstance(v,int):return uint(v)
 if isinstance(v,str):v=v.encode()
 return uint(len(v))+v
def obj(kind,props):return uint(kind)+b''.join(uint(k)+value(v)for k,v in props.items())+b'\0'
def make(id):
 p=STAGE/id;sp=p/'spine-original';raw=json.loads((sp/'banner.json').read_text());poses=json.loads((p/'poses.json').read_text());regions={};name=None
 for line in (sp/'banner.atlas').read_text().splitlines():
  if not line:continue
  if not line.startswith(' '):
   if line.endswith('.webp'):page=Image.open(sp/line).convert('RGBA');name=None
   elif ':' not in line:name=line;regions[name]={'page':page}
  elif name:
   k,v=line.strip().split(':',1);regions[name][k]=v.strip()
 dimensions={i['name']:(i['width'],i['height'])for f in poses for i in f}
 images={};assets=[];hashes={}
 for name,r in regions.items():
  if name not in dimensions:continue
  x,y=map(int,r['xy'].split(','));w,h=map(int,r['size'].split(','));im=r['page'].crop((x,y,x+w,y+h));dw,dh=dimensions[name]
  density=1.5 if name in ['headline','brand-logo'] else 1.25
  im=im.resize((max(1,round(dw*density)),max(1,round(dh*density))),Image.Resampling.LANCZOS)
  buf=io.BytesIO();im.save(buf,format='WEBP',quality=80,method=6,exact=True);data=buf.getvalue();key=hashlib.sha256(data).digest()
  if key not in hashes:hashes[key]=len(assets);assets.append((name,im.width,im.height,data))
  images[name]=(hashes[key],im.width,im.height)
 out=bytearray(b'RIVE'+uint(7)+uint(0)+uint(0)+uint(0));out+=obj(23,{})
 for index,(name,w,h,data)in enumerate(assets):
  out+=obj(105,{203:name,204:index,208:float(w),207:float(h)})
  out+=obj(106,{212:data})
 out+=obj(1,{4:id,7:764.0,8:288.0,11:0.0,12:0.0})
 objects=[]
 # Rive draws siblings back-to-front; reverse Spine slot serialization order.
 for slot in reversed(raw['slots']):
  names=list(dict.fromkeys(i['name']for f in poses for i in f if i['slot']==slot['name']))
  for name in names:
   index=len(objects)+1;asset,w,h=images[name];tracks={k:[] for k in [13,14,15,16,17,18]}
   for f in poses:
    i=next(i for i in f if i['slot']==slot['name']);a,b,c,d,x,y=i['matrix'];sx=math.hypot(a,c);sy=(a*d-b*c)/sx if sx else 0
    vals=[x,288-y,-math.atan2(c,a),sx*dimensions[name][0]/w,sy*dimensions[name][1]/h,i['alpha'] if i['name']==name else 0]
    for k,v in zip(tracks,vals):tracks[k].append(float(v))
   for v in tracks.values():v.append(v[0])
   out+=obj(100,{4:name,5:0,206:asset,23:14 if i.get('add') else 3,**{k:v[0]for k,v in tracks.items()}})
   objects.append((index,tracks))
 out+=obj(31,{55:'idle',56:30,57:120,59:1})
 for index,tracks in objects:
  out+=obj(25,{51:index})
  for prop,vals in tracks.items():
   if max(vals)-min(vals)<.00001:continue
   out+=obj(26,{53:prop})
   # Translation/scale interpolate; pose opacity switches without ghosting.
   for frame,v in enumerate(vals):out+=obj(30,{67:frame,68:0 if prop==18 else 1,70:v})
 target=ROOT/'assets'/id/'animation.riv';target.write_bytes(out)
 stats={'id':id,'bytes':len(out),'embeddedImages':len(assets),'imageObjects':len(objects),'imageBytes':sum(len(a[3])for a in assets),'duration':4,'artboard':[764,288]}
 print(stats);return stats
if __name__=='__main__':
 (ROOT/'RIVE.json').write_text(json.dumps([make(id)for id in ['shield18','casino18']],indent=2))
