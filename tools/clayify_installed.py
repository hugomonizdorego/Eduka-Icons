#!/usr/bin/env python3
"""Give every installed application an Eduka clay icon.

Scans the .desktop files of installed applications (Debian packages, Flatpak,
Snap and local installs). Each icon name that the Eduka-Icons themes do not
draw yet is converted from the application's own icon into clay.

The generated icons are an overlay of the catalog themes: they are written to
the same theme names (Eduka-Icons-Apps and Eduka-Icons-Apps-Comfort) in another
icon base directory, /usr/local/share/icons for all users or
~/.local/share/icons with --user. Icon lookups merge the directories of one
theme across all base directories, so no extra theme is needed and nothing in
the packaged themes is modified. Runs after every apt/dpkg operation and when
Flatpak or Snap applications change.
"""
import argparse
import configparser
import glob
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import re
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:                                        # Pillow and librsvg can be half-installed during an upgrade
    from PIL import Image  # noqa: E402
    from clayify import clay_svg, render_svg, raster_clay, open_raster, finish, comfort, sharpen, save_png  # noqa: E402
    MISSING = None
except (ImportError, OSError) as error:
    MISSING = error

MASTER = 256
STYLE = 'clay-1.0'          # change to regenerate every icon after an upgrade
TIMEOUT = 60                # seconds for one application icon
MEMORY = 1536 * 1024 * 1024
THEMES = {'standard': 'Eduka-Icons-Apps', 'comfort': 'Eduka-Icons-Apps-Comfort'}
COVERED_BY = ('Eduka-Icons-Light', 'Eduka-Icons-Apps')
SYSTEM_ICONS = (Path('/usr/share/icons'), )
SYSTEM_OVERLAY = Path('/usr/local/share/icons')
OLD_THEMES = ('Eduka-Icons-Local', 'Eduka-Icons-Local-Comfort')     # 0.5.0 layout
SAFE_NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._+@-]{0,200}$')
MARK = '.eduka-clayify.json'


def roots(user):
    home = Path.home()
    data = Path(os.environ.get('XDG_DATA_HOME', home / '.local/share'))
    system = [Path('/usr/share'), Path('/usr/local/share'), Path('/var/lib/flatpak/exports/share'),
              Path('/var/lib/snapd/desktop')]
    return ([data, data / 'flatpak/exports/share'] if user else []) + system


def desktop_icons(user):
    """Icon names of every application entry (plain names only, no paths)."""
    names = set()
    folders = [r / 'applications' for r in roots(user)] + [Path('/etc/xdg/autostart')]
    for folder in folders:
        if not folder.is_dir():
            continue
        for path in folder.rglob('*.desktop'):
            try:
                text = path.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue
            for line in text.splitlines():
                if line.startswith('Icon='):
                    icon = line[5:].strip()
                    if icon.endswith(('.png', '.svg', '.xpm')) and '/' not in icon:
                        icon = icon.rsplit('.', 1)[0]
                    if SAFE_NAME.match(icon):
                        names.add(icon)
                    break
    return names


def catalog_sizes():
    """(sizes, hidpi sizes) of the installed catalog theme, read from its index.theme."""
    for root in SYSTEM_ICONS:
        index = root / THEMES['standard'] / 'index.theme'
        if not index.is_file():
            continue
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read(index)
        head = cfg['Icon Theme']
        plain = sorted({int(d.split('x')[0]) for d in head.get('Directories', '').split(',') if d.endswith('/apps')})
        scaled = sorted({int(d.split('x')[0]) for d in head.get('ScaledDirectories', '').split(',') if d.endswith('/apps')})
        if plain:
            return plain, [s for s in scaled if s * 2 in plain]
    return None, None


def covered_names():
    """Names the packaged Eduka themes already draw (any context, any directory)."""
    names = set()
    for root in SYSTEM_ICONS:
        for theme in COVERED_BY:
            folder = root / theme
            if not folder.is_dir():
                continue
            for directory, _, files in os.walk(folder):
                if '/assets' in directory:
                    continue
                names.update(f.rsplit('.', 1)[0] for f in files if f.endswith(('.png', '.svg')))
    return names


def find_sources(name, user):
    """Original icons, best first: scalable SVG, then PNGs from large to small, then pixmaps."""
    found = []
    pattern = glob.escape(name)
    for root in roots(user):
        for theme in ('hicolor', 'Papirus', 'Adwaita', 'breeze'):
            base = root / 'icons' / theme
            if not base.is_dir():
                continue
            for candidate in base.glob(f'*/apps/{pattern}.*'):
                if candidate.stem != name or candidate.suffix not in ('.svg', '.png') or not candidate.is_file():
                    continue
                match = re.match(r'^(\d+)x\d+', candidate.parent.parent.name)
                size = 4096 if candidate.suffix == '.svg' else int(match.group(1)) if match else 1
                found.append((-size, len(found), candidate))
        for extension in ('svg', 'png'):
            pixmap = root / 'pixmaps' / f'{name}.{extension}'
            if pixmap.is_file():
                found.append((0, len(found), pixmap))
    return [path for _, _, path in sorted(found)]


