from pathlib import Path
import json,zipfile,sys
root=Path(__file__).resolve().parents[1];ads=json.loads((root/'catalog.json').read_text())
for ad in ads:
 if sys.argv[1:] and ad['id'] not in sys.argv[1:]:continue
 width,height=ad.get('width',365),ad.get('height',160)
 p=root/'assets'/ad['id'];ad['bytes']['spine']=sum((p/f).stat().st_size for f in [str(f.relative_to(p)) for f in sorted((p/ad['spinePath']).iterdir()) if f.suffix in ['.json','.atlas','.webp']])
 for mode in ['js','spine']+(['rive'] if 'rive' in ad['bytes'] else []):
  files=['animation.riv'] if mode=='rive' else [f'frames-{i}.webp' for i in range(ad['pages'])] if mode=='js' else [str(f.relative_to(p)) for f in sorted((p/ad['spinePath']).iterdir()) if f.suffix in ['.json','.atlas','.webp']]
  with zipfile.ZipFile(p/f'{mode}-package.zip','w',zipfile.ZIP_DEFLATED) as z:
   for f in files:z.write(p/f,f'assets/{ad["id"]}/{f}')
   for f in ['render.js','player.css']:z.write(root/f,f)
   if mode=='rive':
    for f in ['rive.js','rive.wasm','LICENSE']:z.write(root/'vendor/rive'/f,'vendor/rive/'+f)
   if mode=='spine':z.write(root/'vendor/spine-player.js','vendor/spine-player.js')
   z.writestr('index.html','<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+ad['name']+'</title><link rel="stylesheet" href="player.css"><div id="banner" class="banner-surface" style="width:'+str(width)+'px;max-width:100%;aspect-ratio:'+str(width)+'/'+str(height)+'"></div><script type="module">import{renderBanner}from"./render.js";renderBanner(document.querySelector("#banner"),'+json.dumps(ad,ensure_ascii=False)+',"'+mode+'");</script>')
   z.writestr('README.txt','將本資料夾完整上傳至 HTTP(S) 主機，開啟 index.html。無需 npm 或 build。展示尺寸'+str(width)+'×'+str(height)+'。')
(root/'catalog.json').write_text(json.dumps(ads,ensure_ascii=False,indent=2))
print('Updated selected standalone packages and catalog')
