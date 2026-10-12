#!/usr/bin/env python3
"""Validate standalone themes, icon aliases, artwork, and 2x registrations."""
import configparser
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image
from artwork import CATALOG
from build_theme import ROOT, PHYSICAL, DENSITIES, CONTEXTS
from symbolic import SYMBOLS
from check_lookup import check as check_lookup

def validate():
    reports = []
    for variant in ('Light', 'Dark'):
        theme = ROOT / f'build/themes/Eduka-Icons-{variant}'
        errors = []
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read(theme / 'index.theme')
        assert cfg.get('Icon Theme', 'Inherits') == 'hicolor'
        assert cfg.get('Icon Theme', 'X-Eduka-Edition') == 'Standalone'
        registered = cfg.get('Icon Theme', 'Directories').split(',') + cfg.get('Icon Theme', 'ScaledDirectories').split(',')
        for directory in registered:
            if directory not in cfg or not (theme / directory).is_dir(): errors.append(directory)
        for logical in DENSITIES:
            for context in CONTEXTS:
                section = f'{logical}x{logical}@2x/{context}'
                assert cfg.getint(section, 'Scale') == 2
                assert section in cfg.get('Icon Theme', 'ScaledDirectories').split(',')
        links = real_files = 0
        for directory, directories, filenames in os.walk(theme, followlinks=False):
            for name in directories + filenames:
                path = Path(directory) / name
                if path.is_symlink():
                    links += 1
                    if os.path.isabs(os.readlink(path)) or not path.exists() or not path.resolve().is_relative_to(theme):
                        errors.append(str(path.relative_to(theme)))
                elif path.is_file():
                    real_files += 1
                    if path.suffix == '.svg': ET.fromstring(path.read_text())
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
        for name in SYMBOLS:
            assert (theme / 'scalable/status' / (name + '-symbolic.svg')).is_file(), name
        power = theme / '128x128/apps/system-shutdown.png'
        with Image.open(power) as image:
            assert image.convert('RGBA').getpixel((64, 30))[3] > 200, 'Power stroke missing'
        cache = shutil.which('gtk-update-icon-cache')
        if cache: subprocess.run([cache, '-f', '-t', str(theme)], check=True)
        reports.append({'variant': variant, 'regular_files': real_files, 'relative_links': links,
                        'core_icons': len(CATALOG), 'symbolic_icons': len(SYMBOLS), 'errors': errors})
    metadata = json.loads((ROOT / 'assets/generated.json').read_text())
    for record in metadata['assets']:
        assert hashlib.sha256((ROOT / 'assets' / record['file']).read_bytes()).hexdigest() == record['sha256']
    report = {'version': '0.3.0', 'edition': 'Standalone', 'themes': reports,
              'master_checksums_verified': len(metadata['assets']), 'physical_sizes': list(PHYSICAL),
              'gtk_lookup': check_lookup(ROOT / 'build/themes')}
    (ROOT / 'build/validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'gtk_lookup'}), flush=True)
    print('GTK lookup:',report['gtk_lookup']['status'],report['gtk_lookup'].get('checked',0),flush=True)
    if any(item['errors'] for item in reports): raise SystemExit(1)

if __name__ == '__main__': validate()
