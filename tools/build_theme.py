#!/usr/bin/env python3
"""Build the Eduka-Icons Light, Dark, Bright and Comfort themes."""
import argparse
import configparser
import json
import os
from pathlib import Path
import shutil
from PIL import Image, ImageEnhance
from artwork import duplicates
from catalog import plan, upstream
from clay import ROOT, ASSETS, source_for
from clayify import raster_clay, render_svg, comfort, save_png
from prepare_clay import prepare
from symbolic import SYMBOLS, svg, clay_source

VERSION = (ROOT / 'VERSION').read_text().strip()
VARIANTS = ('Light', 'Dark', 'Bright', 'Comfort')
PROFILE = {'Light': 'standard', 'Dark': 'standard', 'Bright': 'bright', 'Comfort': 'comfort'}
SIZES = (16, 22, 24, 32, 40, 48, 64, 96, 128, 256, 512)
DENSITIES = (16, 22, 24, 32, 48, 64, 128, 256)
PHYSICAL = tuple(sorted(set(SIZES) | {s * 2 for s in DENSITIES}))
SYMBOLIC_CONTEXTS = tuple(sorted({v[2] for v in SYMBOLS.values()}))
CONTEXT_LABELS = {'apps': 'Applications', 'places': 'Places', 'devices': 'Devices',
                  'mimetypes': 'MimeTypes', 'categories': 'Categories', 'actions': 'Actions',
                  'status': 'Status', 'emblems': 'Emblems'}
PANEL_CONTEXTS = ('status', 'actions')
# Missing themes are skipped by GTK, Qt and KDE, so the list is safe on any system.
FALLBACK = {'Light': 'Papirus-Light,Papirus,breeze,Adwaita,hicolor',
            'Dark': 'Papirus-Dark,Papirus,breeze-dark,Adwaita,hicolor',
            'Bright': 'Papirus-Light,Papirus,breeze,Adwaita,hicolor',
            'Comfort': 'Papirus-Light,Papirus,breeze,Adwaita,hicolor'}
APPS = {'Light': 'Eduka-Icons-Local,Eduka-Icons-Apps', 'Dark': 'Eduka-Icons-Local,Eduka-Icons-Apps',
        'Bright': 'Eduka-Icons-Local,Eduka-Icons-Apps',
        'Comfort': 'Eduka-Icons-Local-Comfort,Eduka-Icons-Apps-Comfort,Eduka-Icons-Local,Eduka-Icons-Apps'}
INHERITS = {variant: f'{APPS[variant]},{FALLBACK[variant]}' for variant in VARIANTS}
COMMENTS = {'Light': 'Edukasaun OS clay icons for light desktop themes',
            'Dark': 'Edukasaun OS clay icons for dark desktop themes',
            'Bright': 'Edukasaun OS vivid clay icons for bright, colourful desktop themes',
            'Comfort': 'Edukasaun OS eye-comfort clay icons: high-contrast contours, warm low-blue colours'}


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


def panel_names(core):
    """Non-symbolic panel/toolbar names drawn as colourful clay glyphs."""
    reserved = {n for name, (_, _, _, names) in core.items() for n in (name, *names.split())}
    bulk = upstream()
    glyphs = {}
    for name, (kind, names, context) in SYMBOLS.items():
        for other in dict.fromkeys((name, *(n.removesuffix('-symbolic') for n in names.split()))):
            if other in reserved or other in glyphs:
                continue
            if context not in PANEL_CONTEXTS and other in bulk:
                continue  # application/category names use full artwork
            glyphs[other] = (kind, context)
    return glyphs


def prepare_glyphs(kinds):
    for kind in sorted(kinds):
        target = ASSETS / f'glyph-{kind}.png'
        raster_clay(render_svg(clay_source(kind), 512)).save(target)


def export_pixels(required, profile):
    pixels = ROOT / f'build/pixels-{profile}'
    for size in PHYSICAL:
        destination = pixels / str(size)
        destination.mkdir(parents=True, exist_ok=True)
        for name in sorted(required):
            with Image.open(ASSETS / (name + '.png')) as image:
                image = image.convert('RGBA')
                if profile == 'bright': image = brighten(image)
                image = image.resize((size, size), Image.Resampling.LANCZOS)
                if profile == 'comfort': image = comfort(image)
                save_png(image, destination / (name + '.png'), quantize=size >= 128)
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
    core, _ = plan()
    glyphs = panel_names(core)
    prepare_glyphs({kind for kind, _ in glyphs.values()})
    contexts = tuple(sorted({v[2] for v in core.values()} | {c for _, c in glyphs.values()}))
    output.mkdir(parents=True, exist_ok=True)
    required = {source_for(name, data[0]) for name, data in core.items()} | {f'glyph-{k}' for k, _ in glyphs.values()}
    pixel_sets = {}
    counts = {}
    reserved = {n for name, (_, _, _, names) in core.items() for n in (name, *names.split())}
    for variant in variants:
        profile = PROFILE[variant]
        if profile not in pixel_sets: pixel_sets[profile] = export_pixels(required, profile)
        pixels = pixel_sets[profile]
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
            for context in contexts:
                directory = f'{size}x{size}/{context}'
                (theme / directory).mkdir(parents=True)
                directories[directory] = (size, 1, context, False)
            for name, (kind, _, context, names) in core.items():
                directory = theme / f'{size}x{size}' / context
                master = assetdir / (source_for(name, kind) + '.png')
                alias(directory / (name + '.png'), master)
                for other in names.split():
                    alias(directory / (other + '.png'), directory / (name + '.png'))
            for name, (kind, context) in glyphs.items():
                alias(theme / f'{size}x{size}' / context / (name + '.png'), assetdir / f'glyph-{kind}.png')
        for logical in DENSITIES:
            for context in contexts:
                directory = f'{logical}x{logical}@2x/{context}'
                (theme / directory).mkdir(parents=True)
                directories[directory] = (logical, 2, context, False)
                for source in (theme / f'{logical * 2}x{logical * 2}' / context).iterdir():
                    alias(theme / directory / source.name, source)
        for context in SYMBOLIC_CONTEXTS:
            (theme / 'symbolic' / context).mkdir(parents=True)
            directories[f'symbolic/{context}'] = (16, 1, context, True)
        rendered = {}
        for name, (kind, names, context) in SYMBOLS.items():
            folder = theme / 'symbolic' / context
            canonical = folder / (name + '-symbolic.svg')
            if kind not in rendered: rendered[kind] = svg(kind, variant, name)
            canonical.write_text(rendered[kind])
            for other in dict.fromkeys((name, *(n.removesuffix('-symbolic') for n in names.split()))):
                alias(folder / (other + '-symbolic.svg'), canonical)
        write_index(theme, variant, directories)
        counts[variant] = {'artwork': len(required), 'coloured_names': len(reserved) + len(glyphs),
                           'clay_panel_names': len(glyphs),
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
