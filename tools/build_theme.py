#!/usr/bin/env python3
"""Build the Eduka-Icons Light, Dark and Bright themes from this repository's artwork."""
import argparse
import configparser
import json
import os
from pathlib import Path
import shutil
from PIL import Image, ImageEnhance
from artwork import CATALOG, duplicates
from clay import ROOT, ASSETS, source_for
from prepare_clay import prepare
from symbolic import SYMBOLS, svg

VERSION = (ROOT / 'VERSION').read_text().strip()
VARIANTS = ('Light', 'Dark', 'Bright')
SIZES = (16, 22, 24, 32, 40, 48, 64, 96, 128, 256, 512)
DENSITIES = (16, 22, 24, 32, 48, 64, 128, 256)
PHYSICAL = tuple(sorted(set(SIZES) | {s * 2 for s in DENSITIES}))
CONTEXTS = tuple(sorted({v[2] for v in CATALOG.values()}))
SYMBOLIC_CONTEXTS = tuple(sorted({v[2] for v in SYMBOLS.values()}))
CONTEXT_LABELS = {'apps': 'Applications', 'places': 'Places', 'devices': 'Devices',
                  'mimetypes': 'MimeTypes', 'categories': 'Categories', 'actions': 'Actions',
                  'status': 'Status', 'emblems': 'Emblems'}
# Missing themes are skipped by GTK, Qt and KDE, so the list is safe on any system.
INHERITS = {'Light': 'Papirus-Light,Papirus,breeze,Adwaita,hicolor',
            'Dark': 'Papirus-Dark,Papirus,breeze-dark,Adwaita,hicolor',
            'Bright': 'Papirus-Light,Papirus,breeze,Adwaita,hicolor'}
COMMENTS = {'Light': 'Edukasaun OS clay icons for light desktop themes',
            'Dark': 'Edukasaun OS clay icons for dark desktop themes',
            'Bright': 'Edukasaun OS vivid clay icons for bright, colourful desktop themes'}

def brighten(image):
    """Bright edition: livelier clay colours with the same shapes and alpha."""
    alpha = image.getchannel('A')
    rgb = image.convert('RGB')
    rgb = ImageEnhance.Color(rgb).enhance(1.38)
    rgb = ImageEnhance.Brightness(rgb).enhance(1.08)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.06)
    rgb.putalpha(alpha)
    return rgb

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
        'Comment': COMMENTS[variant], 'Inherits': INHERITS[variant], 'Example': 'folder',
        'X-Eduka-Version': VERSION, 'X-Eduka-Edition': 'Standalone', 'X-Eduka-Variant': variant,
        'Directories': ','.join(k for k, v in directories.items() if v[1] == 1),
        'ScaledDirectories': ','.join(k for k, v in directories.items() if v[1] == 2)}
    for directory, (size, scale, context, scalable) in directories.items():
        cfg[directory] = {'Size': str(size), 'Context': CONTEXT_LABELS[context],
                          'Type': 'Scalable' if scalable else 'Fixed'}
        if scale != 1: cfg[directory]['Scale'] = str(scale)
        if scalable:
            cfg[directory]['MinSize'] = '8'
            cfg[directory]['MaxSize'] = '512'
    with (theme / 'index.theme').open('w') as stream:
        cfg.write(stream, space_around_delimiters=False)

def export_pixels(required, bright):
    pixels = ROOT / ('build/pixels-bright' if bright else 'build/pixels')
    for size in PHYSICAL:
        destination = pixels / str(size)
        destination.mkdir(parents=True, exist_ok=True)
        for name in sorted(required):
            with Image.open(ASSETS / (name + '.png')) as image:
                image = image.convert('RGBA')
                if bright: image = brighten(image)
                image = image.resize((size, size), Image.Resampling.LANCZOS)
                image.save(destination / (name + '.png'), optimize=True)
    return pixels

def claim(theme, variant):
    if theme.is_symlink(): raise ValueError(f'Refusing theme-directory symlink: {theme}')
    if theme.exists():
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read(theme / 'index.theme')
        if cfg.get('Icon Theme', 'Name', fallback='') != theme.name and not (theme / '.eduka-build-owner').is_file():
            raise ValueError(f'Refusing unrelated existing directory: {theme}')
        shutil.rmtree(theme)
    theme.mkdir(parents=True)
    (theme / '.eduka-build-owner').write_text(f'{VERSION}:{variant}\n')

def build(output, variants=VARIANTS):
    conflicts = duplicates()
    if conflicts: raise ValueError(f'Icon names claimed twice: {conflicts}')
    prepare()
    output.mkdir(parents=True, exist_ok=True)
    required = {source_for(name, data[0]) for name, data in CATALOG.items()}
    pixel_sets = {}
    counts = {}
    # Coloured names win over symbolic glyphs of the same name.
    reserved = {n for name, (_, _, _, names) in CATALOG.items() for n in (name, *names.split())}
    for variant in variants:
        bright = variant == 'Bright'
        if bright not in pixel_sets: pixel_sets[bright] = export_pixels(required, bright)
        pixels = pixel_sets[bright]
        theme = output / f'Eduka-Icons-{variant}'
        claim(theme, variant)
        directories = {}
        for size in PHYSICAL:
            assetdir = theme / 'assets' / str(size)
            assetdir.mkdir(parents=True)
            for name in required:
                # File hard links keep every theme independently usable.
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
        for context in SYMBOLIC_CONTEXTS:
            (theme / 'symbolic' / context).mkdir(parents=True)
            directories[f'symbolic/{context}'] = (16, 1, context, True)
        glyphs = {}
        for name, (kind, names, context) in SYMBOLS.items():
            folder = theme / 'symbolic' / context
            canonical = folder / (name + '-symbolic.svg')
            if kind not in glyphs: glyphs[kind] = svg(kind, variant, name)
            canonical.write_text(glyphs[kind])
            for other in dict.fromkeys((name, *(n.removesuffix('-symbolic') for n in names.split()))):
                if other not in reserved:
                    alias(folder / (other + '.svg'), canonical)
                alias(folder / (other + '-symbolic.svg'), canonical)
        write_index(theme, variant, directories)
        counts[variant] = {'artwork': len(required), 'coloured_names': len(reserved),
                           'symbolic_names': sum(1 for _ in theme.glob('symbolic/*/*-symbolic.svg')),
                           'physical_sizes': list(PHYSICAL), 'inherits': INHERITS[variant].split(',')}
    report = {'version': VERSION, 'edition': 'Standalone', 'themes': counts}
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build/coverage.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/themes')
    parser.add_argument('--variant', choices=VARIANTS, action='append',
                        help='build only this variant (repeatable); default: all')
    args = parser.parse_args()
    build(args.output, tuple(args.variant or VARIANTS))
