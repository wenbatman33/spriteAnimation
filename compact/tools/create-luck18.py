"""Two reference-directed campaigns. Offline authoring, no website build.

Preserve whole character silhouettes, register feet/waist, animate independent
Spine slots. No optical-flow blending or body slicing. Source logo is unchanged.
"""
from pathlib import Path
import importlib.util, json, math, sys
from PIL import Image, ImageOps
import numpy as np, cv2
spec=importlib.util.spec_from_file_location('creator',Path(__file__).with_name('create-original.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
SRC=m.SRC

def components(path, expected=8):
 im=Image.open(path).convert('RGBA');a=np.array(im)
 _,labels,stats,centers=cv2.connectedComponentsWithStats((a[:,:,3]>35).astype('uint8'),8)
 objects=[(i,b,c) for i,(b,c) in enumerate(zip(stats,centers)) if i and b[4]>1500]
 assert len(objects)==expected,(path,len(objects))
 objects.sort(key=lambda o:o[2][1]);ordered=[]
 for start in range(0,expected,4):ordered.extend(sorted(objects[start:start+4],key=lambda o:o[2][0]))
 out=[]
 for label,(x,y,w,h,_),center in ordered:
  # Connected silhouettes protect palms/sword tips that extend across nominal cells.
  mask=cv2.dilate((labels==label).astype('uint8'),np.ones((5,5),np.uint8))
  pixels=a.copy();pixels[:,:,3]*=mask
  out.append(Image.fromarray(pixels,'RGBA').crop((max(0,x-2),max(0,y-2),min(im.width,x+w+2),min(im.height,y+h+2))))
 return out

def sequence(s,name,images,x,y,keys):
 s.layer(name,images[0],x,y);del s.images[name];s.attach[name]={}
 for i,im in enumerate(images):
  key=f'{name}-{i:02}';s.images[key]=im;s.attach[name][key]={'width':im.width,'height':im.height}
 s.slots[-1]['attachment']=f'{name}-{keys[0][1]:02}'
 s.anim['slots'][name]={'attachment':[{'time':t,'name':f'{name}-{n:02}'} for t,n in keys]}

def registered(images,scale,canvas,anchor='feet'):
 out=[]
 for im in images:
  a=np.array(im)[:,:,3]
  if anchor=='feet':
   xs=np.where(a[int(im.height*.9):]>60)[1];cx=(int(xs.min())+int(xs.max()))/2
  else:
   # Waist center locks torso, independent of raised hand extent.
   xs=np.where(a[int(im.height*.93):]>60)[1];cx=(int(xs.min())+int(xs.max()))/2
  w,h=round(im.width*scale),round(im.height*scale)
  left=round(canvas[0]/2-cx*scale);top=canvas[1]-h
  assert left>=0 and left+w<=canvas[0] and top>=0,(left,top,w,h,canvas)
  frame=Image.new('RGBA',canvas);frame.alpha_composite(im.resize((w,h),Image.Resampling.LANCZOS),(left,top));out.append(frame)
 return out

def fxcell(im,box,w,h):return m.fit(m.tight(im.crop(box)),w,h)

def coins(s,im,count,cx,cy,spread,phase=0):
 for j in range(count):
  name=f'coin-{j}';s.layer(name,im,cx,cy,width=14+(j%3)*5)
  offset=(j/count+phase)%1;keys=[];alph=[]
  for n in range(121):
   t=n/30;p=(t/4+offset)%1
   keys.append((t,[(j/(count-1)-.5)*spread*p,210*math.sin(math.pi*p)-70*p]))
   alph.append((t,min(1,p*12,(1-p)*12)))
  s.track(name,'translate',keys);s.opacity(name,alph)
  s.track(name,'rotate',[(n/30,[360*n/120+45*j])for n in range(121)])
  s.track(name,'scale',[(n/30,[.25+.75*abs(math.cos(n/30*math.pi*2+j)),1])for n in range(121)])
  line=s.anim['bones'][name]['translate']
  for a,b in zip(line,line[1:]):
   if math.hypot(b['x']-a['x'],b['y']-a['y'])>30:a['curve']='stepped'

def create(id):
 src=SRC/id;s=m.Scene(id)
 s.layer('background',ImageOps.fit(Image.open(src/'background.png').convert('RGBA'),(750,330),method=Image.Resampling.LANCZOS),365,160)
 effects=Image.open(src/'effects.png').convert('RGBA')
 titles=Image.open(SRC/'shield18/titles.png').convert('RGBA')
 logo=m.fit(m.tight(Image.open(src/'logo.png').convert('RGBA')),70,78)
 if id=='shield18':
  dragon=[fxcell(effects,(i*443,0,(i+1)*443,434),192,190) for i in range(4)]
  # Match neck base rather than resizing each jaw opening independently.
  frames=[]
  for im in dragon:
   frame=Image.new('RGBA',(224,192));frame.alpha_composite(im,(224-im.width,192-im.height));frames.append(frame)
  dragon=frames
  sequence(s,'dragon',dragon,643,226,[(0,0),(.7,0),(.82,1),(.94,2),(1.06,3),(1.7,3),(1.85,2),(2,1),(2.15,0),(4,0)])
  s.sway('dragon',dy=2,angle=1)
  flame=fxcell(effects,(858,439,1334,884),330,170)
  s.layer('dragon-breath',flame,450,194)
  s.opacity('dragon-breath',[(0,0),(.95,0),(1.12,.8),(1.5,1),(1.85,0),(4,0)])
  s.track('dragon-breath','scale',[(0,[.1,.7]),(.95,[.1,.7]),(1.12,[1,1]),(1.5,[1.05,.85]),(1.85,[1.1,.5]),(4,[.1,.7])])
  aura=fxcell(effects,(1335,435,1774,887),265,265)
  s.layer('shield-aura',aura,177,151)
  s.opacity('shield-aura',[(0,.05),(.9,.05),(1.1,.85),(1.5,.55),(2.1,.05),(4,.05)])
  s.track('shield-aura','rotate',[(0,[0]),(4,[180])])
  hero=registered(components(src/'character.png'),.59,(280,300))
  sequence(s,'knight',hero,119,150,[(0,0),(.65,0),(.8,1),(.92,2),(1.04,3),(1.16,4),(1.4,5),(1.54,6),(1.66,7),(1.8,0),(4,0)])
  chest=fxcell(effects,(0,435,466,887),178,170)
  s.layer('treasure',chest,658,71);s.sway('treasure',dy=1)
  coin=fxcell(effects,(469,439,858,884),56,56);coins(s,coin,9,628,91,215)
  title=m.fit(m.tight(titles.crop((0,0,titles.width,447))),448,210)
  s.layer('headline',title,421,149);s.pulse('headline',.008)
  s.layer('brand-logo',logo,413,272)
 else:
  # Smaller partner behind heroine gives depth; cards never cover the key offer.
  man=fxcell(effects,(1125,413,1536,1024),185,245)
  s.layer('partner',man,77,122);s.sway('partner',dy=2,angle=.6)
  cards=[fxcell(effects,(0,410,394,970),70,100),fxcell(effects,(395,410,775,970),70,100)]
  for j in range(4):
   name=f'card-{j}';s.layer(name,cards[j%2],35+j*214,50+j%2*195)
   s.sway(name,dx=13,dy=14,angle=19,phase=j*1.1)
  woman=registered(components(src/'character.png'),.60,(290,292),'waist')
  sequence(s,'hostess',woman,204,146,[(0,0),(.6,0),(.72,1),(.84,2),(.96,3),(1.1,4),(1.24,3),(1.38,4),(1.52,5),(1.66,6),(1.8,7),(2,0),(4,0)])
  dice=[]
  for i in range(4):
   im=fxcell(effects,(i*384,0,(i+1)*384,410),65,65);frame=Image.new('RGBA',(70,70));frame.alpha_composite(im,((70-im.width)//2,(70-im.height)//2));dice.append(frame)
  for j in range(2):
   name=f'die-{j}';sequence(s,name,dice,310 if j==0 else 687,204 if j==0 else 49,[(round(n/12,6),(n+j)%4)for n in range(48)]+[(4,j)])
   s.sway(name,dx=13 if j==0 else 8,dy=29 if j==0 else 13,angle=24,phase=j)
  coin=fxcell(effects,(775,410,1123,1000),56,56);coins(s,coin,7,318,78,430,.15)
  title=m.fit(m.tight(titles.crop((0,447,titles.width,titles.height))),421,225)
  s.layer('headline',title,510,172)
  s.track('headline','scale',[(0,[1,1]),(1.1,[1,1]),(1.25,[1.025,1.025]),(1.5,[1,1]),(4,[1,1])])
  s.layer('brand-logo',logo,688,274)
 # Choreographed entrance, accent, reading hold, then a clean loop-out.
 def enter(name,start,duration,dx=0,dy=0,pop=False):
  end=start+duration;track=[]
  for n in range(121):
   t=n/30;p=max(0,min(1,(t-start)/duration));ease=1-(1-p)**3
   exit_at=3.4 if id=='casino18' else 3.65
   leave=max(0,min(1,(t-exit_at)/(4-exit_at)));leave=leave*leave*(3-2*leave)
   track.append((t,[dx*(1-ease),dy*(1-ease)-12*leave]))
  s.track(name,'translate',track)
  s.opacity(name,[(0,0),(start,0),(min(end,start+.16),1),(3.4 if id=='casino18' else 3.65,1),(4,0)] if start else [(0,0),(.16,1),(3.4 if id=='casino18' else 3.65,1),(4,0)])
  if pop:s.track(name,'scale',[(0,[.78,.78]),(start,[.78,.78]),(end-.09,[1.045,1.045]),(end,[1,1]),(4,[1,1])])
 if id=='shield18':
  enter('knight',0,.52,dx=-165)
  enter('dragon',.25,.55,dx=160)
  enter('treasure',.48,.48,dy=-130)
  enter('brand-logo',.62,.36,dy=38,pop=True)
  enter('headline',.92,.42,dy=-36,pop=True)
 else:
  enter('partner',.24,.38,dx=-130)
  enter('hostess',.04,.36,dx=-190)
  enter('brand-logo',.38,.28,dy=42,pop=True)
  enter('headline',1.42,.34,dx=165,pop=True)
  for j in range(4):enter(f'card-{j}',.18+j*.14,.38,dx=(-1 if j%2 else 1)*130,dy=-80)
  for j in range(2):enter(f'die-{j}',.42+j*.20,.32,dy=120,pop=True)
 if id=='casino18':
  for key in s.anim['slots']['hostess']['attachment']:
   if 0<key['time']<4:key['time']+=.62
 # Gate each coin until the offer has landed; preserve its original flight path.
 for name,timelines in s.anim['slots'].items():
  if name.startswith('coin-'):
   for key in timelines['color']:
    t=key['time'];a=int(key['color'][-2:],16)/255
    gate=max(0,min(1,(t-(1.8 if id=='casino18' else 1.25))/.25,((3.45 if id=='casino18' else 3.75)-t)/.25))
    key['color']='ffffff'+f'{round(a*gate*255):02x}'
 bones,layers=s.finish()
 (m.STAGE/id/'meta.json').write_text(json.dumps({'id':id,'spineBones':bones,'spineLayers':layers}))
 print(id,bones,'bones',layers,'layers')

if __name__=='__main__':
 for id in sys.argv[1:] or ['shield18','casino18']:create(id)
