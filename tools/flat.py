"""Flat (normal, non-clay) icons from the vendored Papirus set.

Tray applets, toolbars, emblems, emotes and animations use thousands of names
that Eduka does not draw itself (nm-applet stages, keyboard-layout indicators,
package states, ...). They are taken from Papirus (GPL-3.0), recoloured to the
variant's foreground colour and installed as scalable SVG next to the Eduka
line glyphs, so nothing falls through to another theme.
"""
import functools
import os
import re
import tarfile
from pathlib import Path

import settings

ROOT = Path(__file__).resolve().parents[1]
CACHE = settings.BUILD / 'upstream'
TEXT_COLOUR = re.compile(r'(\.ColorScheme-Text\s*\{\s*color\s*:\s*)#[0-9a-fA-F]{3,8}')
# upstream directory -> (theme directory, context, nominal size, min size, max size)
LAYOUT = {
    '16x16/actions': ('flat/16/actions', 'actions', 16, 8, 19),
    '22x22/actions': ('flat/22/actions', 'actions', 22, 20, 23),
    '24x24/actions': ('flat/24/actions', 'actions', 24, 24, 512),
    '16x16/panel': ('flat/16/panel', 'status', 16, 8, 19),
    '22x22/panel': ('flat/22/panel', 'status', 22, 20, 23),
    '24x24/panel': ('flat/24/panel', 'status', 24, 24, 512),
    '16x16/status': ('flat/16/status', 'status', 16, 8, 19),
    '22x22/status': ('flat/22/status', 'status', 22, 20, 23),
    '24x24/status': ('flat/24/status', 'status', 24, 24, 512),
    '16x16/emblems': ('flat/16/emblems', 'emblems', 16, 8, 19),
    '22x22/emblems': ('flat/22/emblems', 'emblems', 22, 20, 512),
    '22x22/emotes': ('flat/22/emotes', 'emotes', 22, 8, 23),
    '24x24/emotes': ('flat/24/emotes', 'emotes', 24, 24, 512),
    '24x24/animations': ('flat/24/animations', 'animations', 24, 8, 512),
}
SYMBOLIC = '16x16/symbolic'      # <context>/<name>-symbolic.svg


def archive(prefix):
    found = sorted((ROOT / 'assets/upstream').glob(f'{prefix}-*.tar.xz'))
    return found[-1] if found else None


def extract(prefix):
    """Unpack a vendored archive once and return its directory (or None)."""
    source = archive(prefix)
    if source is None:
        return None
    folder = CACHE / source.name.split('.tar')[0]
    marker = folder / '.complete'
    if not marker.exists():
        folder.mkdir(parents=True, exist_ok=True)
        with tarfile.open(source) as tar:
            tar.extractall(folder, filter='data')
        marker.write_text('ok\n')
    return folder


def _names(folder):
    """{name: real file} for SVG files and links that resolve inside ``folder``."""
    result = {}
    if not folder.is_dir():
        return result
    base = folder.resolve()
    for path in folder.iterdir():
        if path.suffix != '.svg':
            continue
        real = Path(os.path.realpath(path))
        if real.is_file() and real.parent == base:
            result[path.stem] = real
    return result


@functools.lru_cache(maxsize=1)
def tree():
    """{upstream dir: {name: real file}} of the flat set."""
    root = extract('papirus-flat')
    if root is None:
        return {}
    found = {directory: _names(root / directory) for directory in LAYOUT}
    symbolic = root / SYMBOLIC
    if symbolic.is_dir():
        for context in sorted(p.name for p in symbolic.iterdir() if p.is_dir()):
            found[f'{SYMBOLIC}/{context}'] = _names(symbolic / context)
    return found


def all_names():
    """Every non-symbolic flat name upstream provides."""
    return {name for directory, names in tree().items() if directory in LAYOUT for name in names}


def coloured_names():
    """Emote and emblem names upstream draws in colour (preferred over a one-colour glyph)."""
    return {name for directory, names in tree().items()
            if directory in LAYOUT and LAYOUT[directory][1] in ('emotes', 'emblems') for name in names}


def recolour(text, colour):
    """Use the variant's foreground colour for the icon's text-colour class."""
    return TEXT_COLOUR.sub(lambda match: match.group(1) + colour, text)


def install(theme, colour, taken, symbolic_taken, symbolic_contexts):
    """Write the flat set into ``theme``.

    taken: non-symbolic names already drawn by Eduka (clay or line glyph).
    symbolic_taken: ``-symbolic`` names (without suffix) Eduka draws.
    Returns {theme directory: (size, context, min, max)} for index.theme and
    the number of names written.
    """
    directories, count = {}, 0
    for upstream, names in tree().items():
        if upstream in LAYOUT:
            target, context, size, low, high = LAYOUT[upstream]
            skip = taken
        else:
            context = upstream.rsplit('/', 1)[1]
            if context not in symbolic_contexts:
                continue
            target, size, low, high = f'symbolic/{context}', 16, 8, 512
            skip = {f'{name}-symbolic' for name in symbolic_taken}
        folder = theme / target
        written = {}
        for name, real in sorted(names.items()):
            if name in skip or (upstream not in LAYOUT and not name.endswith('-symbolic')):
                continue
            folder.mkdir(parents=True, exist_ok=True)
            if real not in written:
                destination = folder / f'{real.stem}.svg'
                if real.stem in skip:      # the canonical name is Eduka's: keep the alias as a file
                    destination = folder / f'{name}.svg'
                if not destination.exists():
                    destination.write_text(recolour(real.read_text(encoding='utf-8', errors='ignore'), colour))
                written[real] = destination
            link = folder / f'{name}.svg'
            if not link.exists() and not link.is_symlink():
                link.symlink_to(written[real].name)
            count += 1
        if folder.is_dir() and upstream in LAYOUT:
            directories[target] = (size, context, low, high)
    return directories, count
