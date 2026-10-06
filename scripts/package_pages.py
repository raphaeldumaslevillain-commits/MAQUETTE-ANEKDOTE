"""Create a deployment directory containing only the public website."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]; output=ROOT/'.site'
if output.exists():shutil.rmtree(output)
output.mkdir()
for directory in ['assets','css','js']:
    shutil.copytree(ROOT/directory,output/directory)
for name in ['sitemap.xml','robots.txt','.nojekyll']:
    shutil.copy2(ROOT/name,output/name)
for file in ROOT.rglob('*.html'):
    if any(part.startswith('.') for part in file.relative_to(ROOT).parts):continue
    target=output/file.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target)
print('Public website packaged into .site/')
