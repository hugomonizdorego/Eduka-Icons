#!/usr/bin/env python3
"""Validate the built themes: index files, links, artwork, HiDPI and GTK lookups."""
import configparser
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image
from artwork import CATALOG, duplicates
from build_theme import ROOT, VERSION, VARIANTS, PHYSICAL, DENSITIES, CONTEXTS
from symbolic import SYMBOLS
from check_lookup import check as check_lookup

def validate_theme(variant):
    theme = ROOT / f'build/themes/Eduka-Icons-{variant}'
    errors = []
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(theme / 'index.theme')
    assert cfg.get('Icon Theme', 'Name') == theme.name
    assert cfg.get('Icon Theme', 'Inherits').split(',')[-1] == 'hicolor'
    assert cfg.get('Icon Theme', 'X-Eduka-Version') == VERSION
    registered = cfg.get('Icon Theme', 'Directories').split(',') + cfg.get('Icon Theme', 'ScaledDirectories').split(',')
    for directory in registered:
        if directory not in cfg or not (theme / directory).is_dir(): errors.append(f'unregistered: {directory}')
    for logical in DENSITIES:
        for context in CONTEXTS:
            section = f'{logical}x{logical}@2x/{context}'
            assert cfg.getint(section, 'Scale') == 2, section
    links = real_files = 0
    for directory, directories, filenames in os.walk(theme, followlinks=False):
        for name in directories + filenames:
            path = Path(directory) / name
            if path.is_symlink():
                links += 1
                if os.path.isabs(os.readlink(path)) or not path.exists() or not path.resolve().is_relative_to(theme):
                    errors.append(f'bad link: {path.relative_to(theme)}')
            elif path.is_file():
                real_files += 1
                if path.suffix == '.svg':
                    root = ET.fromstring(path.read_text())
                    # GTK recolours symbolic icons by forcing fill; strokes would turn into blobs.
                    if any(el.get('stroke') not in (None, 'none') for el in root.iter()):
                        errors.append(f'stroked symbolic: {path.relative_to(theme)}')
                if path.suffix == '.png':
                    with Image.open(path) as image: image.verify()
    for size in PHYSICAL:
        for name, (_, _, context, aliases) in CATALOG.items():
            path = theme / f'{size}x{size}' / context / (name + '.png')
            with Image.open(path) as image:
                assert image.size == (size, size), path
                alpha = image.convert('RGBA').getchannel('A')
                assert alpha.getextrema()[0] < 255 and alpha.getbbox(), path
            for other in aliases.split():
                if not other.endswith('-symbolic'):
                    assert (path.parent / (other + '.png')).resolve() == path.resolve(), other
    for name, (_, _, context) in SYMBOLS.items():
        if not (theme / 'symbolic' / context / (name + '-symbolic.svg')).is_file(): errors.append(f'missing symbolic: {name}')
    with Image.open(theme / '128x128/apps/system-shutdown.png') as image:
        assert image.convert('RGBA').getpixel((64, 30))[3] > 200, 'Power artwork missing'
    cache = shutil.which('gtk-update-icon-cache')
    if cache: subprocess.run([cache, '-q', '-f', '-t', str(theme)], check=True)
    return {'variant': variant, 'regular_files': real_files, 'relative_links': links,
            'catalog_entries': len(CATALOG), 'symbolic_entries': len(SYMBOLS), 'errors': errors}

def validate():
    assert not duplicates(), duplicates()
    reports = [validate_theme(variant) for variant in VARIANTS]
    metadata = json.loads((ROOT / 'assets/generated.json').read_text())
    for record in metadata['assets']:
        assert hashlib.sha256((ROOT / 'assets' / record['file']).read_bytes()).hexdigest() == record['sha256']
    report = {'version': VERSION, 'themes': reports, 'master_checksums_verified': len(metadata['assets']),
              'physical_sizes': list(PHYSICAL), 'gtk_lookup': check_lookup(ROOT / 'build/themes')}
    (ROOT / 'build/validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'gtk_lookup'}), flush=True)
    print('GTK lookup:', report['gtk_lookup']['status'], report['gtk_lookup'].get('checked', 0), flush=True)
    if any(item['errors'] for item in reports): raise SystemExit(1)

if __name__ == '__main__': validate()
