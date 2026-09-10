"""Check complete APP/western silhouettes before exporting advertising assets."""
import importlib.util
from pathlib import Path
import numpy as np, cv2
from PIL import Image
p=Path(__file__).with_name('create-original.py');spec=importlib.util.spec_from_file_location('creator',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
review=Image.new('RGB',(8*150,4*160),'#24333d')
for name,side,row in [('app',None,0),('duel',0,2),('duel',1,3)]:
 frames=m.poses(name,side)
 for i,im in enumerate(frames):
  a=np.array(im)[:,:,3];mask=(a>35).astype('uint8');_,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
  bodies=[s for s in stats[1:] if s[4]>100];assert len(bodies)==1,(name,side,i,'detached piece')
  x,y,w,h,_=bodies[0];assert y>=8 and y+h<=313,(name,side,i,'head/feet at edge')
  assert x>=2 and x+w<=im.width-2,(name,side,i,'side clipping')
  thumb=im.resize((round(im.width/2),160));review.paste(thumb,((i%8)*150,(row+i//8)*160),thumb)
 print(name,side,len(frames),'complete silhouettes, no disconnected head/boot fragments')
review.save('/tmp/cutout-review14.jpg')
