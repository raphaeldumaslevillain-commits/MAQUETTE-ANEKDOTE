"""Restore missing local assets from the audited public sources. Never runs in the browser."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import json, subprocess, os, hashlib, shutil
import requests
from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.media-cache'; CACHE.mkdir(exist_ok=True)
FFMPEG=os.environ.get('ANEKDOTE_FFMPEG') or shutil.which('ffmpeg')
if not FFMPEG:
    try:
        import imageio_ffmpeg
        FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError: pass
MAPPING=json.loads((ROOT/'content/media-map.json').read_text())

def download(source, destination):
    if destination.exists(): return
    with requests.get(source, stream=True, timeout=120) as response:
        response.raise_for_status()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('wb') as file:
            for chunk in response.iter_content(256*1024): file.write(chunk)

def convert_video(source, target):
    if not FFMPEG: raise RuntimeError('FFmpeg is required to restore video files.')
    subprocess.run([FFMPEG,'-y','-i',str(source),'-vf',"scale='min(960,iw)':'min(1440,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2",'-r','24','-c:v','libx264','-threads','2','-preset','fast','-crf','27','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-movflags','+faststart',str(target)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if target.stat().st_size>30_000_000:
        temp=target.with_suffix('.temporary.mp4')
        subprocess.run([FFMPEG,'-y','-i',str(target),'-vf','scale=480:-2','-c:v','libx264','-threads','2','-crf','31','-preset','fast','-maxrate','700k','-bufsize','1400k','-c:a','aac','-b:a','80k','-movflags','+faststart',str(temp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        temp.replace(target)

def restore(item):
    source, info=item; target=ROOT/info['path']
    outputs=[target]+[ROOT/v['path'] for v in info.get('variants',[])]+([ROOT/info['poster']] if info.get('poster') else [])
    if all(p.exists() for p in outputs): return
    raw=CACHE/(hashlib.sha256(source.encode()).hexdigest()+Path(urlparse(source).path).suffix)
    download(source,raw); target.parent.mkdir(parents=True,exist_ok=True)
    if target.suffix=='.svg': target.write_bytes(raw.read_bytes())
    elif target.suffix=='.mp4':
        if not target.exists(): convert_video(raw,target)
        if info.get('poster'):
            subprocess.run([FFMPEG,'-y','-ss','0.4','-i',str(target),'-frames:v','1',str(ROOT/info['poster'])],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    else:
        image=ImageOps.exif_transpose(Image.open(raw)); image=image.convert('RGBA' if 'A' in image.getbands() else 'RGB'); image.thumbnail((1920,1920))
        image.save(target,'WEBP',quality=85,method=6)
        for variant in info.get('variants',[]):
            v=image.copy(); width=variant['width']; v.thumbnail((width,int(image.height*width/image.width)))
            v.save(ROOT/variant['path'],'WEBP',quality=82,method=6)
    info['bytes']=target.stat().st_size
    print('Restored', info['path'], flush=True)

with ThreadPoolExecutor(max_workers=2) as executor:
    list(executor.map(restore,MAPPING.items()))
for font in json.loads((ROOT/'content/fonts-map.json').read_text()): download(font['source'], ROOT/font['path'])
(ROOT/'content/media-map.json').write_text(json.dumps(MAPPING,ensure_ascii=False,indent=2))
print('All local media are present.')
