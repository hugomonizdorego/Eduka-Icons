#!/usr/bin/env python3
"""Build the Eduka-Icons Light, Dark, Bright and Comfort themes.

Layout of every variant:

  <N>x<N>/<context>/      clay artwork (PNG) for apps, places, devices, file types, ...
  <N>x<N>@2x/<context>/   HiDPI aliases of the 2N pixel artwork
  scalable/<context>/     flat Eduka line glyphs (normal tray, panel and toolbar icons)
  flat/small/<context>/   flat glyphs for tray-type names up to 24 px (clay from 32 px)
  flat/<N>/<context>/     flat upstream icons Eduka does not draw (recoloured SVG)
  symbolic/<context>/     -symbolic icons
"""
import argparse
import configparser
import json
import multiprocessing
import os
from pathlib import Path
import re
import shutil
from PIL import Image, ImageEnhance

import flat
import folders
import settings
from contexts import context_of
from artwork import duplicates
from catalog import plan, upstream
from clay import ROOT, ASSETS, source_for
from clayify import comfort, save_png, sharpen, rim, fit
from prepare_clay import prepare
from symbolic import SYMBOLS, svg

CFG = settings.load()
VERSION = (ROOT / 'VERSION').read_text().strip()
VARIANTS = tuple(CFG['build']['variants'])
PROFILE = {'Light': 'standard', 'Dark': 'standard', 'Bright': 'bright', 'Comfort': 'comfort'}
SIZES = tuple(CFG['build']['sizes'])
DENSITIES = tuple(d for d in CFG['build']['hidpi'] if d in SIZES)
PHYSICAL = settings.physical(SIZES, DENSITIES)
SMALL_MAX = 24                       # tray-type names are flat up to this size
SYMBOLIC_CONTEXTS = tuple(sorted({v[2] for v in SYMBOLS.values()}))
CONTEXT_LABELS = {'apps': 'Applications', 'places': 'Places', 'devices': 'Devices',
                  'mimetypes': 'MimeTypes', 'categories': 'Categories', 'actions': 'Actions',
                  'status': 'Status', 'emblems': 'Emblems', 'emotes': 'Emotes', 'animations': 'Animations'}
PANEL_CONTEXTS = ('status', 'actions')
# Names used in system trays, panels and session menus: flat at small sizes
# even though Eduka also has clay artwork for them (shown from 32 px).
TRAY = re.compile(r'^(battery|bluetooth|network-(wireless|wired)|audio-(input-microphone|volume)|'
                  r'microphone|notification|preferences-system-notifications|display-brightness|airplane-mode|'
                  r'printer$|drive-removable-media$|system-software-update$|input-touchpad$|'
                  r'system-(shutdown|reboot|restart|log-out|lock-screen|suspend|hibernate|suspend-hibernate|search)$)')
TRAY_GLYPH = {'bluetooth': 'bluetooth', 'battery': 'battery-full', 'network-wireless': 'wifi-high',
              'network-wired': 'wired', 'audio-input-microphone': 'microphone',
              'preferences-system-notifications': 'bell', 'system-hibernate': 'suspend',
              'system-suspend-hibernate': 'suspend', 'system-restart': 'reboot'}
# Missing themes are skipped by GTK, Qt and KDE, so the list is safe on any system.
FALLBACK = {'Light': 'Papirus-Light,Papirus,breeze,Adwaita,hicolor',
            'Dark': 'Papirus-Dark,Papirus,breeze-dark,Adwaita,hicolor',
            'Bright': 'Papirus-Light,Papirus,breeze,Adwaita,hicolor',
            'Comfort': 'Papirus-Light,Papirus,breeze,Adwaita,hicolor'}
# The catalog theme must come first: any parent that itself inherits hicolor (or is missing, which Qt
# replaces by its fallback theme) would otherwise serve an application's own flat icon before ours.
APPS = {'Light': 'Eduka-Icons-Apps', 'Dark': 'Eduka-Icons-Apps', 'Bright': 'Eduka-Icons-Apps',
        'Comfort': 'Eduka-Icons-Apps-Comfort,Eduka-Icons-Apps'}
