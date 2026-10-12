#!/usr/bin/env python3
"""Give every installed application an Eduka clay icon.

Scans the .desktop files of installed applications (Debian packages, Flatpak,
Snap and local installs). Each icon name that the Eduka-Icons themes do not
draw yet is converted from the application's own icon into clay and stored in
the hidden themes Eduka-Icons-Local and Eduka-Icons-Local-Comfort, which every
Eduka-Icons variant inherits. Runs after every apt/dpkg operation and when
Flatpak applications change.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image  # noqa: E402
from clayify import clay_svg, render_svg, raster_clay, finish, comfort, save_png  # noqa: E402

SIZES = (16, 22, 24, 32, 48, 64, 128)
DENSITIES = (16, 24, 32, 64)
MASTER = 256
EDUKA = ('Eduka-Icons-Light', 'Eduka-Icons-Apps')


def roots(user):
    home = Path.home()
    data = Path(os.environ.get('XDG_DATA_HOME', home / '.local/share'))
    system = [Path('/usr/share'), Path('/usr/local/share'), Path('/var/lib/flatpak/exports/share'),
              Path('/var/lib/snapd/desktop')]
    return ([data, data / 'flatpak/exports/share'] if user else []) + system


def desktop_icons(user):
    """{icon name: [desktop files]} for every application entry."""
    names = {}
    folders = [r / 'applications' for r in roots(user)] + [Path('/etc/xdg/autostart')]
    for folder in folders:
        if not folder.is_dir():
            continue
        for path in folder.rglob('*.desktop'):
            try:
                for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
                    if line.startswith('Icon='):
                        icon = line[5:].strip()
                        if icon and '/' not in icon:
                            icon = icon.rsplit('.', 1)[0] if icon.endswith(('.png', '.svg', '.xpm')) else icon
                            names.setdefault(icon, []).append(str(path))
                        break
            except OSError:
                continue
    return names


def eduka_names(icon_roots):
    names = set()
    for root in icon_roots:
        for theme in EDUKA:
            folder = root / theme
            for directory in (folder.glob('*x*/*') if folder.is_dir() else ()):
                if directory.is_dir():
                    names.update(p.stem for p in directory.iterdir())
    return names


def find_source(name, user):
    """Best original icon: scalable SVG, else the largest PNG/XPM."""
    best, best_size = None, -1
    for root in roots(user):
        for theme in ('hicolor', 'Papirus', 'Adwaita', 'breeze'):
            base = root / 'icons' / theme
            if not base.is_dir():
                continue
            for candidate in base.glob(f'*/apps/{name}.*'):
                folder = candidate.parent.parent.name
                size = 4096 if candidate.suffix == '.svg' else int(folder.split('x')[0]) if folder[0].isdigit() and 'x' in folder else 0
                if candidate.suffix in ('.svg', '.png') and size > best_size:
                    best, best_size = candidate, size
        for ext in ('svg', 'png', 'xpm'):
            pixmap = root / 'pixmaps' / f'{name}.{ext}'
            if pixmap.is_file() and best is None:
                best, best_size = pixmap, 0
    return best


def sculpt(source):
    if source.suffix == '.svg':
        try:
            return finish(render_svg(clay_svg(source.read_text(encoding='utf-8', errors='ignore')), MASTER))
        except Exception:
            image = render_svg(source.read_text(encoding='utf-8', errors='ignore'), MASTER)
            return finish(raster_clay(image))
    with Image.open(source) as image:
        image = image.convert('RGBA')
    side = max(image.size)
    square = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    square.paste(image, ((side - image.width) // 2, (side - image.height) // 2))
    inner = round(MASTER * 0.86)
    canvas = Image.new('RGBA', (MASTER, MASTER), (0, 0, 0, 0))
    canvas.paste(square.resize((inner, inner), Image.Resampling.LANCZOS), ((MASTER - inner) // 2,) * 2)
    return finish(raster_clay(canvas))


def write_index(theme, name):
    lines = ['[Icon Theme]', f'Name={name}', 'Comment=Clay icons generated for installed applications',
             'Hidden=true', 'Inherits=hicolor']
    directories = [f'{s}x{s}/apps' for s in SIZES]
    scaled = [f'{s}x{s}@2x/apps' for s in DENSITIES]
    lines += ['Directories=' + ','.join(directories), 'ScaledDirectories=' + ','.join(scaled), '']
    for directory in directories:
        lines += [f'[{directory}]', f'Size={directory.split("x")[0]}', 'Context=Applications', 'Type=Fixed', '']
    for directory in scaled:
        lines += [f'[{directory}]', f'Size={directory.split("x")[0]}', 'Scale=2', 'Context=Applications', 'Type=Fixed', '']
    theme.mkdir(parents=True, exist_ok=True)
    (theme / 'index.theme').write_text('\n'.join(lines))
    for logical in DENSITIES:
        folder = theme / f'{logical}x{logical}@2x/apps'
        if folder.is_symlink() or folder.is_file():
            folder.unlink()
        if not folder.exists():
            folder.parent.mkdir(parents=True, exist_ok=True)
            folder.symlink_to(f'../{logical * 2}x{logical * 2}/apps')


def signature(user):
    entries = []
    for root in roots(user):
        for folder in (root / 'applications', root / 'icons/hicolor'):
            try:
                entries.append(f'{folder}:{folder.stat().st_mtime_ns}')
            except OSError:
                pass
    return hashlib.sha256('\n'.join(entries).encode()).hexdigest()


def run(user=False, only_if_changed=False, quiet=False, rebuild=False):
    if not user and os.geteuid() != 0:
        raise SystemExit('Run as root for all users, or with --user for this account.')
    home_icons = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'icons'
    target_root = home_icons if user else Path('/usr/share/icons')
    state_file = (Path.home() / '.cache/eduka-icons/clayify.json') if user else Path('/var/lib/eduka-icons/clayify.json')
    try:
        state = json.loads(state_file.read_text())
    except (OSError, ValueError):
        state = {}
    current = signature(user)
    if only_if_changed and state.get('signature') == current and not rebuild:
        return 0
    themes = {'standard': target_root / 'Eduka-Icons-Local', 'comfort': target_root / 'Eduka-Icons-Local-Comfort'}
    covered = eduka_names([Path('/usr/share/icons'), Path('/usr/local/share/icons'), home_icons])
    generated = {} if rebuild else state.get('icons', {})
    wanted = {}
    for name in sorted(desktop_icons(user)):
        if name in covered:
            continue
        source = find_source(name, user)
        if source is None:
            continue
        stamp = f'{source}:{source.stat().st_mtime_ns}'
        wanted[name] = stamp
        if generated.get(name) == stamp and (themes['standard'] / f'128x128/apps/{name}.png').exists():
            continue
        try:
            master = sculpt(source)
        except Exception as error:
            if not quiet:
                print(f'Skipped {name}: {error}', file=sys.stderr)
            continue
        for profile, theme in themes.items():
            for size in SIZES:
                folder = theme / f'{size}x{size}/apps'
                folder.mkdir(parents=True, exist_ok=True)
                image = master.resize((size, size), Image.Resampling.LANCZOS)
                save_png(comfort(image) if profile == 'comfort' else image, folder / f'{name}.png')
        generated[name] = stamp
        if not quiet:
            print(f'Clay icon for {name} (from {source})')
    for name in set(generated) - set(wanted):
        for theme in themes.values():
            for size in SIZES:
                (theme / f'{size}x{size}/apps/{name}.png').unlink(missing_ok=True)
        generated.pop(name)
    for profile, theme in themes.items():
        write_index(theme, theme.name)
        if shutil.which('gtk-update-icon-cache'):
            subprocess.run(['gtk-update-icon-cache', '-q', '-f', '-t', str(theme)], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps({'signature': current, 'icons': generated}, indent=1) + '\n')
    if not quiet:
        print(f'{len(generated)} installed applications use generated clay icons.')
    return 0


def main():
    parser = argparse.ArgumentParser(prog='eduka-icons-clayify', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--user', action='store_true', help='only this account (~/.local/share/icons)')
    parser.add_argument('--if-changed', action='store_true', help='do nothing when no application changed')
    parser.add_argument('--rebuild', action='store_true', help='regenerate every icon')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    raise SystemExit(run(args.user, args.if_changed, args.quiet, args.rebuild))


if __name__ == '__main__':
    main()