def sculpt(source):
    """Clay master (256 px RGBA) of one original icon."""
    if source.suffix == '.svg':
        if source.stat().st_size > 2 * 1024 * 1024:
            raise ValueError('SVG too large')
        text = source.read_text(encoding='utf-8', errors='ignore')
        try:
            image = render_svg(clay_svg(text), MASTER)
            if image.getchannel('A').getbbox() is None:
                raise ValueError('empty render')
            image = finish(image)
        except Exception:
            image = finish(raster_clay(render_svg(text, MASTER)))
    else:
        image = open_raster(source)
        side = max(image.size)
        square = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        square.paste(image, ((side - image.width) // 2, (side - image.height) // 2))
        image = finish(raster_clay(square.resize((MASTER, MASTER), Image.Resampling.LANCZOS)))
    box = image.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    if box is None or (box[2] - box[0]) < MASTER // 8 or (box[3] - box[1]) < MASTER // 8:
        raise ValueError('blank icon')
    return image


def _sculpt_child(source, target):
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY, MEMORY))
        resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT, TIMEOUT + 5))
    except (ImportError, ValueError, OSError):
        pass
    try:
        sculpt(source).save(target, 'PNG')
    except BaseException as error:
        print(f'{error.__class__.__name__}: {error}', file=sys.stderr)
        os._exit(1)
    os._exit(0)


def sculpt_safely(source, scratch):
    """Run one conversion in a child process: a hostile or huge icon cannot stall or crash apt."""
    scratch.unlink(missing_ok=True)
    child = multiprocessing.get_context('fork').Process(target=_sculpt_child, args=(source, scratch))
    stderr = os.dup(2)
    try:
        null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(null, 2); os.close(null)            # librsvg warnings of the child
        child.start()
    finally:
        os.dup2(stderr, 2); os.close(stderr)
    child.join(TIMEOUT + 10)
    if child.is_alive():
        child.kill(); child.join()
        raise TimeoutError('took too long')
    if child.exitcode != 0 or not scratch.is_file():
        raise ValueError('could not be converted')
    with Image.open(scratch) as image:
        image.load()
        return image.convert('RGBA')


def _safe_dir(path):
    """Create a real directory; refuse to write through a symbolic link."""
    for part in (path, *path.parents):
        if part.is_symlink():
            raise SystemExit(f'Refusing to write through a symbolic link: {part}')
    path.mkdir(parents=True, exist_ok=True)


def _write(image, target, quality):
    temporary = target.with_name(f'.{target.name}.tmp')
    if temporary.is_symlink() or temporary.exists():
        temporary.unlink()
    save_png(image, temporary, quality)
    os.replace(temporary, target)          # atomic, and never follows a link at the target


def signature(user):
    entries = []
    for root in roots(user):
        for folder in (root / 'applications', root / 'icons/hicolor', root / 'pixmaps'):
            try:
                entries.append(f'{folder}:{folder.stat().st_mtime_ns}')
                entries += [f'{p}:{p.stat().st_mtime_ns}' for p in sorted(folder.glob('*/apps'))[:64]]
            except OSError:
                pass
    for root in SYSTEM_ICONS:
        try:
            entries.append(f'{root / THEMES["standard"] / "index.theme"}:{(root / THEMES["standard"] / "index.theme").stat().st_mtime_ns}')
        except OSError:
            pass
    return hashlib.sha256('\n'.join([STYLE, *entries]).encode()).hexdigest()


def remove_old_layout(quiet):
    """0.5.0 wrote separate Eduka-Icons-Local themes, which hid the catalog behind hicolor."""
    for name in OLD_THEMES:
        folder = Path('/usr/share/icons') / name
        index = folder / 'index.theme'
        if index.is_file() and 'generated for installed applications' in index.read_text(errors='ignore'):
            shutil.rmtree(folder, ignore_errors=True)
            if not quiet:
                print(f'Removed old generated theme {folder}')


def remove_overlay(user=False, quiet=False):
    """Delete everything this tool generated."""
    target_root = _target_root(user)
    for theme in THEMES.values():
        folder = target_root / theme
        mark = folder / MARK
        if not mark.is_file():
            continue
        try:
            names = json.loads(mark.read_text()).get('icons', {})
        except (OSError, ValueError):
            names = {}
        for directory in list(folder.glob('*/apps')):
            for name in names:
                (directory / f'{name}.png').unlink(missing_ok=True)
            try:
                directory.rmdir(); directory.parent.rmdir()
            except OSError:
                pass
        mark.unlink(missing_ok=True)
        try:
            folder.rmdir()
        except OSError:
            pass
    if not quiet:
        print('Generated clay icons removed.')


def _target_root(user):
    if user:
        return Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'icons'
    return SYSTEM_OVERLAY


