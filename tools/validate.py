#!/usr/bin/env python3
"""Validate the built themes: index files, links, artwork, flat icons, HiDPI and GTK lookups."""
import configparser
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image

import flat
from artwork import duplicates
from catalog import plan
from build_theme import (ROOT, VERSION, VARIANTS, PHYSICAL, SIZES, DENSITIES, SMALL_MAX, CFG,
                         panel_names, glyph_kinds)
from contexts import context_of
from build_apps import SIZES as APP_SIZES, THEMES as APP_THEMES
from settings import BUILD
from symbolic import SYMBOLS, BASE
from check_lookup import check as check_lookup

SVG = '{http://www.w3.org/2000/svg}'


def check_index(theme, errors):
    """Every registered directory exists with sane keys, and every section is listed."""
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.optionxform = str
    cfg.read(theme / 'index.theme')
    head = cfg['Icon Theme']
    scaled = [d for d in head.get('ScaledDirectories', '').split(',') if d]
    registered = [d for d in head.get('Directories', '').split(',') if d] + scaled
    if len(registered) != len(set(registered)): errors.append('index: directory listed twice')
    for directory in registered:
        if directory not in cfg: errors.append(f'index: no section for {directory}'); continue
        if not (theme / directory).is_dir(): errors.append(f'index: missing directory {directory}'); continue
        section = cfg[directory]
        size, kind = section.getint('Size'), section.get('Type', 'Threshold')
        if kind not in ('Fixed', 'Scalable', 'Threshold'): errors.append(f'index: bad Type in {directory}')
        if kind == 'Scalable' and not (section.getint('MinSize') <= size <= section.getint('MaxSize')):
            errors.append(f'index: Size outside MinSize..MaxSize in {directory}')
        if (directory in scaled) != (section.getint('Scale', fallback=1) != 1):
            errors.append(f'index: Scale mismatch in {directory}')
    for section in cfg.sections():
        if section != 'Icon Theme' and section not in registered: errors.append(f'index: unlisted section {section}')
    return cfg, registered


def validate_theme(variant):
    theme = BUILD / f'themes/Eduka-Icons-{variant}'
    errors = []
    cfg, registered = check_index(theme, errors)
    assert cfg.get('Icon Theme', 'Name') == theme.name
    assert cfg.get('Icon Theme', 'Inherits').split(',')[-1] == 'hicolor'
    assert cfg.get('Icon Theme', 'X-Eduka-Version') == VERSION
    core, catalog = plan()
    always, small = panel_names(core)
    placed = {n: context_of(n, context) for main, (_, _, context, names) in core.items() for n in (main, *names.split())}
    contexts = sorted(set(placed.values()))
    for logical in DENSITIES:
        for context in contexts:
            assert cfg.getint(f'{logical}x{logical}@2x/{context}', 'Scale') == 2
    links = real_files = 0
    for directory, directories, filenames in os.walk(theme, followlinks=False):
        relative = Path(directory).relative_to(theme)
        holds_icons = any(n.endswith(('.png', '.svg')) for n in filenames)
        unlisted_ok = relative.parts[:1] == ('assets',) or any(
            relative == Path(f'{s}x{s}') / c for s in PHYSICAL if s not in SIZES for c in contexts)
        if holds_icons and not unlisted_ok and str(relative) not in registered:
            errors.append(f'icons in unregistered directory {relative}')
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
                    # Eduka glyphs (they carry a <title>) must be filled outlines: GTK recolours
                    # symbolic icons by forcing fill, which turns stroked paths into blobs.
                    if root.find(f'{SVG}title') is not None and any(
                            el.get('stroke') not in (None, 'none') for el in root.iter()):
                        errors.append(f'stroked glyph: {path.relative_to(theme)}')
                if path.suffix == '.png':
                    with Image.open(path) as image: image.verify()
    for size in PHYSICAL:
        for name, (_, _, context, aliases) in core.items():
            expected = [n for n in (name, *aliases.split()) if not (size <= SMALL_MAX and n in small)]
            if not expected: continue
            path = theme / f'{size}x{size}' / placed[expected[0]] / (expected[0] + '.png')
            with Image.open(path) as image:
                assert image.size == (size, size), path
                alpha = image.convert('RGBA').getchannel('A')
                assert alpha.getextrema()[0] < 255 and alpha.getbbox(), path
            for other in expected[1:]:
                assert (theme / f'{size}x{size}' / placed[other] / (other + '.png')).resolve() == path.resolve(), other
    for name, (_, context) in small.items():
        if not (theme / 'flat/small' / context / f'{name}.svg').exists(): errors.append(f'missing tray glyph: {name}')
        if list(theme.glob(f'22x22/*/{name}.png')): errors.append(f'tray name is still clay at 22 px: {name}')
    for name, (_, context) in always.items():
        if not (theme / 'scalable' / context / f'{name}.svg').exists(): errors.append(f'missing flat glyph: {name}')
    for name, (kind, _, context) in SYMBOLS.items():
        assert kind in BASE, kind
        if not (theme / 'symbolic' / context / (name + '-symbolic.svg')).is_file(): errors.append(f'missing symbolic: {name}')
    for colour in CFG['folders']['colours']:
        if colour == CFG['folders']['default']: continue
        for name in (f'folder-{colour}', f'folder-{colour}-documents', f'folder-{colour}-download'):
            if not (theme / '48x48/places' / f'{name}.png').exists(): errors.append(f'missing folder colour: {name}')
    upstream = flat.all_names()
    if upstream:
        reserved = {n for main, (_, _, _, names) in core.items() for n in (main, *names.split())}
        catalog_names = set(catalog['art']) | set(catalog['links']) | set(catalog['badges'])
        for data in catalog.get('types', {}).values(): catalog_names |= set(data['art']) | set(data['links'])
        present = {p.stem for p in theme.glob('flat/*/*/*.svg')} | reserved | set(always) | catalog_names
        lost = sorted(upstream - present)
        if lost: errors.append(f'{len(lost)} upstream flat names not installed, e.g. {lost[:5]}')
    with Image.open(theme / '128x128' / placed['system-shutdown'] / 'system-shutdown.png') as image:
        assert image.convert('RGBA').getpixel((64, 64))[3] > 200, 'Power artwork missing'
    cache = shutil.which('gtk-update-icon-cache')
    if cache: subprocess.run([cache, '-q', '-f', '-t', str(theme)], check=True)
    return {'variant': variant, 'regular_files': real_files, 'relative_links': links,
            'catalog_entries': len(core), 'symbolic_entries': len(SYMBOLS), 'glyphs': len(glyph_kinds()),
            'errors': errors}


