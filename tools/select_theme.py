#!/usr/bin/env python3
"""Select an Eduka-Icons theme for every desktop environment and window manager.

User mode (no sudo) writes the icon theme into the settings read by LXQt and
Eduka-Desktop, GTK 2/3/4, GNOME, Budgie, Cinnamon, MATE, Xfce, KDE Plasma,
LXDE, qt5ct/qt6ct and xsettingsd (i3, Openbox, Fluxbox, sway, ...).

System mode (root, e.g. the Cubic chroot terminal) writes the defaults used by
every new account and the live session, and can undo them again.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

VARIANTS = ('Light', 'Dark', 'Bright', 'Comfort')
HIDDEN = ('Eduka-Icons-Apps', 'Eduka-Icons-Apps-Comfort')
PREFIX = 'Eduka-Icons-'
STATE = Path('/var/lib/eduka-icons')
GSCHEMA_DIR = Path('/usr/share/glib-2.0/schemas')
GSCHEMA = GSCHEMA_DIR / '90_eduka-icons.gschema.override'
ICON_ROOTS = [Path('/usr/share/icons'), Path('/usr/local/share/icons')]
# Eduka-Desktop theme -> icon variant.
DESKTOP_THEMES = {'Edukasaun-Dark': 'Dark', 'Eduka-Transparan': 'Dark',
                  'Eduka-MultiColor': 'Bright', 'Eduka-Default-Theme': 'Light',
                  'Liquid Glass': 'Light', 'Eduka-Low-Theme': 'Light'}
GSETTINGS = (('org.gnome.desktop.interface', 'icon-theme'),
             ('org.cinnamon.desktop.interface', 'icon-theme'),
             ('org.mate.interface', 'icon-theme'))


def theme_name(variant):
    return PREFIX + variant


def log(message, quiet=False):
    if not quiet:
        print(message, flush=True)


def read_text(path):
    """Read a settings file without losing bytes that are not valid UTF-8."""
    return Path(path).read_text(encoding='utf-8', errors='surrogateescape')


def write_text(path, text):
    """Replace a settings file atomically, keeping its permissions."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    target = Path(os.path.realpath(path)) if path.is_symlink() else path   # keep dotfile-manager links
    temporary = target.with_name(f'.{target.name}.eduka-tmp')
    temporary.write_text(text, encoding='utf-8', errors='surrogateescape')
    try:
        shutil.copymode(target, temporary)
    except OSError:
        pass
    os.replace(temporary, target)


def backup_once(path):
    """Keep one copy of the file as it was before Eduka-Icons touched it."""
    copy = path.with_name(path.name + '.eduka-icons-backup')
    if path.is_file() and not copy.exists():
        shutil.copy2(path, copy)
    return copy


def read_ini_value(path, section, key):
    try:
        lines = read_text(path).splitlines()
    except OSError:
        return None
    current = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            current = stripped[1:-1]
        elif current == section and '=' in stripped and stripped.split('=', 1)[0].strip() == key:
            return stripped.split('=', 1)[1].strip()
    return None


def set_ini_value(path, section, key, value, backup=True):
    """Line-based INI update that keeps comments, order and key case intact."""
    path = Path(path)
    lines = read_text(path).splitlines() if path.exists() else []
    out, current, done, seen = [], None, False, False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            if current == section and not done:
                out.append(f'{key}={value}')
                done = True
            current = stripped[1:-1]
            seen = seen or current == section
        elif current == section and '=' in stripped and stripped.split('=', 1)[0].strip() == key:
            if not done:
                out.append(f'{key}={value}')
                done = True
            continue
        out.append(line)
    if not done:
        if not seen:
            if out and out[-1].strip():
                out.append('')
            out.append(f'[{section}]')
        elif current != section:
            # The section exists earlier in the file; insert after its header.
            index = out.index(f'[{section}]') + 1
            out.insert(index, f'{key}={value}')
            done = True
        if not done:
            out.append(f'{key}={value}')
    text = '\n'.join(out) + '\n'
    if path.exists() and read_text(path) == text:
        return False
    if backup:
        backup_once(path)
    write_text(path, text)
    return True


