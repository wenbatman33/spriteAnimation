"""Copy completed Luck18 exports and register both campaigns before compression."""
from pathlib import Path
import json,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
STAGE=Path('/Users/batman_work/codex-archives/five-original-production')
ads=json.loads((ROOT/'catalog.json').read_text())
for id,name in [('shield18','18神之盾现世 · 解锁终极宝藏'),('casino18','棋牌激情加码 · 返水日领18,888')]:
 if sys.argv[1:] and id not in sys.argv[1:]:continue
 source=STAGE/id;out=ROOT/'assets'/id;out.mkdir(exist_ok=True)
 for file in ['animation.mp4','animation.webp','poster.webp']+[f'frames-{i}.webp'for i in range(8)]:shutil.copy2(source/file,out/file)
 shutil.copytree(source/'spine-original',out/'spine-original',dirs_exist_ok=True)
 meta=json.loads((source/'meta.json').read_text())
 ad=dict(id=id,name=name,seconds=4,fps=30,forwardFrames=120,loopFrames=120,pages=8,revision='luck18-hd3',width=764,height=288,posterFrame=75,sourceFrame=[1528,576],fit='contain',spineMode='layered-character-action-and-effects',spinePath='spine-original',spineViewport=dict(x=0,y=0,width=764,height=288),spineBones=meta['spineBones'],spineLayers=meta['spineLayers'],bytes=dict(mp4=(out/'animation.mp4').stat().st_size,webp=(out/'animation.webp').stat().st_size,js=sum((out/f'frames-{i}.webp').stat().st_size for i in range(8)),spine=sum(f.stat().st_size for f in (out/'spine-original').iterdir())))
 ads=[a for a in ads if a['id']!=id];ads.append(ad)
(ROOT/'catalog.json').write_text(json.dumps(ads,ensure_ascii=False,indent=2))
print('Registered both Luck18 campaigns; now run optimize-delivery.py and package.py shield18 casino18')
