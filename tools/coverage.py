#!/usr/bin/env python3
"""Report which icon names use Eduka artwork, a fallback theme, or nothing."""
import json
from pathlib import Path
from build_theme import ROOT
from reference_names import EDUKA_DESKTOP, FREEDESKTOP, DESKTOP_APPS

FALLBACK_ROOTS = [Path('/usr/share/icons'), Path('/usr/local/share/icons')]

def names_in(theme):
    names = set()
    for path in theme.rglob('*'):
        if path.suffix in ('.png', '.svg') and 'assets' not in path.relative_to(theme).parts:
            names.add(path.stem)
    return names

def coverage(variant='Light'):
    theme = ROOT / f'build/themes/Eduka-Icons-{variant}'
    own = names_in(theme)
    fallback = set()
    for root in FALLBACK_ROOTS:
        for name in ('Papirus', 'Papirus-Light', 'breeze', 'Adwaita', 'hicolor'):
            if (root / name).is_dir():
                fallback |= names_in(root / name)
    report = {'variant': variant, 'own_names': len(own), 'fallback_themes_found': bool(fallback), 'lists': {}}
    for label, names in (('eduka-desktop', EDUKA_DESKTOP), ('freedesktop', FREEDESKTOP), ('desktop-apps', DESKTOP_APPS)):
        names = sorted(set(names))
        eduka = [n for n in names if n in own or n + '-symbolic' in own]
        backup = [n for n in names if n not in eduka and n in fallback]
        missing = [n for n in names if n not in eduka and n not in backup]
        report['lists'][label] = {'total': len(names), 'eduka': len(eduka), 'fallback': backup, 'missing': missing}
    return report

if __name__ == '__main__':
    report = coverage()
    (ROOT / 'build/coverage-names.json').write_text(json.dumps(report, indent=2) + '\n')
    for label, data in report['lists'].items():
        print(f"{label}: {data['eduka']}/{data['total']} Eduka artwork, "
              f"{len(data['fallback'])} fallback, {len(data['missing'])} missing")
        if data['missing'] or data['fallback']:
            print('  not yet Eduka:', ' '.join(data['missing'] + data['fallback']))
    if report['lists']['eduka-desktop']['eduka'] != report['lists']['eduka-desktop']['total']:
        raise SystemExit('Some Eduka-Desktop icon names have no Eduka artwork.')
