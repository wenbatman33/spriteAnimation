from pathlib import Path
import json,zipfile
root=Path(__file__).resolve().parents[1];ads=json.loads((root/'catalog.json').read_text())
for ad in ads:
 p=root/'assets'/ad['id'];ad['bytes']['spine']=sum((p/f).stat().st_size for f in [str(f.relative_to(p)) for f in sorted((p/ad['spinePath']).iterdir()) if f.suffix in ['.json','.atlas','.webp']])
 for mode in ['js','spine']:
  files=[f'frames-{i}.webp' for i in range(ad['pages'])] if mode=='js' else [str(f.relative_to(p)) for f in sorted((p/ad['spinePath']).iterdir()) if f.suffix in ['.json','.atlas','.webp']]
  with zipfile.ZipFile(p/f'{mode}-package.zip','w',zipfile.ZIP_DEFLATED) as z:
   for f in files:z.write(p/f,f'assets/{ad["id"]}/{f}')
   for f in ['render.js','player.css']:z.write(root/f,f)
   if mode=='spine':z.write(root/'vendor/spine-player.js','vendor/spine-player.js')
   z.writestr('index.html','<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+ad['name']+'</title><link rel="stylesheet" href="player.css"><div id="banner" class="banner-surface" style="width:365px;height:160px"></div><script type="module">import{renderBanner}from"./render.js";renderBanner(document.querySelector("#banner"),'+json.dumps(ad,ensure_ascii=False)+',"'+mode+'");</script>')
   z.writestr('README.txt','將本資料夾完整上傳至 HTTP(S) 主機，開啟 index.html。無需 npm 或 build。展示尺寸365×160。')
(root/'catalog.json').write_text(json.dumps(ads,ensure_ascii=False,indent=2))
print('Updated 10 standalone packages and catalog')
