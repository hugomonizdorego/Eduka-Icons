#!/usr/bin/env python3
"""Build the eduka-icons .deb (Light, Dark and Bright) from build/themes."""
import argparse
import gzip
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / 'VERSION').read_text().strip()
VARIANTS = ('Light', 'Dark', 'Bright')

CONTROL = '''Package: eduka-icons
Version: {version}
Section: x11
Priority: optional
Architecture: all
Maintainer: Edukasaun OS <dev@edukasaun.org>
Depends: python3, hicolor-icon-theme
Recommends: papirus-icon-theme, gtk-update-icon-cache | libgtk-3-bin
Suggests: edukasaun-desktop-menu
Enhances: edukasaun-desktop-menu
Installed-Size: {size}
Homepage: https://github.com/hugomonizdorego/Eduka-Icons
Description: Edukasaun OS clay icon themes (Light, Dark and Bright)
 Official icon themes of Edukasaun OS with hand-sculpted clay artwork:
  * Eduka-Icons-Light  - for light desktop themes (default)
  * Eduka-Icons-Dark   - for dark desktop themes
  * Eduka-Icons-Bright - vivid colours for bright, colourful themes
 .
 More than a thousand application, folder, device, file-type and settings
 names use Eduka clay artwork, and over four hundred symbolic panel and
 toolbar icons are drawn for GTK, Qt and KDE recolouring. Anything else falls
 back to Papirus, Breeze, Adwaita and hicolor.
 .
 On first installation Eduka-Icons-Light becomes the system default for
 Eduka-Desktop/LXQt, GTK, GNOME, Cinnamon, MATE, Budgie, Xfce, KDE and LXDE.
 Set EDUKA_ICONS_DEFAULT=Dark or Bright to choose another default, or
 EDUKA_ICONS_NO_DEFAULT=1 to keep the current one.
'''

POSTINST = '''#!/bin/sh
set -e
STATE=/var/lib/eduka-icons
case "$1" in
  configure)
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
      for theme in Eduka-Icons-Light Eduka-Icons-Dark Eduka-Icons-Bright; do
        [ -d "/usr/share/icons/$theme" ] && gtk-update-icon-cache -q -f -t "/usr/share/icons/$theme" || true
      done
    fi
    if [ "${EDUKA_ICONS_NO_DEFAULT:-0}" != "1" ] && [ ! -e "$STATE/defaults-initialized" ]; then
      variant="${EDUKA_ICONS_DEFAULT:-Light}"
      case "$variant" in Light|Dark|Bright) ;; *) variant=Light ;; esac
      if python3 /usr/lib/eduka-icons/select_theme.py --apply "$variant" --system-defaults --quiet; then
        mkdir -p "$STATE"
        echo "$variant" > "$STATE/defaults-initialized"
        echo "Eduka-Icons-$variant is now the default icon theme."
      else
        echo "eduka-icons: could not set the default icon theme; run eduka-icons-select --apply Light --system-defaults" >&2
      fi
    fi
    ;;
esac
exit 0
'''

PRERM = '''#!/bin/sh
set -e
case "$1" in
  remove|deconfigure)
    python3 /usr/lib/eduka-icons/select_theme.py --reset-system-defaults --quiet || true
    rm -f /var/lib/eduka-icons/defaults-initialized
    ;;
esac
exit 0
'''

POSTRM = '''#!/bin/sh
set -e
case "$1" in
  remove|purge)
    for theme in Eduka-Icons-Light Eduka-Icons-Dark Eduka-Icons-Bright; do
      rm -f "/usr/share/icons/$theme/icon-theme.cache"
      rmdir "/usr/share/icons/$theme" 2>/dev/null || true
    done
    [ "$1" = purge ] && rm -rf /var/lib/eduka-icons
    ;;
esac
exit 0
'''

PREINST = '''#!/bin/sh
set -e
case "$1" in
  install|upgrade)
    for theme in Eduka-Icons-Light Eduka-Icons-Dark Eduka-Icons-Bright; do
      base="/usr/share/icons/$theme"
      if [ -L "$base" ]; then echo "Refusing theme-directory symlink: $base" >&2; exit 1; fi
      # 0.3.0 and older shipped some HiDPI directories as symlinks.
      if [ -d "$base" ]; then
        find "$base" -maxdepth 1 -type l -name '*@2x' -exec rm -f {} +
      fi
    done
    ;;
esac
exit 0
'''

AUTOSTART = '''[Desktop Entry]
Type=Application
Name=Eduka-Icons theme follower
Comment=Use Eduka-Icons Dark or Bright when the Eduka-Desktop theme changes
Exec=eduka-icons-select --follow-desktop --watch --quiet
Icon=preferences-desktop-theme
OnlyShowIn=LXQt;
NoDisplay=true
X-GNOME-Autostart-enabled=true
'''

COPYRIGHT = '''Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: Eduka-Icons
Source: https://github.com/hugomonizdorego/Eduka-Icons

Files: *
Copyright: 2024-2026 Hugo Moniz do Rego and the Edukasaun OS project
License: GPL-3.0+
 On Debian systems the full text of the GNU General Public License version 3
 can be found in /usr/share/common-licenses/GPL-3.
'''


