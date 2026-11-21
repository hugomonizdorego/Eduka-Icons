#!/usr/bin/env python3
"""Build the hidden catalog themes Eduka-Icons-Apps and Eduka-Icons-Apps-Comfort.

They hold the clay versions of thousands of application, file-type and device
icons. Every visible Eduka-Icons variant inherits from them, so the catalog is
stored once instead of once per variant.
"""
import argparse
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import shutil
from PIL import Image

import settings
from catalog import plan
from clay import ROOT, ASSETS
from clayify import clay_svg, render_svg, finish, comfort, monogram, save_png, sharpen, fit

CFG = settings.load()
VERSION = (ROOT / 'VERSION').read_text().strip()
SIZES = tuple(CFG['build']['app_sizes'])
DENSITIES = tuple(d for d in CFG['build']['app_hidpi'] if d * 2 in SIZES)
MASTER = 256
# Masters are rebuilt whenever the code that draws them changes.
STAMP = hashlib.sha256(b''.join((Path(__file__).parent / f).read_bytes()
                                for f in ('clayify.py', 'render.py'))).hexdigest()[:16]
MASTERS = settings.BUILD / 'app-masters'
THEMES = {'standard': 'Eduka-Icons-Apps', 'comfort': 'Eduka-Icons-Apps-Comfort'}
LABELS = {'apps': 'Applications', 'mimetypes': 'MimeTypes', 'devices': 'Devices'}


def _key(*parts):
    return hashlib.sha256('\0'.join([STAMP, *map(str, parts)]).encode()).hexdigest()[:16]


def _fresh(target, key):
    stamp = target.with_suffix('.key')
    return target.exists() and stamp.exists() and stamp.read_text() == key


def make_art(job):
    """Clay master for one upstream artwork (cached by source content)."""
    context, name, source = job
    target = MASTERS / 'art' / context / f'{name}.png'
    key = _key(hashlib.sha256(source.read_bytes()).hexdigest())
    if _fresh(target, key):
        return context, name, True
    try:
        image = finish(render_svg(clay_svg(source.read_text(encoding='utf-8', errors='ignore')), MASTER))
        if image.getchannel('A').getbbox() is None:
            raise ValueError('empty render')
    except Exception as error:  # a broken upstream file must not stop the build
        return context, name, f'{error}'
    target.with_suffix('.key').unlink(missing_ok=True)
    image.save(target)
    target.with_suffix('.key').write_text(key)
    return context, name, True


def make_badge(job):
    name, (source, base) = job
    target = MASTERS / 'badge' / f'{name}.png'
    path = ASSETS / f'{base}.png' if source == 'core' else MASTERS / 'art/apps' / f'{base}.png'
    key = _key('chip-5', name, source, base, hashlib.sha256(path.read_bytes()).hexdigest())
    if _fresh(target, key):
        return name, True
    target.with_suffix('.key').unlink(missing_ok=True)
    with Image.open(path) as image:
        image = fit(image.convert('RGBA')).resize((MASTER, MASTER), Image.Resampling.LANCZOS)
    # Three masters: plain artwork (16-24 px, a chip would only be a blob), one letter (32-47 px), two letters.
    image.save(target.with_name(f'{name}@0.png'))
    monogram(image, name, 1).save(target.with_name(f'{name}@1.png'))
    monogram(image, name, 2).save(target)
    target.with_suffix('.key').write_text(key)
    return name, True


def export(job):
    """Write every size of one master for one profile."""
    master, folder, context, profile = job
    build, tone = CFG['build'], CFG['comfort']
    sources = {}
    for size in SIZES:
        variant = master
        if master.parent.name == 'badge':
            variant = master.with_name(f'{master.stem}@0.png') if size <= 24 else (
                master.with_name(f'{master.stem}@1.png') if size < 48 else master)
        if variant not in sources:
            with Image.open(variant) as image:
                sources[variant] = image.convert('RGBA')
        image = sources[variant]
        if profile == 'comfort':
            small = comfort(image, size, tone['outline'], tone['contrast'], tone['saturation'], tone['blue'],
                            build['sharpen_up_to'], build['sharpen_percent'])
        else:
            small = sharpen(image.resize((size, size), Image.Resampling.LANCZOS), size,
                            build['sharpen_up_to'], build['sharpen_percent'])
        save_png(small, folder / f'{size}x{size}/{context}' / master.name, 'lossless' if size <= 24 else 'small')
    return master.stem


