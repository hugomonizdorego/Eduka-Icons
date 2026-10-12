#!/usr/bin/env python3
"""Build the hidden application themes Eduka-Icons-Apps and Eduka-Icons-Apps-Comfort.

Every visible Eduka-Icons variant inherits from them, so thousands of
application icons are stored once instead of once per variant.
"""
import argparse
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import shutil
from PIL import Image

from catalog import plan
from clay import ROOT, ASSETS
from clayify import clay_svg, render_svg, finish, comfort, monogram, save_png

VERSION = (ROOT / 'VERSION').read_text().strip()
SIZES = (16, 22, 24, 32, 48, 64, 128)
DENSITIES = (16, 24, 32, 64)
MASTER = 256
STAMP = 'clayify-1'
MASTERS = ROOT / 'build/app-masters'
THEMES = {'standard': 'Eduka-Icons-Apps', 'comfort': 'Eduka-Icons-Apps-Comfort'}


def _key(*parts):
    return hashlib.sha256('\0'.join([STAMP, *map(str, parts)]).encode()).hexdigest()[:16]


def make_art(job):
    """Clay master for one upstream artwork (cached)."""
    name, source = job
    target = MASTERS / 'art' / f'{name}.png'
    stamp = target.with_suffix('.key')
    key = _key(hashlib.sha256(source.read_bytes()).hexdigest())
    if target.exists() and stamp.exists() and stamp.read_text() == key:
        return name, True
    try:
        image = finish(render_svg(clay_svg(source.read_text()), MASTER))
    except Exception as error:  # a broken upstream file must not stop the build
        return name, f'{error}'
    image.save(target)
    stamp.write_text(key)
    return name, True


def make_badge(job):
    name, (source, base) = job
    target = MASTERS / 'badge' / f'{name}.png'
    stamp = target.with_suffix('.key')
    if source == 'core':
        path = ASSETS / f'{base}.png'
    else:
        path = MASTERS / 'art' / f'{base}.png'
    key = _key('chip-2', name, source, base, hashlib.sha256(path.read_bytes()).hexdigest())
    if target.exists() and stamp.exists() and stamp.read_text() == key:
        return name, True
    with Image.open(path) as image:
        image = image.convert('RGBA').resize((MASTER, MASTER), Image.Resampling.LANCZOS)
    monogram(image, name).save(target)
    stamp.write_text(key)
    return name, True


def export(job):
    """Write every size of one master for one profile."""
    master, folder, profile = job
    with Image.open(master) as image:
        image = image.convert('RGBA')
        for size in SIZES:
            small = image.resize((size, size), Image.Resampling.LANCZOS)
            if profile == 'comfort':
                small = comfort(small)
            save_png(small, folder / f'{size}x{size}/apps' / master.name)
    return master.stem


def write_index(theme, name):
    lines = ['[Icon Theme]', f'Name={name}',
             'Comment=Eduka clay application icons (shared by the Eduka-Icons themes)',
             'Hidden=true', 'Inherits=hicolor', f'X-Eduka-Version={VERSION}', 'Example=gimp']
    directories = [f'{s}x{s}/apps' for s in SIZES]
    scaled = [f'{s}x{s}@2x/apps' for s in DENSITIES]
    lines += ['Directories=' + ','.join(directories), 'ScaledDirectories=' + ','.join(scaled), '']
    for directory in directories:
        size = directory.split('x')[0]
        lines += [f'[{directory}]', f'Size={size}', 'Context=Applications', 'Type=Fixed', '']
    for directory in scaled:
        size = directory.split('x')[0]
        lines += [f'[{directory}]', f'Size={size}', 'Scale=2', 'Context=Applications', 'Type=Fixed', '']
    (theme / 'index.theme').write_text('\n'.join(lines))


def build(output, workers=None):
    _, apps = plan()
    for folder in ('art', 'badge'):
        (MASTERS / folder).mkdir(parents=True, exist_ok=True)
    workers = workers or os.cpu_count() or 2
    failed = {}
    with multiprocessing.Pool(workers) as pool:
        for name, ok in pool.imap_unordered(make_art, sorted(apps['art'].items()), chunksize=8):
            if ok is not True:
                failed[name] = ok
        badge_jobs = [(n, b) for n, b in sorted(apps['badges'].items())
                      if not (b[0] == 'upstream' and b[1] in failed)]
        for name, ok in pool.imap_unordered(make_badge, badge_jobs, chunksize=8):
            pass
        masters = {name: MASTERS / 'art' / f'{name}.png' for name in apps['art'] if name not in failed}
        masters.update({name: MASTERS / 'badge' / f'{name}.png' for name, _ in badge_jobs})
        report = {'version': VERSION, 'artwork': len(apps['art']) - len(failed),
                  'monogram_copies': len(badge_jobs), 'failed': failed}
        for profile, theme_name in THEMES.items():
            theme = output / theme_name
            if theme.exists():
                shutil.rmtree(theme)
            for size in SIZES:
                (theme / f'{size}x{size}/apps').mkdir(parents=True)
            jobs = [(path, theme, profile) for path in masters.values()]
            for _ in pool.imap_unordered(export, jobs, chunksize=16):
                pass
            names = 0
            for size in SIZES:
                folder = theme / f'{size}x{size}/apps'
                for name, target in apps['links'].items():
                    if target in masters and name not in masters:
                        (folder / f'{name}.png').symlink_to(f'{target}.png')
                names = len(list(folder.iterdir()))
            for logical in DENSITIES:
                folder = theme / f'{logical}x{logical}@2x/apps'
                folder.mkdir(parents=True)
                for path in (theme / f'{logical * 2}x{logical * 2}/apps').iterdir():
                    (folder / path.name).symlink_to(os.path.relpath(path, folder))
            write_index(theme, theme_name)
            report[theme_name] = {'names': names}
    (ROOT / 'build/apps.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'failed'} | {'failed': len(failed)}), flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'build/themes')
    parser.add_argument('--jobs', type=int)
    args = parser.parse_args()
    build(args.output, args.jobs)