DEBIAN_CHANGELOG = """eduka-icons ({version}) unstable; urgency=medium

  * Eduka-Icons {version}: Light, Dark and Bright clay icon themes.
    See /usr/share/doc/eduka-icons/CHANGELOG.md for details.

 -- Edukasaun OS <dev@edukasaun.org>  Mon, 12 Oct 2026 00:00:00 +0000
"""

MANPAGE = r""".TH EDUKA-ICONS-SELECT 1 "October 2026" "eduka-icons {version}" "User Commands"
.SH NAME
eduka-icons-select \- choose the Eduka-Icons theme for every desktop
.SH SYNOPSIS
.B eduka-icons-select
[\fB\-\-apply\fR \fILight\fR|\fIDark\fR|\fIBright\fR [\fB\-\-system\-defaults\fR]]
[\fB\-\-follow\-desktop\fR [\fB\-\-watch\fR]] [\fB\-\-reset\-system\-defaults\fR] [\fB\-\-status\fR]
.SH DESCRIPTION
Writes the icon theme into the settings of LXQt and Eduka-Desktop, GTK 2/3/4,
GNOME, Budgie, Cinnamon, MATE, Xfce, KDE Plasma, LXDE, qt5ct/qt6ct and xsettingsd.
.TP
.BR \-\-apply " " \fIVARIANT\fR
Select Eduka-Icons-Light, -Dark or -Bright for the current account.
.TP
.B \-\-system\-defaults
With \-\-apply, as root: set the default for new accounts and the live session (Cubic).
.TP
.B \-\-reset\-system\-defaults
As root: remove the defaults written by \-\-system\-defaults.
.TP
.B \-\-follow\-desktop
Match the Eduka-Desktop theme: dark themes use Dark, Eduka-MultiColor uses Bright.
.TP
.B \-\-status
Show installed variants and the current selection.
.SH SEE ALSO
/usr/share/doc/eduka-icons/USAGE.md
"""


def stage_file(source, target):
    try: os.link(source, target)
    except OSError: shutil.copy2(source, target)
    return target


def write(path, text, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(mode)


def build(output):
    for variant in VARIANTS:
        if not (ROOT / f'build/themes/Eduka-Icons-{variant}/index.theme').is_file():
            raise SystemExit('Run "make build" first.')
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='eduka-package-') as directory:
        package = Path(directory)
        icons = package / 'usr/share/icons'
        icons.mkdir(parents=True)
        for variant in VARIANTS:
            name = f'Eduka-Icons-{variant}'
            shutil.copytree(ROOT / 'build/themes' / name, icons / name, symlinks=True, copy_function=stage_file,
                            ignore=shutil.ignore_patterns('icon-theme.cache', '.eduka-build-owner'))
        write(package / 'usr/lib/eduka-icons/select_theme.py', (ROOT / 'tools/select_theme.py').read_text(), 0o755)
        write(package / 'usr/bin/eduka-icons-select',
              '#!/bin/sh\nexec python3 /usr/lib/eduka-icons/select_theme.py "$@"\n', 0o755)
        write(package / 'etc/xdg/autostart/eduka-icons-follow.desktop', AUTOSTART)
        docs = package / 'usr/share/doc/eduka-icons'
        write(docs / 'copyright', COPYRIGHT)
        for name in ('README.md', 'VERSION'):
            shutil.copyfile(ROOT / name, docs / name)
        shutil.copyfile(ROOT / 'docs/INSTALL.md', docs / 'USAGE.md')
        shutil.copyfile(ROOT / 'CHANGELOG.md', docs / 'CHANGELOG.md')
        with gzip.GzipFile(docs / 'changelog.gz', 'wb', compresslevel=9, mtime=0) as stream:
            stream.write(DEBIAN_CHANGELOG.format(version=VERSION).encode())
        man = package / 'usr/share/man/man1'
        man.mkdir(parents=True)
        with gzip.GzipFile(man / 'eduka-icons-select.1.gz', 'wb', compresslevel=9, mtime=0) as stream:
            stream.write(MANPAGE.format(version=VERSION).encode())
        for path in package.rglob('*'):
            if path.is_dir() and not path.is_symlink():
                path.chmod(0o755)
        control = package / 'DEBIAN'
        control.mkdir()
        # Hard links between the themes share their data; count each file once.
        size = sum({p.stat().st_ino: p.stat().st_size for p in package.rglob('*') if p.is_file() and not p.is_symlink()}.values()) // 1024
        write(control / 'control', CONTROL.format(version=VERSION, size=size))
        write(control / 'conffiles', '/etc/xdg/autostart/eduka-icons-follow.desktop\n')
        for name, text in (('preinst', PREINST), ('postinst', POSTINST), ('prerm', PRERM), ('postrm', POSTRM)):
            write(control / name, text, 0o755)
        sums = []
        for path in sorted(package.rglob('*')):
            relative = path.relative_to(package)
            if path.is_file() and not path.is_symlink() and relative.parts[0] not in ('DEBIAN', 'etc'):
                sums.append(f'{hashlib.md5(path.read_bytes()).hexdigest()}  {relative}')
        write(control / 'md5sums', '\n'.join(sums) + '\n')
        target = output / f'eduka-icons_{VERSION}_all.deb'
        subprocess.run(['dpkg-deb', '--root-owner-group', '-Zxz', '-z9',
                        '--build', str(package), str(target)], check=True)
        print(target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    build(parser.parse_args().output)