def remove_ini_value(path, section, key, only_prefix=PREFIX):
    path = Path(path)
    if not path.is_file():
        return False
    current, out, changed = None, [], False
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            current = stripped[1:-1]
        elif (current == section and '=' in stripped and stripped.split('=', 1)[0].strip() == key
              and stripped.split('=', 1)[1].strip().startswith(only_prefix)):
            changed = True
            continue
        out.append(line)
    if changed:
        write_text(path, '\n'.join(out) + '\n' if out else '')
    return changed


def set_line(path, pattern, line, create=True, backup=True):
    """Replace a 'key = value' style line (GTK 2, xsettingsd) or append it."""
    path = Path(path)
    if not path.exists() and not create:
        return False
    text = read_text(path) if path.exists() else ''
    lines = [l for l in text.splitlines() if not re.match(pattern, l.strip())]
    lines.append(line)
    new = '\n'.join(lines) + '\n'
    if new == text:
        return False
    if backup:
        backup_once(path)
    write_text(path, new)
    return True


def installed(variant, extra_roots=()):
    roots = [*extra_roots, *ICON_ROOTS]
    return any((root / theme_name(variant) / 'index.theme').is_file() for root in roots)


def run(command, quiet=True):
    try:
        return subprocess.run(command, check=False, timeout=10,
                              stdout=subprocess.DEVNULL if quiet else None,
                              stderr=subprocess.DEVNULL if quiet else None).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


# --- per-user settings ------------------------------------------------------

def user_dirs():
    home = Path.home()
    config = Path(os.environ.get('XDG_CONFIG_HOME', home / '.config'))
    data = Path(os.environ.get('XDG_DATA_HOME', home / '.local/share'))
    return home, config, data


def current_user_theme():
    home, config, _ = user_dirs()
    for path, section, key in ((config / 'lxqt/lxqt.conf', 'General', 'icon_theme'),
                               (Path('/etc/xdg/lxqt/lxqt.conf'), 'General', 'icon_theme'),
                               (config / 'gtk-3.0/settings.ini', 'Settings', 'gtk-icon-theme-name')):
        value = read_ini_value(path, section, key)
        if value:
            return value
    return ''


def apply_user(variant, quiet=False):
    if os.geteuid() == 0:
        raise SystemExit('Run the user selection without sudo. Use --system-defaults for an ISO.')
    theme = theme_name(variant)
    home, config, _ = user_dirs()
    done, failed = [], []

    def step(label, action, *args, **kwargs):
        """One settings file: a read-only or broken file must not stop the others."""
        try:
            action(*args, **kwargs)
        except (OSError, UnicodeError) as error:
            failed.append(f'{label} ({error.__class__.__name__})')
            return False
        if label:
            done.append(label)
        return True

    def xfce_file(path):
        text = read_text(path)
        new = re.sub(r'(<property name="IconThemeName" type="string" value=")[^"]*(")', rf'\g<1>{theme}\g<2>', text)
        if new != text:
            backup_once(path); write_text(path, new)

    # LXQt and Eduka-Desktop (Eduka-Menu, Eduka-Panel, Eduka-Settings).
    step('LXQt/Eduka-Desktop', set_ini_value, config / 'lxqt/lxqt.conf', 'General', 'icon_theme', theme)
    # GTK 3 and GTK 4 applications in every session.
    for gtk in ('gtk-3.0', 'gtk-4.0'):
        step('GTK 2/3/4', set_ini_value, config / gtk / 'settings.ini', 'Settings', 'gtk-icon-theme-name', theme)
    # GTK 2 applications.
    step('GTK 2/3/4', set_line, home / '.gtkrc-2.0', r'^gtk-icon-theme-name\s*=', f'gtk-icon-theme-name="{theme}"')
    # GNOME, Budgie, Unity, Cinnamon, MATE, Pantheon, sway (gsettings / dconf).
    bus = os.environ.get('DBUS_SESSION_BUS_ADDRESS')
    if shutil.which('gsettings') and bus:
        for schema, key in GSETTINGS:
            if run(['gsettings', 'set', schema, key, theme]):
                done.append(schema)
    # Xfce.
    xsettings = config / 'xfce4/xfconf/xfce-perchannel-xml/xsettings.xml'
    if shutil.which('xfconf-query') and bus:
        if run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/IconThemeName', '-n', '-t', 'string', '-s', theme]):
            done.append('Xfce')
    elif xsettings.is_file():
        step('Xfce', xfce_file, xsettings)
    # KDE Plasma 5/6.
    step('KDE', set_ini_value, config / 'kdeglobals', 'Icons', 'Theme', theme)
    if shutil.which('dbus-send') and bus:
        run(['dbus-send', '--session', '--type=signal', '/KIconLoader', 'org.kde.KIconLoader.iconChanged', 'int32:0'])
    # Qt outside LXQt/KDE.
    for tool in ('qt5ct', 'qt6ct'):
        conf = config / tool / f'{tool}.conf'
        if conf.exists() or shutil.which(tool):
            step(tool, set_ini_value, conf, 'Appearance', 'icon_theme', theme)
    # LXDE.
    lxde = config / 'lxsession/LXDE/desktop.conf'
    if lxde.exists():
        step('LXDE', set_ini_value, lxde, 'GTK', 'sNet/IconThemeName', theme)
    # xsettingsd (i3, Openbox, bspwm, Fluxbox, ...).
    for path in (home / '.xsettingsd', config / 'xsettingsd/xsettingsd.conf'):
        if path.exists() and step('xsettingsd', set_line, path, r'^Net/IconThemeName\s', f'Net/IconThemeName "{theme}"'):
            run(['pkill', '-HUP', '-x', 'xsettingsd'])
    # Ask Eduka-Desktop components to reload their icons.
    runtime = os.environ.get('XDG_RUNTIME_DIR')
    if runtime and Path(runtime, 'eduka-desktop').is_dir():
        step('', Path(runtime, 'eduka-desktop', 'reload').write_text, str(datetime.datetime.now().timestamp()))
    if not done:
        raise SystemExit(f'Could not write any settings file for {theme}: ' + ', '.join(failed))
    log(f'Selected {theme} for: ' + ', '.join(dict.fromkeys(done)) + '.', quiet)
    if failed:
        print('Not written: ' + ', '.join(dict.fromkeys(failed)) + '.', file=sys.stderr)
    log('Applications started before the change pick it up after a restart or a new login.', quiet)
    return theme


