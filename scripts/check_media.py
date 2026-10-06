from pathlib import Path
import subprocess,json,struct
import imageio_ffmpeg
r=Path(__file__).resolve().parents[1];ff=imageio_ffmpeg.get_ffmpeg_exe();checks=[]
for p in sorted((r/'assets/videos').rglob('*.mp4')):
 result=subprocess.run([ff,'-v','error','-i',str(p),'-frames:v','1','-f','null','-'],capture_output=True,text=True)
 atoms=[]
 with p.open('rb') as file:
  while file.tell()<p.stat().st_size:
   hdr=file.read(8)
   if len(hdr)<8:break
   size,typ=struct.unpack('>I4s',hdr)
   if size==1:size=struct.unpack('>Q',file.read(8))[0];header=16
   else:header=8
   atoms.append(typ.decode('ascii',errors='replace'))
   if size<header:break
   file.seek(size-header,1)
 checks.append({'path':str(p.relative_to(r)),'firstFrameDecoded':result.returncode==0,'fastStart':atoms.index('moov')<atoms.index('mdat') if 'moov' in atoms and 'mdat' in atoms else False,'bytes':p.stat().st_size})
report={'videos':len(checks),'errors':[x for x in checks if not x['firstFrameDecoded'] or not x['fastStart']],'checks':checks}
(r/'docs/video-validation.json').write_text(json.dumps(report,indent=2));print('Videos checked',len(checks),'Errors',len(report['errors']))
