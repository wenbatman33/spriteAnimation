"""Author five original layered Spine banners from generated RGBA assets.

Offline asset production only; the website itself is native ESM and needs no build.
Requires Pillow, numpy and OpenCV. Keeps characters intact; optical flow creates
in-betweens, while Spine bones animate independent effects and lettering.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import cv2, json, math, sys

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'original-source'
STAGE=Path('/Users/batman_work/codex-archives/five-original-production')
STAGE.mkdir(parents=True,exist_ok=True)
IDS=['crown','thunder','app','line','duel']
FPS=30; COUNT=120
def tight(im,threshold=12):
 box=im.getchannel('A').point(lambda a:255 if a>threshold else 0).getbbox()
 return im.crop(box) if box else im
def fit(im,w,h):
 im=im.copy();im.thumbnail((w,h),Image.Resampling.LANCZOS);return im
def text_image(s,size=26):
 font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',size)
 box=font.getbbox(s);im=Image.new('RGBA',(box[2]-box[0]+16,box[3]-box[1]+16));ImageDraw.Draw(im).text((8-box[0],8-box[1]),s,font=font,fill='#fff1c5',stroke_width=2,stroke_fill='#24140b');return im
def poses(id,side=None):
 sheet=Image.open(SRC/f'five-{id}.png').convert('RGBA');cols,rows=(2,4) if id=='duel' else ((4,4) if id=='app' else (4,2))
 seq=[]
 if id in ['duel','app']:
  # The generated rows are NOT equally tall. Find each whole alpha silhouette;
  # a fixed grid otherwise imports the preceding character's boots and clips heads.
  pixels=np.array(sheet);_,labels,stats,centers=cv2.connectedComponentsWithStats((pixels[:,:,3]>35).astype('uint8'),8)
  figures=[(i,b,c) for i,(b,c) in enumerate(zip(stats,centers)) if i and b[4]>1500]
  assert len(figures)==16, 'Expected sixteen intact figures'
  figures.sort(key=lambda v:v[2][1]);ordered=[]
  for start in range(0,16,4):ordered.extend(sorted(figures[start:start+4],key=lambda v:v[2][0]))
  selected=[v for j,v in enumerate(ordered) if id=='app' or j%2==side]
  for label,(x,y,w,h,area),center in selected:
   mask=cv2.dilate((labels==label).astype('uint8'),np.ones((3,3),np.uint8));clean=pixels.copy();clean[:,:,3]*=mask
   seq.append(Image.fromarray(clean,'RGBA').crop((max(0,x-1),max(0,y-1),min(sheet.width,x+w+1),min(sheet.height,y+h+1))))
 else:
  for n in range(cols*rows):
   x,y=n%cols,n//cols;box=(round(x*sheet.width/cols),round(y*sheet.height/rows),round((x+1)*sheet.width/cols),round((y+1)*sheet.height/rows));im=sheet.crop(box)
   im=tight(im,28);seq.append(im)
 # A fixed canvas, fixed foot line and UNIFORM scale prevent stretched bodies.
 height=280 if id!='duel' else (238 if side==0 else 294)
 width=300 if id!='duel' else 220
 result=[]
 for im in seq:
  im=im.resize((round(im.width*height/im.height),height),Image.Resampling.LANCZOS)
  if im.width>width-8:im=fit(im,width-8,height)
  alpha=np.array(im)[:,:,3];bottom=alpha[round(im.height*.88):];xs=np.where(bottom>60)[1];anchor=float((xs.min()+xs.max())/2) if len(xs) else im.width/2
  layer=Image.new('RGBA',(width,320));layer.alpha_composite(im,(max(2,min(width-im.width-2,round(width/2-anchor))),310-im.height));result.append(layer)
 return result
def crisp(seq):
 # No optical-flow morph or alpha mixing: hold actual drawn poses on a timed loop.
 # Use the coherent lid-opening action; omit the unrelated lift/drop poses.
 action=[seq[i] for i in [0,1,4,5,6,7,8,9,10,11]]
 return [action[0] if n<15 or n>=90 else action[min(9,(n-15)//3)] if n<45 else action[9] if n<60 else action[9-(n-60)//3] for n in range(COUNT)]
def smooth(seq):
 h,w=np.array(seq[0]).shape[:2];xx,yy=np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32));flow=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
 arr=[np.array(im).astype(np.float32) for im in seq]
 for a in arr:a[:,:,:3]*=a[:,:,3:4]/255
 gray=[cv2.cvtColor(a[:,:,:3].astype(np.uint8),cv2.COLOR_RGB2GRAY) for a in arr]
 fields=[(flow.calc(gray[i],gray[(i+1)%len(seq)],None),flow.calc(gray[(i+1)%len(seq)],gray[i],None)) for i in range(len(seq))]
 out=[]
 for n in range(COUNT):
  p=n*len(seq)/COUNT;i=int(p)%len(seq);t=p-int(p);a,b=arr[i],arr[(i+1)%len(seq)];ab,ba=fields[i]
  # Motion-compensated premultiplied-alpha interpolation, not a crossfade.
  aa=cv2.remap(a,xx-ab[:,:,0]*t,yy-ab[:,:,1]*t,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  bb=cv2.remap(b,xx-ba[:,:,0]*(1-t),yy-ba[:,:,1]*(1-t),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  c=aa*(1-t)+bb*t;c[:,:,:3]=np.divide(c[:,:,:3]*255,c[:,:,3:4],out=np.zeros_like(c[:,:,:3]),where=c[:,:,3:4]>1)
  out.append(Image.fromarray(np.clip(c,0,255).astype('uint8'),'RGBA'))
 return out

class Scene:
 def __init__(self,id):
  self.id=id;self.out=STAGE/id/'spine-original';self.out.mkdir(parents=True,exist_ok=True);self.images={};self.bones=[{'name':'root'}];self.slots=[];self.attach={};self.anim={'bones':{},'slots':{}}
 def layer(self,name,image,x,y,width=None,height=None,blend=None,parent='root'):
  if width is None:width=image.width
  if height is None:height=image.height*width/image.width
  self.images[name]=image;self.bones.append({'name':name,'parent':parent,'x':x,'y':y});slot={'name':name,'bone':name,'attachment':name}
  if blend:slot['blend']=blend
  self.slots.append(slot);self.attach[name]={name:{'width':width,'height':height}};return name
 def sequence(self,name,frames,x,y):
  self.layer(name,frames[0],x,y);del self.images[name];self.attach[name]={}
  for i,im in enumerate(frames):
   key=f'{name}-{i:03}';self.images[key]=im;self.attach[name][key]={'width':im.width,'height':im.height}
  self.slots[-1]['attachment']=f'{name}-000';self.anim['slots'][name]={'attachment':[{'time':round(i/FPS,6),'name':f'{name}-{i:03}'} for i in range(COUNT)]+[{'time':4,'name':f'{name}-000'}]}
 def track(self,name,kind,values):
  fields={'rotate':['angle'],'translate':['x','y'],'scale':['x','y']}[kind]
  self.anim['bones'].setdefault(name,{})[kind]=[{'time':t,**dict(zip(fields,v))} for t,v in values]
 def sway(self,name,dx=0,dy=2,angle=0,phase=0):
  ts=[i/8 for i in range(33)]
  self.track(name,'translate',[(t,[dx*math.sin(t*math.pi/2+phase),dy*math.sin(t*math.pi/2+phase)]) for t in ts])
  if angle:self.track(name,'rotate',[(t,[angle*math.sin(t*math.pi/2+phase)]) for t in ts])
 def pulse(self,name,amount=.025,phase=0):
  self.track(name,'scale',[(i/8,[1+amount*math.sin(i/8*math.pi/2+phase)]*2) for i in range(33)])
 def opacity(self,name,values):
  self.anim['slots'].setdefault(name,{})['color']=[{'time':t,'color':'ffffff'+f'{round(a*255):02x}'} for t,a in values]
 def finish(self):
  atlas='';page=Image.new('RGBA',(2048,2048));x=y=2;rowh=0;pageno=0;regions=[]
  def save():
   nonlocal atlas
   usedh=min(2048,y+rowh+2);page.crop((0,0,2048,usedh)).save(self.out/f'texture-{pageno}.webp',quality=88,method=5,exact=True)
   atlas+=f'\ntexture-{pageno}.webp\nsize: 2048,{usedh}\nformat: RGBA8888\nfilter: Linear,Linear\nrepeat: none\n'+''.join(regions)
  for name,im in self.images.items():
   if x+im.width+2>2048:x=2;y+=rowh+4;rowh=0
   if y+im.height+2>2048:save();pageno+=1;page=Image.new('RGBA',(2048,2048));x=y=2;rowh=0;regions=[]
   page.alpha_composite(im,(x,y));regions.append(f'{name}\n  rotate: false\n  xy: {x}, {y}\n  size: {im.width}, {im.height}\n  orig: {im.width}, {im.height}\n  offset: 0, 0\n  index: -1\n');x+=im.width+4;rowh=max(rowh,im.height)
  save();(self.out/'banner.atlas').write_text(atlas)
  data={'skeleton':{'spine':'3.8.99','x':0,'y':0,'width':730,'height':320,'images':'./'},'bones':self.bones,'slots':self.slots,'skins':[{'name':'default','attachments':self.attach}],'animations':{'idle':self.anim}}
  (self.out/'banner.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
  return len(self.bones),len(self.slots)

def create(id):
 s=Scene(id);bg=ImageOps.fit(Image.open(SRC/f'five-bg-{id}.png').convert('RGBA'),(752,330),method=Image.Resampling.LANCZOS);s.layer('background',bg,365,160);s.sway('background',dx=3,dy=1)
 titles=Image.open(SRC/'five-titles.png');cuts=[0,315,615,925,1200,1536];i=IDS.index(id);title=tight(titles.crop((0,cuts[i],1024,cuts[i+1])),15)
 fx=Image.open(SRC/'five-fx.png');parts=[tight(fx.crop((j%3*512,j//3*512,j%3*512+512,j//3*512+512)),10) for j in range(6)]
 ring=fit(parts[min(i,3)],280,280)
 rx,ry={'crown':(558,164),'thunder':(542,166),'app':(120,160),'line':(157,157),'duel':(365,160)}[id]
 s.layer('aura',ring,rx,ry);s.track('aura','rotate',[(0,[0]),(4,[360])] if id in ['thunder','app'] else [(k/8,[12*math.sin(k/8*math.pi/2)]) for k in range(33)]);s.pulse('aura',.07);s.opacity('aura',[(0,.40),(1,.7),(2,.5),(3,.7),(4,.40)])
 if id=='duel':
  for side,(name,x,y) in enumerate([('fox',100,156),('ranger',618,160)]):
   seq=poses(id,side)[:6];seq=seq+seq[-2:0:-1]
   print(id,name,'flow',flush=True);s.sequence(name,smooth(seq),x,y);s.sway(name,dy=1.0,angle=.25,phase=side*math.pi)
 else:
  x,y={'crown':(560,155),'thunder':(585,151),'app':(593,160),'line':(154,151)}[id];print(id,'poses',flush=True);s.sequence('character',crisp(poses(id)) if id=='app' else smooth(poses(id)),x,y);s.sway('character',dy=1.5)
 # Foreground small effects, independently timed and never masking faces/hands.
 sparkle=fit(parts[5],54,54);coin=fit(parts[4],35,45)
 for j in range(6):
  name=f'spark-{j}';x=(80+j*113)%700+15;y=32+(j*59)%248;s.layer(name,sparkle,x,y,blend='additive');s.pulse(name,.35,j*.8);s.sway(name,dy=9,angle=15,phase=j)
  s.opacity(name,[(k/4,.04+.48*max(0,math.sin(k/4*math.pi+j))**5) for k in range(17)])
 if id in ['thunder','app','line']:
  for j in range(5):
   name=f'coin-{j}';cx,cy={'thunder':(442,118),'app':(568,138),'line':(260,137)}[id];s.layer(name,coin,cx,cy)
   s.track(name,'translate',[(k/8,[math.sin((k/8/4*2*math.pi)+j)* (50+j*8),math.cos(k/8/4*2*math.pi+j)*(35+j*9)]) for k in range(33)])
   s.track(name,'rotate',[(0,[j*40]),(4,[j*40+360])]);s.opacity(name,[(k/4,.05+.7*max(0,math.sin(k/4*math.pi/2+j))**3) for k in range(17)])
 placement={'crown':(240,190,450,180),'thunder':(253,218,465,165),'app':(337,197,375,185),'line':(473,211,446,160),'duel':(365,179,418,175)}[id]
 tx,ty,tw,th=placement;title=fit(title,tw,th);s.layer('headline',title,tx,ty);s.pulse('headline',.012,math.pi/2)
 cta={'crown':'解鎖限量榮耀頭框  ›','thunder':'投注榜開打  ›','app':'立即下載  ›','line':'領 $2000  ·  前往 LINE@  ›','duel':'中西強檔 · 巔峰對決'}[id]
 ci=text_image(cta,25 if id!='line' else 24);ci=fit(ci,430,45);cx,cy={'crown':(231,64),'thunder':(249,68),'app':(337,70),'line':(477,81),'duel':(365,65)}[id];s.layer('cta',ci,cx,cy);s.pulse('cta',.035)
 bones,layers=s.finish();return {'id':id,'spineBones':bones,'spineLayers':layers}

if __name__=='__main__':
 ids=sys.argv[1:] or IDS
 for id in ids:
  meta=create(id);(STAGE/id/'meta.json').write_text(json.dumps(meta));print(id,'packed',meta,flush=True)