def validate_apps(name):
    """Every planned catalog name exists at every size and is a real PNG of that size."""
    theme = BUILD / 'themes' / name
    _, apps = plan()
    errors = []
    check_index(theme, errors)
    wanted = {'apps': set(apps['links']) | set(apps['badges']) | set(apps['art'])}
    for context, data in apps.get('types', {}).items():
        wanted[context] = set(data['art']) | set(data['links'])
    for context, names in wanted.items():
        for size in APP_SIZES:
            folder = theme / f'{size}x{size}/{context}'
            present = {p.stem for p in folder.iterdir() if p.exists()}
            missing = names - present
            if missing: errors.append(f'{context} {size}px: {len(missing)} names missing, e.g. {sorted(missing)[:3]}')
            for index, path in enumerate(sorted(folder.iterdir())):
                if path.is_symlink(): continue
                try:
                    with Image.open(path) as image:      # every file: header and size; a sample: pixels
                        if image.size != (size, size): errors.append(f'wrong size: {path.relative_to(theme)}')
                        elif index % 23 == 0 and image.convert('RGBA').getchannel('A').getbbox() is None:
                            errors.append(f'empty: {path.relative_to(theme)}')
                except OSError as error:
                    errors.append(f'unreadable: {path.relative_to(theme)} ({error})')
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.read(theme / 'index.theme')
    assert cfg.get('Icon Theme', 'Hidden') == 'true'
    return {'variant': name, 'names': {c: len(n) for c, n in wanted.items()}, 'errors': errors}


def validate():
    assert not duplicates(), duplicates()
    reports = [validate_theme(variant) for variant in VARIANTS]
    reports += [validate_apps(name) for name in APP_THEMES.values()]
    metadata = json.loads((ROOT / 'assets/generated.json').read_text())
    for record in metadata['assets']:
        assert hashlib.sha256((ROOT / 'assets' / record['file']).read_bytes()).hexdigest() == record['sha256']
    report = {'version': VERSION, 'themes': reports, 'master_checksums_verified': len(metadata['assets']),
              'sizes': list(SIZES), 'gtk_lookup': check_lookup(BUILD / 'themes', VARIANTS)}
    (BUILD / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'gtk_lookup'}), flush=True)
    print('GTK lookup:', report['gtk_lookup']['status'], report['gtk_lookup'].get('checked', 0), flush=True)
    if any(item['errors'] for item in reports): raise SystemExit(1)


if __name__ == '__main__': validate()