# --- Eduka-Desktop theme follower --------------------------------------------

def follow_state_path():
    return user_dirs()[1] / 'eduka-icons/follow.json'


def read_follow_state():
    try:
        state = json.loads(follow_state_path().read_text())
    except (OSError, ValueError):
        state = None
    if not isinstance(state, dict):
        state = {}
    return {'enabled': state.get('enabled', True) is not False, 'last_applied': str(state.get('last_applied') or '')}


def write_follow_state(state):
    try:
        write_text(follow_state_path(), json.dumps(state, indent=2) + '\n')
    except OSError:
        pass  # a read-only home must not break the session


def desktop_variant():
    """Icon variant that matches the Eduka-Desktop theme of this account."""
    path = user_dirs()[1] / 'eduka-desktop/desktop/settings.json'
    try:
        style = str(json.loads(path.read_text()).get('theme_style', ''))
    except (OSError, ValueError, AttributeError):
        style = ''
    for name, variant in DESKTOP_THEMES.items():
        if style.casefold() == name.casefold():
            return variant
    return 'Light'


def follow_once(quiet=True):
    """Switch Light/Dark/Bright with the Eduka-Desktop theme, never against a user choice.

    Returns a short reason: 'applied', 'unchanged', 'no-desktop', 'disabled',
    'other-theme', 'comfort', 'manual' or 'not-installed'.
    """
    config = user_dirs()[1]
    if not (config / 'eduka-desktop/desktop/settings.json').is_file():
        return 'no-desktop'  # Eduka-Desktop is not used by this account.
    state = read_follow_state()
    if not state['enabled']:
        return 'disabled'
    current = current_user_theme()
    if current and not current.startswith(PREFIX):
        return 'other-theme'  # A different icon theme was chosen; respect it.
    if current == theme_name('Comfort'):
        return 'comfort'  # Accessibility choice: never switched automatically.
    variant = desktop_variant()
    wanted = theme_name(variant)
    last = state['last_applied']
    if current == wanted:
        if last != wanted:   # remember it, so a later change by hand is recognised
            state.update(last_applied=wanted)
            write_follow_state(state)
        return 'unchanged'
    chosen_by_user = bool(read_ini_value(config / 'lxqt/lxqt.conf', 'General', 'icon_theme'))
    if chosen_by_user and last and current != last:
        # Picked by hand (e.g. in Eduka-Settings) since the last automatic switch: stop following.
        state.update(enabled=False, last_applied=current)
        write_follow_state(state)
        return 'manual'
    if not installed(variant, [user_dirs()[2] / 'icons']):
        return 'not-installed'
    apply_user(variant, quiet)
    state.update(enabled=True, last_applied=wanted)
    write_follow_state(state)
    return 'applied'


