"""Verify the extracted review package against its internal SHA-256 manifest."""
from pathlib import Path
import hashlib,json,sys

base=Path(__file__).resolve().parent
manifest=json.loads((base/'PACKAGE_MANIFEST.json').read_text())
failures=[]
for entry in manifest['files']:
    path=base/entry['path']
    if not path.is_file():
        failures.append((entry['path'],'missing'))
        continue
    data=path.read_bytes()
    if len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
        failures.append((entry['path'],'changed'))
if failures:
    for name,reason in failures: print(reason+': '+name)
    sys.exit(1)
print('PASS: '+str(len(manifest['files']))+' files match the package manifest.')
print('This verifies integrity, not the mathematical or empirical claims.')
