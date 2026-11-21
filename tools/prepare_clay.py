#!/usr/bin/env python3
"""Restore lossless hero artwork and build original clay compositions offline."""
import hashlib
import json
import shutil
from PIL import Image
from artwork import CATALOG
from clay import ASSETS, ROOT, KIND_ASSET, OVERLAYS, source_for, vector, folder_svg, overlay_svg, encoded
from render import render

def prepare():
    ASSETS.mkdir(parents=True, exist_ok=True)
    compositions = ASSETS.parent / 'compositions'
    compositions.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((ROOT / 'assets/generated.json').read_text())
    generated = set(metadata['generated_assets'])
    for record in metadata['assets']:
        source = ROOT / 'assets' / record['file']
        if hashlib.sha256(source.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError(f'Master checksum mismatch: {record["name"]}')
        with Image.open(source) as image:
            image.convert('RGBA').save(ASSETS / (record['name'] + '.png'))
    encoded.cache_clear()
    required = {source_for(name, kind) for name, (kind, _, _, _) in CATALOG.items()}
    required.add('folder-plain')
    # Overlays are composed on finished masters, so they are rendered last.
    for name in sorted(required, key=lambda n: (n in OVERLAYS, n)):
        destination = ASSETS / (name + '.png')
        if name in OVERLAYS:
            encoded.cache_clear()
            data = overlay_svg(name)
        elif name.startswith('folder-'):
            if name == 'folder-plain':
                shutil.copyfile(ASSETS / 'folder.png', destination)
                continue
            data = folder_svg(name[7:])
        elif name in generated:
            continue
        else:
            kind = next((k for k, v in KIND_ASSET.items() if v == name), name)
            data = vector(kind)
        source = compositions / (name + '.svg')
        if destination.exists() and source.exists() and source.read_text() == data:
            continue                       # unchanged composition: keep the rendered master
        source.write_text(data)
        render(source, 1024, destination)
    encoded.cache_clear()
    print(f'Prepared {len(required)} own clay masters offline.', flush=True)

if __name__ == '__main__':
    prepare()