def write_index(theme, name, contexts):
    lines = ['[Icon Theme]', f'Name={name}',
             'Comment=Eduka clay application, file-type and device icons (shared by the Eduka-Icons themes)',
             'Hidden=true', f'X-Eduka-Version={VERSION}', 'Example=gimp']
    directories = [f'{s}x{s}/{c}' for s in SIZES for c in contexts]
    scaled = [f'{s}x{s}@2x/{c}' for s in DENSITIES for c in contexts]
    lines += ['Directories=' + ','.join(directories), 'ScaledDirectories=' + ','.join(scaled), '']
    def span(size, sizes, top):
        ordered = sorted(sizes)
        index = ordered.index(size)
        return (ordered[index - 1] + 1 if index else 8), (size if index < len(ordered) - 1 else top)

    # Non-overlapping ranges: sizes in between (18, 20, 36, 40, 96, 256 ...) are scaled down from the
    # next larger artwork, and the largest size serves everything above it.
    for directory in directories:
        size, context = int(directory.split('x')[0]), directory.split('/')[1]
        low, high = span(size, SIZES, 1024)
        lines += [f'[{directory}]', f'Size={size}', f'Context={LABELS[context]}', 'Type=Scalable',
                  f'MinSize={low}', f'MaxSize={high}', '']
    for directory in scaled:
        size, context = int(directory.split('x')[0]), directory.split('/')[1]
        low, high = span(size, DENSITIES, size)
        lines += [f'[{directory}]', f'Size={size}', 'Scale=2', f'Context={LABELS[context]}', 'Type=Scalable',
                  f'MinSize={low}', f'MaxSize={high}', '']
    (theme / 'index.theme').write_text('\n'.join(lines))


def build(output, workers=None):
    _, apps = plan()
    contexts = ['apps', *sorted(apps.get('types', {}))]
    art_jobs = [('apps', name, path) for name, path in sorted(apps['art'].items())]
    for context, data in sorted(apps.get('types', {}).items()):
        art_jobs += [(context, name, path) for name, path in sorted(data['art'].items())]
    for context in contexts:
        (MASTERS / 'art' / context).mkdir(parents=True, exist_ok=True)
    (MASTERS / 'badge').mkdir(parents=True, exist_ok=True)
    workers = workers or os.cpu_count() or 2
    failed = {}
    with multiprocessing.Pool(workers) as pool:
        for context, name, ok in pool.imap_unordered(make_art, art_jobs, chunksize=8):
            if ok is not True:
                failed[f'{context}/{name}'] = ok
        badge_jobs = [(n, b) for n, b in sorted(apps['badges'].items())
                      if not (b[0] == 'upstream' and f'apps/{b[1]}' in failed)]
        for _ in pool.imap_unordered(make_badge, badge_jobs, chunksize=8):
            pass
        masters = {context: {} for context in contexts}
        for context, name, _ in art_jobs:
            if f'{context}/{name}' not in failed:
                masters[context][name] = MASTERS / 'art' / context / f'{name}.png'
        masters['apps'].update({name: MASTERS / 'badge' / f'{name}.png' for name, _ in badge_jobs})
        links = {'apps': apps['links'], **{c: d['links'] for c, d in apps.get('types', {}).items()}}
        report = {'version': VERSION, 'artwork': len(art_jobs) - len(failed),
                  'monogram_copies': len(badge_jobs), 'failed': failed}
        for profile, theme_name in THEMES.items():
            theme = output / theme_name
            if theme.exists():
                shutil.rmtree(theme)
            jobs = []
            for context in contexts:
                for size in SIZES:
                    (theme / f'{size}x{size}/{context}').mkdir(parents=True)
                jobs += [(path, theme, context, profile) for path in masters[context].values()]
            for _ in pool.imap_unordered(export, jobs, chunksize=16):
                pass
            names = {}
            for context in contexts:
                for size in SIZES:
                    folder = theme / f'{size}x{size}/{context}'
                    for name, target in links[context].items():
                        if target in masters[context] and name not in masters[context]:
                            (folder / f'{name}.png').symlink_to(f'{target}.png')
                    names[context] = len(list(folder.iterdir()))
                for logical in DENSITIES:
                    folder = theme / f'{logical}x{logical}@2x/{context}'
                    folder.mkdir(parents=True)
                    for path in (theme / f'{logical * 2}x{logical * 2}/{context}').iterdir():
                        (folder / path.name).symlink_to(os.path.relpath(path, folder))
            write_index(theme, theme_name, contexts)
            report[theme_name] = {'names': names}
    (settings.BUILD / 'apps.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'failed'} | {'failed': len(failed)}), flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=settings.BUILD / 'themes')
    parser.add_argument('--jobs', type=int)
    args = parser.parse_args()
    result = build(args.output, args.jobs)
    # A few broken upstream files are tolerated (their names fall back to a parent theme); many are a bug.
    if len(result['failed']) > max(5, result['artwork'] // 200):
        raise SystemExit(f"{len(result['failed'])} artworks could not be converted, see {settings.BUILD / 'apps.json'}")
