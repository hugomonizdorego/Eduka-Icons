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

VARIANTS = ('Light', 'Dark', 'Bright')
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


def backup_once(path):
    """Keep one copy of the file as it was before Eduka-Icons touched it."""
    copy = path.with_name(path.name + '.eduka-icons-backup')
    if path.is_file() and not copy.exists():
        shutil.copy2(path, copy)
    return copy


def read_ini_value(path, section, key):
    try:
        lines = Path(path).read_text(encoding='utf-8', errors='ignore').splitlines()
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
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = path.read_text(encoding='utf-8', errors='ignore').splitlines() if path.exists() else []
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
    if path.exists() and path.read_text(encoding='utf-8', errors='ignore') == text:
        return False
    if backup:
        backup_once(path)
    path.write_text(text, encoding='utf-8')
    return True


def remove_ini_value(path, section, key, only_prefix=PREFIX):
    path = Path(path)
    if not path.is_file():
        return False
    current, out, changed = None, [], False
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            current = stripped[1:-1]
        elif (current == section and '=' in stripped and stripped.split('=', 1)[0].strip() == key
              and stripped.split('=', 1)[1].strip().startswith(only_prefix)):
            changed = True
            continue
        out.append(line)
    if changed:
        backup = path.with_name(path.name + '.eduka-icons-backup')
        if not backup.exists() and all(not l.strip() or l.strip().startswith('[') for l in out):
            path.unlink()  # Only Eduka-Icons ever wrote this file.
            try: path.parent.rmdir()
            except OSError: pass
        else:
            path.write_text('\n'.join(out) + '\n', encoding='utf-8')
            if backup.exists(): backup.unlink()
    return changed