FOLLOW_MESSAGES = {
    'applied': None,
    'unchanged': 'The icon theme already matches the Eduka-Desktop theme.',
    'no-desktop': 'Eduka-Desktop settings were not found for this account; nothing to follow.',
    'disabled': 'Following is switched off.',
    'other-theme': 'Another icon theme is selected; run eduka-icons-select --apply Light first.',
    'comfort': 'Eduka-Icons-Comfort is selected and is never switched automatically.',
    'manual': 'The icon theme was chosen by hand; following is now off.',
    'not-installed': 'The matching Eduka-Icons variant is not installed.',
}


def watch(interval=3.0):
    """Follow Eduka-Desktop theme changes during the session (cheap mtime poll)."""
    import time
    path = user_dirs()[1] / 'eduka-desktop/desktop/settings.json'
    stamp = None
    while True:
        try:
            now = path.stat().st_mtime_ns
        except OSError:
            now = None
        if now != stamp:
            stamp = now
            try:
                follow_once()
            except (Exception, SystemExit) as error:   # keep the session helper alive
                print(f'eduka-icons-select: {error}', file=sys.stderr)
        time.sleep(interval)


# --- system defaults (Cubic / live ISO / all new users) ------------------------

def system_targets():
    targets = [('/etc/xdg/lxqt/lxqt.conf', 'General', 'icon_theme'),
               ('/etc/xdg/gtk-3.0/settings.ini', 'Settings', 'gtk-icon-theme-name'),
               ('/etc/xdg/gtk-4.0/settings.ini', 'Settings', 'gtk-icon-theme-name'),
               ('/etc/xdg/kdeglobals', 'Icons', 'Theme')]
    for tool in ('qt5ct', 'qt6ct'):
        if shutil.which(tool) or Path(f'/etc/xdg/{tool}/{tool}.conf').exists():
            targets.append((f'/etc/xdg/{tool}/{tool}.conf', 'Appearance', 'icon_theme'))
    if Path('/etc/xdg/lxsession/LXDE/desktop.conf').exists():
        targets.append(('/etc/xdg/lxsession/LXDE/desktop.conf', 'GTK', 'sNet/IconThemeName'))
    return targets


def compile_schemas():
    if shutil.which('glib-compile-schemas') and GSCHEMA_DIR.is_dir():
        run(['glib-compile-schemas', str(GSCHEMA_DIR)])


XFCE_SYSTEM = '/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml'
XFCE_VALUE = r'(<property name="IconThemeName" type="string" value=")([^"]*)(")'
GTK2_SKEL = '/etc/skel/.gtkrc-2.0'
GTK2_LINE = r'^gtk-icon-theme-name\s*=\s*(.*)$'


def _previous_path(root=Path('/')):
    return root / str(STATE).lstrip('/') / 'backup/previous-defaults.json'


def _line_value(path, pattern):
    try:
        for line in read_text(path).splitlines():
            match = re.match(pattern, line.strip())
            if match:
                return match.group(1).strip()
    except OSError:
        pass
    return None


def _remember_previous(root, targets):
    """Record the defaults that were in place before Eduka-Icons, once.

    Kept under /var/lib/eduka-icons/backup: backup files next to the originals
    would be copied into every new home directory from /etc/skel.
    """
    record = _previous_path(root)
    if record.exists():
        return
    def at(path): return root / str(path).lstrip('/')
    def keep(value): return value if value and not value.strip('"\'').startswith(PREFIX) else None
    previous = {'ini': [[path, section, key, keep(read_ini_value(at(path), section, key)), at(path).exists()]
                        for path, section, key in targets],
                'gtk2': keep(_line_value(at(GTK2_SKEL), GTK2_LINE)), 'gtk2_existed': at(GTK2_SKEL).exists(),
                'xfce': None}
    try:
        match = re.search(XFCE_VALUE, read_text(at(XFCE_SYSTEM)))
        previous['xfce'] = keep(match.group(2)) if match else None
    except OSError:
        pass
    write_text(record, json.dumps(previous, indent=2) + '\n')


