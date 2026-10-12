#!/usr/bin/env python3
"""Build the optional binary package separately from the GitHub source."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.3.0'

def stage_file(source, target):
    try: os.link(source, target)
    except OSError: shutil.copy2(source, target)
    return target

def build(output):
    for variant in ('Light', 'Dark'):
        if not (ROOT / f'build/themes/Eduka-Icons-{variant}/index.theme').is_file():
            raise SystemExit('Run make build first.')
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='eduka-package-') as directory:
        package = Path(directory)
        icons = package / 'usr/share/icons'
        icons.mkdir(parents=True)
        for variant in ('Light', 'Dark'):
            name = f'Eduka-Icons-{variant}'
            shutil.copytree(ROOT / 'build/themes' / name, icons / name, symlinks=True,
                            copy_function=stage_file, ignore=shutil.ignore_patterns('icon-theme.cache'))
        lib = package / 'usr/lib/eduka-icons'
        lib.mkdir(parents=True)
        shutil.copyfile(ROOT / 'tools/install.py', lib / 'select.py')
        binary = package / 'usr/bin'
        binary.mkdir(parents=True)
        selector = binary / 'eduka-icons-select'
        selector.write_text('#!/bin/sh\nexec python3 /usr/lib/eduka-icons/select.py --select-only "$@"\n')
        selector.chmod(0o755)
        docs = package / 'usr/share/doc/eduka-icons'
        docs.mkdir(parents=True)
        for name in ('LICENSE', 'README.md', 'CHANGELOG.md', 'VERSION'):
            shutil.copyfile(ROOT / name, docs / name)
        control = package / 'DEBIAN'
        control.mkdir()
        size = sum(p.stat().st_size for p in package.rglob('*') if p.is_file() and not p.is_symlink()) // 1024
        (control / 'control').write_text(f'''Package: eduka-icons
Version: {VERSION}
Section: x11
Priority: optional
Architecture: all
Maintainer: Edukasaun OS <eduka-icons@localhost>
Depends: python3, hicolor-icon-theme
Recommends: gtk-update-icon-cache
Installed-Size: {size}
Description: Eduka original clay icons for Edukasaun OS
 Standalone Light and Dark icon themes with original clay artwork,
 native panel glyphs, HiDPI exports, and standard hicolor fallback.
''')
        preinst = control / 'preinst'
        preinst.write_text('''#!/bin/sh
set -e
case "$1" in
  install|upgrade)
    for theme in Eduka-Icons-Light Eduka-Icons-Dark; do
      base="/usr/share/icons/$theme"
      if [ -L "$base" ]; then echo "Refusing theme-directory symlink: $base" >&2; exit 1; fi
      for size in 16 18 22 24 32 40 48 64 96 128 192 256 512; do
        dir="$base/${size}x${size}@2x"
        if [ -L "$dir" ]; then unlink "$dir"; mkdir "$dir"; fi
      done
    done
    ;;
esac
''')
        preinst.chmod(0o755)
        for name in ('postinst', 'postrm'):
            script = control / name
            script.write_text('''#!/bin/sh
set -e
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  for theme in Eduka-Icons-Light Eduka-Icons-Dark; do
    if [ -d "/usr/share/icons/$theme" ]; then gtk-update-icon-cache -f -t "/usr/share/icons/$theme" || true; fi
  done
fi
''')
            script.chmod(0o755)
        target = output / f'eduka-icons_{VERSION}_all.deb'
        subprocess.run(['dpkg-deb', '--root-owner-group', '--threads-max=2', '-Zxz', '-z6',
                        '--build', str(package), str(target)], check=True)
        print(target)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    build(parser.parse_args().output)