INHERITS = {variant: f'{APPS[variant]},{FALLBACK[variant]}' for variant in settings.KNOWN_VARIANTS}
COMMENTS = {'Light': 'Edukasaun OS clay icons for light desktop themes',
            'Dark': 'Edukasaun OS clay icons for dark desktop themes',
            'Bright': 'Edukasaun OS vivid clay icons for bright, colourful desktop themes',
            'Comfort': 'Edukasaun OS eye-comfort clay icons: high-contrast contours, warm low-blue colours'}


def brighten(image):
    """Bright edition: livelier clay colours with the same shapes and alpha."""
    tone = CFG['bright']
    alpha = image.getchannel('A')
    rgb = image.convert('RGB')
    rgb = ImageEnhance.Color(rgb).enhance(tone['saturation'])
    rgb = ImageEnhance.Brightness(rgb).enhance(tone['brightness'])
    rgb = ImageEnhance.Contrast(rgb).enhance(tone['contrast'])
    rgb.putalpha(alpha)
    return rgb


def alias(target, source):
    if target == source: return
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink(): target.unlink()
    elif target.exists(): raise ValueError(f'Alias conflicts with a real file: {target}')
    target.symlink_to(os.path.relpath(source, target.parent))


def write_index(theme, variant, directories):
    """directories: {path: (size, scale, context, kind, min, max)}; kind Fixed or Scalable."""
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.optionxform = str
    cfg['Icon Theme'] = {'Name': f'Eduka-Icons-{variant}',
        'Comment': COMMENTS[variant], 'Inherits': INHERITS[variant], 'Example': 'folder',
        'X-Eduka-Version': VERSION, 'X-Eduka-Edition': 'Standalone', 'X-Eduka-Variant': variant,
        'Directories': ','.join(k for k, v in directories.items() if v[1] == 1),
        'ScaledDirectories': ','.join(k for k, v in directories.items() if v[1] == 2)}
    for directory, (size, scale, context, kind, low, high) in directories.items():
        cfg[directory] = {'Size': str(size), 'Context': CONTEXT_LABELS[context], 'Type': kind}
        if scale != 1: cfg[directory]['Scale'] = str(scale)
        if kind == 'Scalable':
            cfg[directory]['MinSize'] = str(low)
            cfg[directory]['MaxSize'] = str(high)
    with (theme / 'index.theme').open('w') as stream:
        cfg.write(stream, space_around_delimiters=False)


def size_range(size, sizes):
    """(MinSize, MaxSize) so that the directories of ``sizes`` cover 8..1024 without overlap."""
    ordered = sorted(sizes)
    index = ordered.index(size)
    low = ordered[index - 1] + 1 if index else 8
    high = size if index < len(ordered) - 1 else 1024
    return low, high


def glyph_kinds():
    """{icon name: (glyph kind, context)} for every name the line glyphs can draw."""
    names = {}
    for name, (kind, aliases, context) in SYMBOLS.items():
        for other in dict.fromkeys((name, *(n.removesuffix('-symbolic') for n in aliases.split()))):
            names.setdefault(other, (kind, context))
    return names


def panel_names(core):
    """Flat names: (always flat, flat only at small sizes)."""
    reserved = {n for name, (_, _, _, names) in core.items() for n in (name, *names.split())}
    bulk = upstream()
    drawable = glyph_kinds()
    always, small = {}, {}
    coloured = flat.coloured_names()
    for name, (kind, context) in drawable.items():
        if name in reserved or name in coloured:
            continue
        if context not in PANEL_CONTEXTS and name in bulk:
            continue  # application/category names use full artwork
        always[name] = (kind, context_of(name, context))
    for name in sorted(reserved):
        if not TRAY.match(name):
            continue
        if name in TRAY_GLYPH:
            small[name] = (TRAY_GLYPH[name], 'status')
        elif name in drawable:
            small[name] = (drawable[name][0], 'status')
    return always, small