def set_line(path, pattern, line, create=True):
    """Replace a 'key = value' style line (GTK 2, xsettingsd) or append it."""
    path = Path(path)
    if not path.exists() and not create:
        return False
    text = path.read_text(encoding='utf-8', errors='ignore') if path.exists() else ''
    lines = [l for l in text.splitlines() if not re.match(pattern, l.strip())]
    lines.append(line)
    new = '\n'.join(lines) + '\n'
    if new == text:
        return False
    backup_once(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(new, encoding='utf-8')
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
    done = []
    # LXQt and Eduka-Desktop (Eduka-Menu, Eduka-Panel, Eduka-Settings).
    set_ini_value(config / 'lxqt/lxqt.conf', 'General', 'icon_theme', theme); done.append('LXQt/Eduka-Desktop')
    # GTK 3 and GTK 4 applications in every session.
    for gtk in ('gtk-3.0', 'gtk-4.0'):
        set_ini_value(config / gtk / 'settings.ini', 'Settings', 'gtk-icon-theme-name', theme)
    # GTK 2 applications.
    set_line(home / '.gtkrc-2.0', r'^gtk-icon-theme-name\s*=', f'gtk-icon-theme-name="{theme}"')
    done.append('GTK 2/3/4')
    # GNOME, Budgie, Unity, Cinnamon, MATE, Pantheon, sway (gsettings / dconf).
    if shutil.which('gsettings') and os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        for schema, key in GSETTINGS:
            if run(['gsettings', 'set', schema, key, theme]):
                done.append(schema)
    # Xfce.
    if shutil.which('xfconf-query') and os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        if run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/IconThemeName', '-n', '-t', 'string', '-s', theme]):
            done.append('Xfce')
    else:
        xsettings = config / 'xfce4/xfconf/xfce-perchannel-xml/xsettings.xml'
        if xsettings.is_file():
            text = xsettings.read_text(encoding='utf-8', errors='ignore')
            new = re.sub(r'(<property name="IconThemeName" type="string" value=")[^"]*(")', rf'\g<1>{theme}\g<2>', text)
            if new != text:
                backup_once(xsettings); xsettings.write_text(new, encoding='utf-8'); done.append('Xfce')
    # KDE Plasma 5/6.
    set_ini_value(config / 'kdeglobals', 'Icons', 'Theme', theme); done.append('KDE')
    if shutil.which('dbus-send') and os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        run(['dbus-send', '--session', '--type=signal', '/KIconLoader', 'org.kde.KIconLoader.iconChanged', 'int32:0'])
    # Qt outside LXQt/KDE.
    for tool in ('qt5ct', 'qt6ct'):
        conf = config / tool / f'{tool}.conf'
        if conf.exists() or shutil.which(tool):
            set_ini_value(conf, 'Appearance', 'icon_theme', theme); done.append(tool)
    # LXDE.
    lxde = config / 'lxsession/LXDE/desktop.conf'
    if lxde.exists():
        set_ini_value(lxde, 'GTK', 'sNet/IconThemeName', theme); done.append('LXDE')
    # xsettingsd (i3, Openbox, bspwm, Fluxbox, ...).
    for path in (home / '.xsettingsd', config / 'xsettingsd/xsettingsd.conf'):
        if path.exists():
            set_line(path, r'^Net/IconThemeName\s', f'Net/IconThemeName "{theme}"'); done.append('xsettingsd')
            run(['pkill', '-HUP', '-x', 'xsettingsd'])
    # Ask Eduka-Desktop components to reload their icons.
    runtime = os.environ.get('XDG_RUNTIME_DIR')
    if runtime and Path(runtime, 'eduka-desktop').is_dir():
        Path(runtime, 'eduka-desktop', 'reload').write_text(str(datetime.datetime.now().timestamp()))
    log(f'Selected {theme} for: ' + ', '.join(dict.fromkeys(done)) + '.', quiet)
    log('Applications started before the change pick it up after a restart or a new login.', quiet)
    return theme


# --- Eduka-Desktop theme follower --------------------------------------------

def follow_state_path():
    return user_dirs()[1] / 'eduka-icons/follow.json'


def read_follow_state():
    try:
        return json.loads(follow_state_path().read_text())
    except (OSError, ValueError):
        return {'enabled': True, 'last_applied': ''}


def write_follow_state(state):
    path = follow_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + '\n')


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
    """Switch Light/Dark/Bright with the Eduka-Desktop theme, never against a user choice."""
    config = user_dirs()[1]
    if not (config / 'eduka-desktop/desktop/settings.json').is_file():
        return False  # Eduka-Desktop is not used by this account.
    state = read_follow_state()
    if not state.get('enabled', True):
        return False
    current = current_user_theme()
    if current and not current.startswith(PREFIX):
        return False  # A different icon theme was chosen; respect it.
    variant = desktop_variant()
    wanted = theme_name(variant)
    chosen_by_user = bool(read_ini_value(config / 'lxqt/lxqt.conf', 'General', 'icon_theme'))
    last = state.get('last_applied', '')
    if chosen_by_user and current != (last or wanted):
        # Picked by hand (e.g. in Eduka-Settings): stop following.
        state.update(enabled=False, last_applied=current)
        write_follow_state(state)
        return False
    if wanted == current or not installed(variant, [user_dirs()[2] / 'icons']):
        return False
    apply_user(variant, quiet)
    state.update(enabled=True, last_applied=wanted)
    write_follow_state(state)
    return True


def watch(interval=3.0):
    """Follow Eduka-Desktop theme changes during the session (cheap mtime poll)."""
    import time
    path = user_dirs()[1] / 'eduka-desktop/desktop/settings.json'
    stamp = None
    while True:
        try:
            now = path.stat().st_mtime
        except OSError:
            now = None
        if now != stamp:
            stamp = now
            follow_once()
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


def apply_system(variant, quiet=False, root=Path('/')):
    if os.geteuid() != 0 and root == Path('/'):
        raise SystemExit('System defaults require root (sudo, or the Cubic terminal).')
    theme = theme_name(variant)
    if root == Path('/') and not installed(variant):
        raise SystemExit(f'{theme} is not installed in /usr/share/icons. Install the eduka-icons package first.')
    def at(path): return root / str(path).lstrip('/')
    for path, section, key in system_targets():
        set_ini_value(at(path), section, key, theme)
    set_line(at('/etc/skel/.gtkrc-2.0'), r'^gtk-icon-theme-name\s*=', f'gtk-icon-theme-name="{theme}"')
    xfce = at('/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml')
    if xfce.is_file():
        text = xfce.read_text(encoding='utf-8', errors='ignore')
        new = re.sub(r'(<property name="IconThemeName" type="string" value=")[^"]*(")', rf'\g<1>{theme}\g<2>', text)
        if new != text:
            backup_once(xfce); xfce.write_text(new, encoding='utf-8')
    schema = at(GSCHEMA)
    schema.parent.mkdir(parents=True, exist_ok=True)
    schema.write_text('# Written by eduka-icons-select --system-defaults\n' +
                      ''.join(f'[{s}]\n{k}=\'{theme}\'\n\n' for s, k in GSETTINGS))
    if root == Path('/'):
        compile_schemas()
    state = at(STATE)
    state.mkdir(parents=True, exist_ok=True)
    (state / 'system-defaults.json').write_text(json.dumps({'theme': theme, 'set_at': datetime.datetime.now().isoformat(timespec='seconds')}, indent=2) + '\n')
    log(f'{theme} is now the default icon theme for new accounts and the live session.', quiet)
    log('LXQt/Eduka-Desktop, GTK 2/3/4, GNOME/Cinnamon/MATE/Budgie, KDE, Xfce, LXDE and qt5ct/qt6ct defaults were set.', quiet)