def apply_system(variant, quiet=False, root=Path('/')):
    if os.geteuid() != 0 and root == Path('/'):
        raise SystemExit('System defaults require root (sudo, or the Cubic terminal).')
    theme = theme_name(variant)
    if root == Path('/') and not installed(variant):
        raise SystemExit(f'{theme} is not installed in /usr/share/icons. Install the eduka-icons package first.')
    def at(path): return root / str(path).lstrip('/')
    targets = system_targets()
    _remember_previous(root, targets)
    for path, section, key in targets:
        set_ini_value(at(path), section, key, theme, backup=False)
    set_line(at(GTK2_SKEL), r'^gtk-icon-theme-name\s*=', f'gtk-icon-theme-name="{theme}"', backup=False)
    xfce = at(XFCE_SYSTEM)
    if xfce.is_file():
        text = read_text(xfce)
        new = re.sub(XFCE_VALUE, rf'\g<1>{theme}\g<3>', text)
        if new != text:
            write_text(xfce, new)
    schema = at(GSCHEMA)
    write_text(schema, '# Written by eduka-icons-select --system-defaults\n' +
               ''.join(f'[{s}]\n{k}=\'{theme}\'\n\n' for s, k in GSETTINGS))
    if root == Path('/'):
        compile_schemas()
    write_text(at(STATE) / 'system-defaults.json', json.dumps(
        {'theme': theme, 'set_at': datetime.datetime.now().isoformat(timespec='seconds')}, indent=2) + '\n')
    log(f'{theme} is now the default icon theme for new accounts and the live session.', quiet)
    log('LXQt/Eduka-Desktop, GTK 2/3/4, GNOME/Cinnamon/MATE/Budgie, KDE, Xfce, LXDE and qt5ct/qt6ct defaults were set.', quiet)


def _drop_if_empty(path):
    """Delete a settings file that only holds empty sections (Eduka-Icons created it)."""
    try:
        if all(not l.strip() or l.strip().startswith('[') for l in read_text(path).splitlines()):
            path.unlink()
            path.parent.rmdir()
    except OSError:
        pass


def reset_system(quiet=False, root=Path('/')):
    """Put back the defaults that were in place before Eduka-Icons was selected."""
    if os.geteuid() != 0 and root == Path('/'):
        raise SystemExit('Resetting system defaults requires root.')
    def at(path): return root / str(path).lstrip('/')
    try:
        previous = json.loads(_previous_path(root).read_text())
        assert isinstance(previous, dict)
    except (OSError, ValueError, AssertionError):
        previous = {}
    known = {(p, s, k): (value, existed) for p, s, k, value, existed in previous.get('ini', [])
             if all(isinstance(x, str) for x in (p, s, k))}
    targets = dict.fromkeys([*system_targets(), *known])
    for path, section, key in targets:
        file = at(path)
        if not (read_ini_value(file, section, key) or '').startswith(PREFIX):
            continue                       # changed by the administrator since: leave it alone
        value, existed = known.get((path, section, key), (None, True))
        if isinstance(value, str) and value:
            set_ini_value(file, section, key, value, backup=False)
        else:
            remove_ini_value(file, section, key)
            if not existed:
                _drop_if_empty(file)
    skel = at(GTK2_SKEL)
    if PREFIX in (_line_value(skel, GTK2_LINE) or ''):
        lines = [l for l in read_text(skel).splitlines() if not re.match(GTK2_LINE, l.strip())]
        if isinstance(previous.get('gtk2'), str) and previous['gtk2']:
            lines.append(f'gtk-icon-theme-name={previous["gtk2"]}')
        if lines or previous.get('gtk2_existed'):
            write_text(skel, '\n'.join(lines) + '\n' if lines else '')
        else:
            skel.unlink()
    xfce = at(XFCE_SYSTEM)
    if xfce.is_file():
        text = read_text(xfce)
        match = re.search(XFCE_VALUE, text)
        if match and match.group(2).startswith(PREFIX):
            old = previous.get('xfce') if isinstance(previous.get('xfce'), str) else None
            legacy = xfce.with_name(xfce.name + '.eduka-icons-backup')      # written by 0.4/0.5
            if old:
                write_text(xfce, re.sub(XFCE_VALUE, lambda m: m.group(1) + old + m.group(3), text))
            elif legacy.is_file():
                os.replace(legacy, xfce)
    # Side-by-side backups of 0.4/0.5 (they leaked into new homes through /etc/skel).
    for path in [at(GTK2_SKEL), xfce, *(at(p) for p, _, _ in targets)]:
        path.with_name(path.name + '.eduka-icons-backup').unlink(missing_ok=True)
    schema = at(GSCHEMA)
    if schema.exists():
        schema.unlink()
        if root == Path('/'):
            compile_schemas()
    (at(STATE) / 'system-defaults.json').unlink(missing_ok=True)
    _previous_path(root).unlink(missing_ok=True)
    try: _previous_path(root).parent.rmdir()
    except OSError: pass
    log('Eduka-Icons system defaults were removed; the earlier defaults are back.', quiet)