def run(user=False, only_if_changed=False, quiet=False, rebuild=False):
    if not user and os.geteuid() != 0:
        raise SystemExit('Run as root for all users, or with --user for this account.')
    if MISSING is not None:
        if not quiet:
            print(f'eduka-icons-clayify needs python3-pil and librsvg2-2: {MISSING}', file=sys.stderr)
        return 0 if quiet else 1
    sizes, hidpi = catalog_sizes()
    if not sizes:
        if not quiet:
            print('The Eduka-Icons catalog theme is not installed; nothing to do.')
        return 0
    if not user:
        remove_old_layout(quiet)
    target_root = _target_root(user)
    standard = target_root / THEMES['standard']
    mark = standard / MARK
    try:
        state = json.loads(mark.read_text())
        assert isinstance(state, dict) and isinstance(state.get('icons', {}), dict)
    except (OSError, ValueError, AssertionError):
        state = {}
    current = signature(user)
    if only_if_changed and state.get('signature') == current and not rebuild:
        return 0
    covered = covered_names()
    previous = {n: v for n, v in state.get('icons', {}).items() if SAFE_NAME.match(str(n))}
    # A new clay style or another set of sizes regenerates everything.
    same_style = state.get('style') == STYLE and state.get('sizes') == sizes
    generated = dict(previous) if same_style and not rebuild else {}
    wanted = {}
    _safe_dir(standard)
    scratch = standard / f'.sculpt-{os.getpid()}.png'
    try:
        for name in sorted(desktop_icons(user)):
            if name in covered:
                continue
            for source in find_sources(name, user):
                try:
                    stamp = f'{source}:{source.stat().st_mtime_ns}'
                except OSError:
                    continue
                if generated.get(name) == stamp and (standard / f'{sizes[-1]}x{sizes[-1]}/apps/{name}.png').exists():
                    wanted[name] = stamp
                    break
                try:
                    master = sculpt_safely(source, scratch)
                except Exception as error:
                    if not quiet:
                        print(f'Skipped {source}: {error}', file=sys.stderr)
                    continue                  # try the next original of this application
                for profile, theme in THEMES.items():
                    for size in sizes:
                        folder = target_root / theme / f'{size}x{size}/apps'
                        _safe_dir(folder)
                        if profile == 'comfort':
                            image = comfort(master, size)
                        else:
                            image = sharpen(master.resize((size, size), Image.Resampling.LANCZOS), size)
                        _write(image, folder / f'{name}.png', 'lossless' if size <= 24 else 'small')
                    for logical in hidpi:      # real directories with file links (no directory links)
                        folder = target_root / theme / f'{logical}x{logical}@2x/apps'
                        _safe_dir(folder)
                        link = folder / f'{name}.png'
                        if link.is_symlink() or link.exists():
                            link.unlink()
                        link.symlink_to(f'../../{logical * 2}x{logical * 2}/apps/{name}.png')
                wanted[name] = generated[name] = stamp
                if not quiet:
                    print(f'Clay icon for {name} (from {source})')
                break
    finally:
        scratch.unlink(missing_ok=True)
    # Applications that were removed, or that the packaged themes draw now.
    for name in (set(previous) | set(generated)) - set(wanted):
        for theme in THEMES.values():
            for directory in (target_root / theme).glob('*/apps'):
                (directory / f'{name}.png').unlink(missing_ok=True)
        generated.pop(name, None)
    if generated or mark.exists():
        for theme in THEMES.values():
            _safe_dir(target_root / theme)
            stale = target_root / theme / 'icon-theme.cache'    # a cache without index.theme would hide new icons
            if stale.exists():
                stale.unlink()
            record = target_root / theme / MARK
            temporary = record.with_name(record.name + '.tmp')
            if temporary.is_symlink() or temporary.exists():
                temporary.unlink()
            temporary.write_text(json.dumps({'signature': current, 'style': STYLE, 'sizes': sizes,
                                             'icons': generated}, indent=1) + '\n')
            os.replace(temporary, record)
    else:
        for theme in THEMES.values():
            try: (target_root / theme).rmdir()
            except OSError: pass
    if not quiet:
        print(f'{len(generated)} installed applications use generated clay icons in {target_root}.')
    return 0


def main():
    parser = argparse.ArgumentParser(prog='eduka-icons-clayify', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--user', action='store_true', help='only this account (~/.local/share/icons)')
    parser.add_argument('--if-changed', action='store_true', help='do nothing when no application changed')
    parser.add_argument('--rebuild', action='store_true', help='regenerate every icon')
    parser.add_argument('--remove', action='store_true', help='delete the generated icons')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    if args.remove:
        if not args.user and os.geteuid() != 0:
            raise SystemExit('Run as root, or with --user.')
        remove_overlay(args.user, args.quiet)
        raise SystemExit(0)
    raise SystemExit(run(args.user, args.if_changed, args.quiet, args.rebuild))


if __name__ == '__main__':
    main()
