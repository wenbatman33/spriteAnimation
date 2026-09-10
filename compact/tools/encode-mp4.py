"""Encode lossless rendered frames, optionally to a per-banner byte budget."""
from pathlib import Path
import json,subprocess,sys,tempfile

STAGE=Path('/Users/batman_work/codex-archives/five-original-production')
def encode(id):
 p=STAGE/id;meta=json.loads((p/'meta.json').read_text()) if (p/'meta.json').exists() else {}
 base=['/opt/homebrew/bin/ffmpeg','-y','-loglevel','error','-framerate','30','-i',str(p/'rendered/%03d.png'),'-c:v','libx264','-preset','slow','-pix_fmt','yuv420p','-an']
 target=meta.get('videoTargetBytes')
 if target:
  # Reserve container overhead; two passes distribute bits over the full loop.
  bitrate=round((target-6000)*8/4)
  with tempfile.TemporaryDirectory(prefix='banner-x264-') as tmp:
   common=base+['-b:v',str(bitrate),'-passlogfile',str(Path(tmp)/'pass')]
   subprocess.run(common+['-pass','1','-f','null','/dev/null'],check=True)
   subprocess.run(common+['-pass','2','-movflags','+faststart',str(p/'animation.mp4')],check=True)
   actual=(p/'animation.mp4').stat().st_size
   if abs(actual-target)>target*.02:
    corrected=round(bitrate*(target-6000)/(actual-6000))
    common[common.index('-b:v')+1]=str(corrected)
    subprocess.run(common+['-pass','2','-movflags','+faststart',str(p/'animation.mp4')],check=True)
 else:
  subprocess.run(base+['-crf',str(meta.get('videoCrf',22)),'-movflags','+faststart',str(p/'animation.mp4')],check=True)
 print(id,(p/'animation.mp4').stat().st_size,'bytes',flush=True)

if __name__=='__main__':
 for id in sys.argv[1:]:encode(id)