def _export_asset(job):
    """Write every size (and folder colour) of one clay master for one profile."""
    name, profile, pixels = job
    build, tone = CFG['build'], CFG['comfort']
    colours = [c for c in CFG['folders']['colours'] if c != CFG['folders']['default']]
    limit = {}
    with Image.open(ASSETS / (name + '.png')) as image:
        master = fit(image.convert('RGBA'))   # keep artwork and shadow off the canvas edge
    versions = {name: master}
    if name == 'folder' or name.startswith('folder-'):
        if CFG['folders']['default'] != 'aqua':
            versions[name] = folders.tint(master, CFG['folders']['default'])
        for colour in colours:
            versions[f'{name}@{colour}'] = folders.tint(master, colour)
    for asset, image in versions.items():
        if profile == 'bright': image = brighten(image)
        largest = CFG['folders']['max_size'] if '@' in asset else max(PHYSICAL)
        limit[asset] = largest
        for size in PHYSICAL:
            if size > largest: continue
            if profile == 'comfort':
                small = comfort(image, size, tone['outline'], tone['contrast'], tone['saturation'], tone['blue'],
                                build['sharpen_up_to'], build['sharpen_percent'])
            else:
                small = image.resize((size, size), Image.Resampling.LANCZOS)
                small = sharpen(small, size, build['sharpen_up_to'], build['sharpen_percent'])
                if size <= 32: small = rim(small)   # cream objects keep an edge on light backgrounds
            target = pixels / str(size) / (asset + '.png')
            if target.exists(): target.unlink()   # never write through a hard link
            save_png(small, target, 'lossless' if size < 128 else 'fine')
    return limit


def export_pixels(required, profile):
    """Write every size of every clay master; returns (directory, {asset: largest size written})."""
    pixels = settings.BUILD / f'pixels-{profile}'
    if pixels.exists(): shutil.rmtree(pixels)
    for size in PHYSICAL:
        (pixels / str(size)).mkdir(parents=True)
    limit = {}
    with multiprocessing.Pool(os.cpu_count() or 2) as pool:
        for part in pool.imap_unordered(_export_asset, [(name, profile, pixels) for name in sorted(required)], chunksize=2):
            limit.update(part)
    return pixels, limit


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


def write_glyphs(theme, variant, base, names, directories, scaled=False):
    """Write flat glyph SVGs for {name: (kind, context)} below theme/base/<context>."""
    canonical = {}
    for name, (kind, context) in sorted(names.items()):
        folder = theme / base / context
        folder.mkdir(parents=True, exist_ok=True)
        key = (context, kind)
        if key not in canonical:
            canonical[key] = folder / f'{name}.svg'
            canonical[key].write_text(svg(kind, variant, name))
        else:
            alias(folder / f'{name}.svg', canonical[key])
    for context in sorted({c for _, c in names.values()}):
        if base == 'scalable':
            directories[f'{base}/{context}'] = (16, 1, context, 'Scalable', 8, 512)
        else:
            directories[f'{base}/{context}'] = (16, 1, context, 'Scalable', 8, SMALL_MAX)
            if scaled:   # the same glyphs for HiDPI panels (otherwise 2x would pick the clay artwork)
                twin = theme / f'{base}@2x' / context
                twin.mkdir(parents=True, exist_ok=True)
                for path in (theme / base / context).iterdir():
                    alias(twin / path.name, path)
                directories[f'{base}@2x/{context}'] = (16, 2, context, 'Scalable', 8, SMALL_MAX)