def reset_system(quiet=False):
    if os.geteuid() != 0:
        raise SystemExit('Resetting system defaults requires root.')
    for path, section, key in system_targets():
        remove_ini_value(Path(path), section, key)
    skel = Path('/etc/skel/.gtkrc-2.0')
    if skel.is_file():
        lines = [l for l in skel.read_text().splitlines() if not (l.startswith('gtk-icon-theme-name') and PREFIX in l)]
        if lines: skel.write_text('\n'.join(lines) + '\n')
        else: skel.unlink()
    xfce = Path('/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml')
    backup = xfce.with_name(xfce.name + '.eduka-icons-backup')
    if xfce.is_file() and backup.is_file() and PREFIX in xfce.read_text(errors='ignore'):
        shutil.move(str(backup), str(xfce))
    if GSCHEMA.exists():
        GSCHEMA.unlink()
        compile_schemas()
    if (STATE / 'system-defaults.json').exists():
        (STATE / 'system-defaults.json').unlink()
    log('Eduka-Icons system defaults were removed.', quiet)


# --- installation from a source checkout -------------------------------------

def install_from_build(destination, quiet=False):
    root = Path(__file__).resolve().parents[1]
    destination.mkdir(parents=True, exist_ok=True)
    for variant in VARIANTS:
        source = root / 'build/themes' / theme_name(variant)
        if not (source / 'index.theme').is_file():
            raise SystemExit('Run "make build" before installing from source.')
        target = destination / theme_name(variant)
        if target.is_symlink():
            raise SystemExit(f'Refusing to overwrite a theme-directory symlink: {target}')
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target, symlinks=True, ignore=shutil.ignore_patterns('.eduka-build-owner'))
        if shutil.which('gtk-update-icon-cache'):
            run(['gtk-update-icon-cache', '-q', '-f', '-t', str(target)])
        log(f'Installed {theme_name(variant)} in {target}', quiet)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='eduka-icons-select', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--apply', choices=VARIANTS, help='select Light, Dark or Bright')
    parser.add_argument('--system-defaults', action='store_true',
                        help='with --apply: set the default for all new users and the live ISO (root)')
    parser.add_argument('--reset-system-defaults', action='store_true', help='remove the system defaults (root)')
    parser.add_argument('--follow-desktop', action='store_true',
                        help='match the Eduka-Desktop theme (dark themes use Dark, Eduka-MultiColor uses Bright)')
    parser.add_argument('--watch', action='store_true', help='with --follow-desktop: keep following during the session')
    parser.add_argument('--install', metavar='DIR', type=Path, nargs='?', const=None, default=False,
                        help='copy the built themes (default: ~/.local/share/icons, or /usr/share/icons as root)')
    parser.add_argument('--status', action='store_true', help='show installed variants and the current selection')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)

    if args.install is not False:
        target = args.install or (Path('/usr/share/icons') if os.geteuid() == 0 else user_dirs()[2] / 'icons')
        install_from_build(target, args.quiet)
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
        parser.error('--system-defaults needs --apply Light, Dark or Bright')
    if args.follow_desktop and not args.apply:
        if os.geteuid() == 0:
            raise SystemExit('--follow-desktop runs in the desktop account, not as root.')
        state = read_follow_state()
        if not args.watch:
            # An explicit request turns following back on from the current theme.
            state.update(enabled=True, last_applied=current_user_theme())
            write_follow_state(state)
        follow_once(args.quiet)
        if args.watch:
            watch()
    if len(sys.argv if argv is None else argv) <= (0 if argv is not None else 1):
        parser.print_help()


if __name__ == '__main__':
    main()
