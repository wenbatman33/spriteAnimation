"""Curse and Rebirth: discrete facial acting and separately animated flying bats."""
from pathlib import Path
from PIL import Image,ImageOps
import importlib.util,json,math,numpy as np,cv2
spec=importlib.util.spec_from_file_location('creator',Path(__file__).with_name('create-original.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
src=m.ROOT/'original-source/vampire';s=m.Scene('vampire')
def figures(path,count):
 im=Image.open(path).convert('RGBA');a=np.array(im);_,labels,stats,centers=cv2.connectedComponentsWithStats((a[:,:,3]>35).astype('uint8'),8)
 found=[(i,st,c) for i,(st,c) in enumerate(zip(stats,centers)) if i and st[4]>1000];assert len(found)==count,(path,len(found))
 found.sort(key=lambda v:v[2][1]);ordered=[]
 for n in range(0,count,4):ordered.extend(sorted(found[n:n+4],key=lambda v:v[2][0]))
 result=[]
 for label,(x,y,w,h,_),c in ordered:
  mask=cv2.dilate((labels==label).astype('uint8'),np.ones((3,3),np.uint8));p=a.copy();p[:,:,3]*=mask;result.append((Image.fromarray(p,'RGBA').crop((x,y,x+w,y+h)),(x,y,w,h)))
 return result
portraits=[]
for im,box in figures(src/'character.png',12):
 im=m.fit(im,338,310);frame=Image.new('RGBA',(342,320));frame.alpha_composite(im,((342-im.width)//2,320-im.height));portraits.append(frame)
bat_images=[];anchors=[(250,300),(687,315),(1122,307),(1584,310),(251,698),(693,700),(1125,701),(1580,705)]
for (im,(x,y,w,h)),(ax,ay) in zip(figures(src/'bats.png',8),anchors):
 frame=Image.new('RGBA',(128,128));im=im.resize((round(w*.2),round(h*.2)),Image.Resampling.LANCZOS);frame.alpha_composite(im,(round(64+(x-ax)*.2),round(64+(y-ay)*.2)));bat_images.append(frame)
bg=ImageOps.fit(Image.open(src/'background.png').convert('RGBA'),(750,330),method=Image.Resampling.LANCZOS);s.layer('background',bg,365,160);s.sway('background',dx=2,dy=.6)
def sequence(name,images,order,x,y,width):
 s.layer(name,images[0],x,y,width=width);del s.images[name];s.attach[name]={}
 for i,im in enumerate(images):
  key=f'{"wing" if name.startswith("bat") else name}-{i:02}';s.images[key]=im;s.attach[name][key]={'width':width,'height':width*im.height/im.width}
 keys=list(s.attach[name]);s.slots[-1]['attachment']=keys[order[0]];s.anim['slots'][name]={'attachment':[{'time':round(i/30,6),'name':keys[k]} for i,k in enumerate(order)]+[{'time':4,'name':keys[order[0]]}]}
for j in range(8):
 name=f'bat-{j}';phase=j/8;size=60+j%3*24
 sequence(name,bat_images,[(int(i/30*14+j*1.7)%8) for i in range(120)],0,0,size)
 # The wrap occurs outside the viewport; the visible path stays continuous.
 keys=[]
 for i in range(121):
  t=i/30;p=(t/4+phase)%1;keys.append((t,[-125+1000*p,260+(j%3)*15+16*math.sin(p*math.pi*2+j)]))
 s.track(name,'translate',keys);s.track(name,'rotate',[(i/30,[8*math.sin(i/30*math.pi+j)]) for i in range(121)])
 timeline=s.anim['bones'][name]['translate']
 for current,nxt in zip(timeline,timeline[1:]):
  if nxt['x']<current['x']:current['curve']='stepped'
order=[]
for n in range(120):
 t=n/30
 k=0 if t<.5 else min(7,1+int((t-.5)*10)) if t<1.2 else 6+(int((t-1.2)*5)%2) if t<2.4 else min(11,8+int((t-2.4)*6)) if t<3.1 else 0
 order.append(k)
sequence('vampire',portraits,order,172,160,342)
s.track('vampire','translate',[(i/30,[0,1.4*math.sin(i/30*math.pi*8)*max(0,math.sin((i/30-1.2)/1.2*math.pi)) if 1.2<i/30<2.4 else 0]) for i in range(121)])
title=m.fit(m.tight(Image.open(src/'title.png').convert('RGBA')),418,216);s.layer('headline',title,512,158);s.pulse('headline',.012)
s.layer('cta',m.text_image('立即探索  ›',25),512,29);s.pulse('cta',.025)
bones,layers=s.finish();(m.STAGE/'vampire/meta.json').write_text(json.dumps({'id':'vampire','spineBones':bones,'spineLayers':layers}))
review=Image.new('RGB',(6*171,2*160),'#20313a')
for i,im in enumerate(portraits):review.paste(im.resize((171,160)),((i%6)*171,(i//6)*160),im.resize((171,160)))
review.save('/tmp/vampire-poses.jpg');print('Vampire scene:',bones,'bones,',layers,'layers, 12 facial poses and 8 wingbeat poses')