def build(output, variants=VARIANTS):
    conflicts = duplicates()
    if conflicts: raise ValueError(f'Icon names claimed twice: {conflicts}')
    prepare()
    core, catalog = plan()
    always, small = panel_names(core)
    catalog_names = set(catalog['art']) | set(catalog['links']) | set(catalog['badges'])
    for data in catalog.get('types', {}).values():
        catalog_names |= set(data['art']) | set(data['links'])
    # Every name is filed under its specification context, whatever artwork entry it belongs to.
    placed = {name: context_of(name, context) for main, (_, _, context, names) in core.items()
              for name in (main, *names.split())}
    contexts = tuple(sorted(set(placed.values())))
    output.mkdir(parents=True, exist_ok=True)
    required = {source_for(name, data[0]) for name, data in core.items()}
    reserved = {n for name, (_, _, _, names) in core.items() for n in (name, *names.split())}
    colours = [c for c in CFG['folders']['colours'] if c != CFG['folders']['default']]
    symbolic_names = set(glyph_kinds())
    pixel_sets, counts = {}, {}
    for variant in variants:
        profile = PROFILE[variant]
        if profile not in pixel_sets: pixel_sets[profile] = export_pixels(required, profile)
        pixels, limit = pixel_sets[profile]
        theme = output / f'Eduka-Icons-{variant}'
        claim(theme, variant)
        directories = {}
        for size in PHYSICAL:
            assetdir = theme / 'assets' / str(size)
            assetdir.mkdir(parents=True)
            for asset, largest in limit.items():
                if size > largest: continue
                # File hard links keep every theme independently usable.
                try: os.link(pixels / str(size) / (asset + '.png'), assetdir / (asset + '.png'))
                except OSError: shutil.copy2(pixels / str(size) / (asset + '.png'), assetdir / (asset + '.png'))
            for context in contexts:
                (theme / f'{size}x{size}/{context}').mkdir(parents=True)
                if size in SIZES:
                    # Non-overlapping ranges: a size between two directories is scaled DOWN from the
                    # next larger artwork (Qt never scales up and would return an undersized icon).
                    directories[f'{size}x{size}/{context}'] = (size, 1, context, 'Scalable', *size_range(size, SIZES))
            for name, (kind, _, _, names) in core.items():
                asset = source_for(name, kind)
                master = assetdir / (asset + '.png')
                for other in (name, *names.split()):
                    if size <= SMALL_MAX and other in small:
                        continue           # flat glyph at tray sizes
                    alias(theme / f'{size}x{size}' / placed[other] / (other + '.png'), master)
                if asset == 'folder' or asset.startswith('folder-'):
                    for colour in colours:
                        if size <= limit[f'{asset}@{colour}']:
                            alias(theme / f'{size}x{size}/places' / (name.replace('folder', f'folder-{colour}', 1) + '.png'),
                                  assetdir / f'{asset}@{colour}.png')
        for logical in DENSITIES:
            for context in contexts:
                directory = f'{logical}x{logical}@2x/{context}'
                (theme / directory).mkdir(parents=True)
                directories[directory] = (logical, 2, context, 'Scalable', *size_range(logical, DENSITIES))
                for source in (theme / f'{logical * 2}x{logical * 2}' / context).iterdir():
                    if logical <= SMALL_MAX and source.stem in small:
                        continue           # flat glyph at tray sizes on HiDPI screens too
                    alias(theme / directory / source.name, source)
        for size in PHYSICAL:
            if size not in SIZES:          # only reachable through its @2x directory
                for context in contexts:
                    directories.pop(f'{size}x{size}/{context}', None)
        write_glyphs(theme, variant, 'scalable', always, directories)
        write_glyphs(theme, variant, 'flat/small', small, directories, scaled=True)
        # -symbolic icons.
        for context in SYMBOLIC_CONTEXTS:
            (theme / 'symbolic' / context).mkdir(parents=True)
            directories[f'symbolic/{context}'] = (16, 1, context, 'Scalable', 8, 512)
        rendered = {}
        for name, (kind, names, context) in SYMBOLS.items():
            folder = theme / 'symbolic' / context
            canonical = folder / (name + '-symbolic.svg')
            if kind not in rendered: rendered[kind] = svg(kind, variant, name)
            canonical.write_text(rendered[kind])
            for other in dict.fromkeys((name, *(n.removesuffix('-symbolic') for n in names.split()))):
                alias(folder / (other + '-symbolic.svg'), canonical)
        # Everything else a tray, toolbar or file manager may ask for: flat upstream icons.
        extra, flat_count = flat.install(theme, CFG['glyphs']['colour'][variant], reserved | set(always) | catalog_names,
                                         symbolic_names, set(SYMBOLIC_CONTEXTS))
        for directory, (size, context, low, high) in extra.items():
            directories[directory] = (size, 1, context, 'Scalable', low, high)
        write_index(theme, variant, directories)
        counts[variant] = {'artwork': len(required), 'clay_names': len(reserved),
                           'eduka_flat_names': len(always), 'tray_small_names': len(small),
                           'upstream_flat_names': flat_count, 'folder_colours': [CFG['folders']['default'], *colours],
                           'symbolic_names': sum(1 for _ in theme.glob('symbolic/*/*-symbolic.svg')),
                           'sizes': list(SIZES), 'inherits': INHERITS[variant].split(',')}
    report = {'version': VERSION, 'edition': 'Standalone', 'themes': counts}
    (settings.BUILD / 'coverage.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=settings.BUILD / 'themes')
    parser.add_argument('--variant', choices=settings.KNOWN_VARIANTS, action='append',
                        help='build only this variant (repeatable); default: all in eduka-icons.toml')
    args = parser.parse_args()
    build(args.output, tuple(args.variant or VARIANTS))