# --- folder colours ---------------------------------------------------------------

FOLDER_MARK = '.eduka-folder-colour'


def folder_colours():
    """Colours shipped with the installed themes (from the asset file names)."""
    colours = set()
    for root in ICON_ROOTS:
        assets = root / theme_name('Light') / 'assets'
        for path in (sorted(assets.glob('48/folder*@*.png')) if assets.is_dir() else ()):
            colours.add(path.stem.split('@', 1)[1])
    return sorted(colours)


def set_folder_colour(colour, system=False, quiet=False):
    """Recolour every standard folder for this account (or for all users with --system).

    Nothing in the packaged themes is modified: overrides are symbolic links in
    a directory that icon lookups search first (~/.local/share/icons, or
    /usr/local/share/icons for all users). "default" removes them.
    """
    if system and os.geteuid() != 0:
        raise SystemExit('--system needs root.')
    if not system and os.geteuid() == 0:
        raise SystemExit('Run without sudo for your account, or add --system for all users.')
    available = folder_colours()
    if colour != 'default' and colour not in available:
        raise SystemExit(f'Unknown folder colour "{colour}". Available: default, ' + ', '.join(available))
    source_root = next((r for r in ICON_ROOTS if (r / theme_name('Light') / 'index.theme').is_file()), None)
    if source_root is None:
        raise SystemExit('The Eduka-Icons themes are not installed in /usr/share/icons.')
    target_root = Path('/usr/local/share/icons') if system else user_dirs()[2] / 'icons'
    if target_root == source_root:
        raise SystemExit('The themes are installed in /usr/local/share/icons; use the per-user mode.')
    for variant in VARIANTS:
        source = source_root / theme_name(variant)
        target = target_root / theme_name(variant)
        if not source.is_dir():
            continue
        # Remove earlier overrides (only links that point at Eduka folder assets).
        if (target / FOLDER_MARK).is_file():
            for link in target.glob('*/places/*.png'):
                if link.is_symlink() and '/assets/' in os.readlink(link) and '@' in os.readlink(link):
                    link.unlink()
            for folder in sorted(target.glob('*/places'), reverse=True):
                try: folder.rmdir(); folder.parent.rmdir()
                except OSError: pass
            (target / FOLDER_MARK).unlink()
            try: target.rmdir()
            except OSError: pass
        if colour == 'default':
            continue
        made = 0
        for places in sorted(source.glob('*/places')):
            for entry in places.iterdir():
                real = Path(os.path.realpath(entry))
                if real.parent.parent.name != 'assets' or '@' in real.stem:
                    continue
                if real.stem != 'folder' and not real.stem.startswith('folder-'):
                    continue
                tinted = real.with_name(f'{real.stem}@{colour}.png')
                if not tinted.is_file():
                    continue
                link = target / places.parent.name / 'places' / entry.name
                link.parent.mkdir(parents=True, exist_ok=True)
                if link.is_symlink() or link.exists():
                    link.unlink()
                link.symlink_to(tinted)
                made += 1
        if made:
            write_text(target / FOLDER_MARK, colour + '\n')
    if shutil.which('gtk-update-icon-cache'):
        for variant in VARIANTS:   # a stale cache in the override directory would hide the links
            cache = target_root / theme_name(variant) / 'icon-theme.cache'
            if cache.exists(): cache.unlink()
    log(f'Folder colour: {colour}. Open windows show it after the file manager restarts or a new login.', quiet)


