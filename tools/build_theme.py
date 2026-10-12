#!/usr/bin/env python3
"""Build standalone Eduka themes using only this repository's artwork."""
import argparse
import configparser
import json
import os
from pathlib import Path
import shutil
from PIL import Image
from artwork import CATALOG
from clay import ROOT, ASSETS, source_for
from prepare_clay import prepare
from symbolic import SYMBOLS, svg

VERSION = '0.3.0'
SIZES = (16, 22, 24, 32, 40, 48, 64, 96, 128, 192, 256, 512)
DENSITIES = (16, 18, 22, 24, 32, 40, 48, 64, 96, 128, 192, 256, 512)
PHYSICAL = tuple(sorted(set(SIZES) | {s * 2 for s in DENSITIES}))
CONTEXTS = tuple(sorted({v[2] for v in CATALOG.values()}))
CONTEXT_LABELS = {'apps': 'Applications', 'places': 'Places', 'devices': 'Devices',
                  'mimetypes': 'MimeTypes', 'categories': 'Categories',
                  'status': 'Status', 'emblems': 'Emblems'}

def alias(target, source):
    if target == source: return
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink(): target.unlink()
    elif target.exists(): raise ValueError(f'Alias conflicts with a real file: {target}')
    target.symlink_to(os.path.relpath(source, target.parent))

def write_index(theme, variant, directories):
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.optionxform = str
    cfg['Icon Theme'] = {'Name': f'Eduka-Icons-{variant}',
        'Comment': 'Edukasaun OS original clay icon theme', 'Inherits': 'hicolor',
        'X-Eduka-Version': VERSION, 'X-Eduka-Edition': 'Standalone',
        'Directories': ','.join(k for k, v in directories.items() if v[1] == 1),
        'ScaledDirectories': ','.join(k for k, v in directories.items() if v[1] == 2)}
    for directory, (size, scale, context, scalable) in directories.items():
        cfg[directory] = {'Size': str(size), 'Context': CONTEXT_LABELS[context],
                          'Type': 'Scalable' if scalable else 'Fixed'}
        if scale != 1: cfg[directory]['Scale'] = str(scale)
        if scalable:
            cfg[directory]['MinSize'] = '8'
            cfg[directory]['MaxSize'] = '1024'
    with (theme / 'index.theme').open('w') as stream:
        cfg.write(stream, space_around_delimiters=False)

def build(output):
    prepare()
    output.mkdir(parents=True, exist_ok=True)
    pixels = ROOT / 'build/pixels'
    required = {source_for(name, data[0]) for name, data in CATALOG.items()}
    for size in PHYSICAL:
        destination = pixels / str(size)
        destination.mkdir(parents=True, exist_ok=True)
        for name in sorted(required):
            with Image.open(ASSETS / (name + '.png')) as image:
                image = image.convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)
                image.save(destination / (name + '.png'))
    counts = {}
    for variant in ('Light', 'Dark'):
        theme = output / f'Eduka-Icons-{variant}'
        if theme.is_symlink(): raise ValueError(f'Refusing theme-directory symlink: {theme}')
        if theme.exists():
            cfg = configparser.ConfigParser(interpolation=None)
            cfg.read(theme / 'index.theme')
            marker = theme / '.eduka-build-owner'
            owned = marker.is_file() and marker.read_text() == f'{VERSION}:{variant}\n'
            if cfg.get('Icon Theme', 'Name', fallback='') != theme.name and not owned:
                raise ValueError(f'Refusing unrelated existing directory: {theme}')
            shutil.rmtree(theme)
        theme.mkdir()
        (theme / '.eduka-build-owner').write_text(f'{VERSION}:{variant}\n')
        directories = {}
        for size in PHYSICAL:
            assetdir = theme / 'assets' / str(size)
            assetdir.mkdir(parents=True)
            for name in required:
                # File hard links keep both themes independently usable.
                try: os.link(pixels / str(size) / (name + '.png'), assetdir / (name + '.png'))
                except OSError: shutil.copy2(pixels / str(size) / (name + '.png'), assetdir / (name + '.png'))
            for context in CONTEXTS:
                directory = f'{size}x{size}/{context}'
                (theme / directory).mkdir(parents=True)
                directories[directory] = (size, 1, context, False)
            for name, (kind, _, context, names) in CATALOG.items():
                directory = theme / f'{size}x{size}' / context
                master = assetdir / (source_for(name, kind) + '.png')
                alias(directory / (name + '.png'), master)
                for other in names.split():
                    if not other.endswith('-symbolic'):
                        alias(directory / (other + '.png'), directory / (name + '.png'))
        for logical in DENSITIES:
            for context in CONTEXTS:
                directory = f'{logical}x{logical}@2x/{context}'
                (theme / directory).mkdir(parents=True)
                directories[directory] = (logical, 2, context, False)
                for source in (theme / f'{logical * 2}x{logical * 2}' / context).iterdir():
                    alias(theme / directory / source.name, source)
        (theme / 'scalable/status').mkdir(parents=True)
        directories['scalable/status'] = (24, 1, 'status', True)
        # Non-symbolic panel names do not replace the coloured desktop roles.
        reserved = set(CATALOG)
        for name, (kind, names) in SYMBOLS.items():
            canonical = theme / 'scalable/status' / (name + '-symbolic.svg')
            canonical.write_text(svg(kind, variant, name))
            for other in (name, *names.split()):
                if other not in reserved:
                    alias(canonical.parent / (other + '.svg'), canonical)
                alias(canonical.parent / (other + '-symbolic.svg'), canonical)
        write_index(theme, variant, directories)
        counts[variant] = {'core_icons': len(CATALOG), 'own_symbolic_icons': len(SYMBOLS),
                           'physical_sizes': list(PHYSICAL), 'inherits': ['hicolor']}
    report = {'version': VERSION, 'edition': 'Standalone', 'themes': counts,
              'source_artwork_only': True, 'upstream_assets_included': False}
    (ROOT / 'build/coverage.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/themes')
    build(parser.parse_args().output)