# --- installation from a source checkout -------------------------------------

def install_from_build(destination, quiet=False):
    root = Path(__file__).resolve().parents[1]
    destination.mkdir(parents=True, exist_ok=True)
    for name in (*HIDDEN, *(theme_name(v) for v in VARIANTS)):
        source = root / 'build/themes' / name
        if not (source / 'index.theme').is_file():
            raise SystemExit('Run "make build" before installing from source.')
        target = destination / name
        if target.is_symlink():
            raise SystemExit(f'Refusing to overwrite a theme-directory symlink: {target}')
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target, symlinks=True, ignore=shutil.ignore_patterns('.eduka-build-owner'))
        if shutil.which('gtk-update-icon-cache'):
            run(['gtk-update-icon-cache', '-q', '-f', '-t', str(target)])
        log(f"Installed {name} in {target}", quiet)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='eduka-icons-select', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--apply', choices=VARIANTS, help='select Light, Dark, Bright or Comfort (eye comfort / low vision)')
    parser.add_argument('--system-defaults', action='store_true',
                        help='with --apply: set the default for all new users and the live ISO (root)')
    parser.add_argument('--reset-system-defaults', action='store_true', help='remove the system defaults (root)')
    parser.add_argument('--follow-desktop', action='store_true',
                        help='match the Eduka-Desktop theme (dark themes use Dark, Eduka-MultiColor uses Bright)')
    parser.add_argument('--watch', action='store_true', help='with --follow-desktop: keep following during the session')
    parser.add_argument('--install', metavar='DIR', type=Path, nargs='?', const=None, default=False,
                        help='copy the built themes (default: ~/.local/share/icons, or /usr/share/icons as root)')
    parser.add_argument('--folder-colour', '--folder-color', metavar='COLOUR', dest='folder_colour',
                        help='colour of the standard folders: default, or one of --list-folder-colours')
    parser.add_argument('--system', action='store_true', help='with --folder-colour: for all users (root)')
    parser.add_argument('--list-folder-colours', action='store_true', help='print the available folder colours')
    parser.add_argument('--status', action='store_true', help='show installed variants and the current selection')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)

    if args.install is not False:
        target = args.install or (Path('/usr/share/icons') if os.geteuid() == 0 else user_dirs()[2] / 'icons')
        install_from_build(target, args.quiet)
    if args.list_folder_colours:
        print('default ' + ' '.join(folder_colours()))
    if args.folder_colour:
        set_folder_colour(args.folder_colour, args.system, args.quiet)
    if args.reset_system_defaults:
        reset_system(args.quiet)
    if args.status:
        print('Installed:', ', '.join(v for v in VARIANTS if installed(v, [user_dirs()[2] / 'icons'])) or 'none')
        print('Current icon theme:', current_user_theme() or '(desktop default)')
        print('Follows Eduka-Desktop:', 'yes' if read_follow_state().get('enabled', True) else 'no')
    if args.apply:
        if args.system_defaults:
            apply_system(args.apply, args.quiet)
        else:
            apply_user(args.apply, args.quiet)
            state = read_follow_state()
            state.update(enabled=bool(args.follow_desktop), last_applied=theme_name(args.apply))
            write_follow_state(state)
    elif args.system_defaults:
        parser.error('--system-defaults needs --apply Light, Dark, Bright or Comfort')
    if args.follow_desktop and not args.apply:
        if os.geteuid() == 0:
            raise SystemExit('--follow-desktop runs in the desktop account, not as root.')
        state = read_follow_state()
        if not args.watch:
            # An explicit request turns following back on from the current theme.
            state.update(enabled=True, last_applied=current_user_theme())
            write_follow_state(state)
        result = follow_once(args.quiet)
        if not args.watch and FOLLOW_MESSAGES.get(result):
            log(FOLLOW_MESSAGES[result], args.quiet)
        if args.watch:
            watch()
    if len(sys.argv if argv is None else argv) <= (0 if argv is not None else 1):
        parser.print_help()


if __name__ == '__main__':
    main()
