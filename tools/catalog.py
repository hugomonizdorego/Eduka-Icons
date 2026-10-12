"""Decide which artwork every icon name uses.

* Eduka hero/clay artwork (``artwork.CATALOG``) for generic desktop names and
  Eduka's own applications.
* Clay versions of the vendored Papirus application catalog for every
  application that has its own logo, so that, for example, GIMP, Inkscape
  and Krita no longer share one brush icon.
* A clay copy with the app's monogram chip when an application would
  otherwise share artwork with another one (e.g. pcmanfm-qt and Nemo).
"""
import functools
import os
import re
import tarfile
from pathlib import Path

from artwork import CATALOG
from clay import ROOT, source_for
import reference_names

UPSTREAM = sorted((ROOT / 'assets/upstream').glob('papirus-apps-*.tar.xz'))
CACHE = ROOT / 'build/upstream'
# Desktop-wide names: these keep Eduka artwork instead of an app logo.
GENERIC = re.compile(
    r'^(preferences-|system-|utilities-|accessories-|applications-|application-|multimedia-|internet-|'
    r'help-|office-|applets-|x-office-|text-|image-|audio-|video-|font-|package-|web-browser$|mail-|'
    r'im-|chat$|terminal$|calculator$|calendar$|weather$|clock$|drive-|media-|input-|network-|'
    r'computer|camera|printer|scanner|user-|folder|inode-|start-here|distributor-logo|dialog-|'
    r'emblem-|battery|bluetooth|phone$|display$|video-display|security-|edit-|document-|go-|view-|'
    r'window-|list-|process-|zoom-|face-|appointment-|call-|software-|trash|desktop$|settings$)')
PROTECTED = re.compile(r'^(eduka|edukasaun)', re.I)
# Applications seen on Edukasaun OS whose icon names are not in the catalog.
EXTRA = {
    'preferences-desktop-filetype-association': 'preferences-system',
    'blueman-adapters': 'bluetooth', 'blueman-manager': 'bluetooth', 'fcitx5': 'input-keyboard',
    'fcitx5-configtool': 'input-keyboard', 'org.fcitx.fcitx5-config-qt': 'input-keyboard',
    'im-config': 'input-keyboard', 'onboard-settings': 'input-keyboard', 'xfwm4-tweaks': 'preferences-system',
    'imagemagick': 'image-x-generic', 'coulr': 'applications-graphics', 'com.github.huluti.Coulr': 'applications-graphics',
    'abacus': 'accessories-calculator', 'filius': 'network-workgroup', 'fretboard': 'multimedia-audio-player',
    'hex-a-hop': 'applications-games', 'mathhurdler': 'accessories-calculator', 'swift-feet': 'applications-games',
    'trivia-quiz': 'help-browser', '2048': 'applications-games', 'kiwix': 'accessories-dictionary',
    'users': 'system-users', 'lxqt-config': 'preferences-system', 'lxqt-config-appearance': 'preferences-desktop-theme',
    'lxqt-config-input': 'input-mouse', 'lxqt-config-locale': 'preferences-desktop-locale',
    'lxqt-config-monitor': 'computer', 'lxqt-config-notificationd': 'preferences-system-notifications',
    'lxqt-config-powermanagement': 'battery', 'lxqt-config-session': 'preferences-system',
    'lxqt-config-globalkeyshortcuts': 'input-keyboard', 'lxqt-config-file-associations': 'preferences-system',
    'lxqt-config-brightness': 'computer', 'lxqt-admin-user': 'system-users', 'lxqt-admin-time': 'org.gnome.clocks',
    'lxqt-runner': 'system-run', 'lxqt-sudo': 'dialog-password', 'lxqt-panel': 'preferences-system',
    'lxqt-notificationd': 'preferences-system-notifications', 'lxqt-policykit': 'dialog-password',
    'lxqt-leave': 'system-shutdown', 'qterminal': 'utilities-terminal', 'pcmanfm-qt': 'system-file-manager',
}


GUESS = [(r'edu|learn|school|teach|kid|tux|quiz|word', 'applications-education'),
         (r'math|calc|abacus|geo|frac', 'accessories-calculator'), (r'music|audio|sound|song|tune|piano', 'multimedia-audio-player'),
         (r'video|movie|film|player|tv|stream', 'multimedia-video-player'), (r'chat|messag|talk|irc', 'eduka-konekta'),
         (r'mail', 'internet-mail'), (r'browser|web', 'internet-web-browser'), (r'game|play|puzzle|chess|kart', 'applications-games'),
         (r'paint|draw|photo|image|pic|color', 'applications-graphics'), (r'office|doc|write|note|text', 'accessories-text-editor'),
         (r'code|dev|ide|git|program', 'applications-development'), (r'map|earth|globe|star|sky', 'preferences-desktop-locale'),
         (r'term|shell|console', 'utilities-terminal'), (r'file|folder|disk|drive|backup', 'system-file-manager'),
         (r'net|wifi|vpn|remote|share', 'network-workgroup'), (r'set|config|tweak|pref', 'preferences-system'),
         (r'sci|chem|phys|lab', 'applications-science'), (r'key|pass|secret|lock|secur', 'dialog-password')]


def guess(name):
    for pattern, main in GUESS:
        if re.search(pattern, name, re.I):
            return main
    return 'application-x-executable'


WEBAPP = re.compile(r'^(steam_icon_|lutris_|chrome-|brave-|msedge-|vivaldi-|opera-|appimagekit_|wine-|userapp-|'
                    r'com\.valvesoftware\.Steam\.)|-Default$', re.I)
TOKEN_STOP = {'org', 'com', 'io', 'net', 'de', 'kde', 'gnome', 'desktop', 'app', 'github', 'gitlab', 'freedesktop',
              'x', 'bin', 'the', 'and', 'for', 'linux', 'beta', 'dev', 'nightly', 'stable', 'flatpak', 'snap',
              'default', 'mate', 'xfce', 'xfce4', 'gtk', 'qt', 'qt5', 'kf5', 'icon', 'gui', 'launcher', 'client'}


def _tokens(name):
    return {t for t in re.split(r'[^a-z0-9]+', name.lower()) if len(t) > 1 and t not in TOKEN_STOP}


def same_app(name, target):
    """True when an upstream alias most likely names the same application."""
    if WEBAPP.search(name):
        return True
    a, b = _tokens(name), _tokens(target)
    if a & b:
        return True
    flat_a, flat_b = re.sub('[^a-z0-9]', '', name.lower()), re.sub('[^a-z0-9]', '', target.lower())
    return any(t in flat_b for t in a if len(t) > 2) or any(t in flat_a for t in b if len(t) > 2)


def generic(name):
    return bool(GENERIC.match(name)) or bool(PROTECTED.match(name))


@functools.lru_cache(maxsize=1)
def upstream():
    """{name: final real artwork name} of the vendored Papirus apps."""
    if not UPSTREAM:
        return {}
    archive = UPSTREAM[-1]
    folder = CACHE / archive.name.split('.tar')[0]
    if not (folder / 'apps').is_dir():
        folder.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive) as tar:
            tar.extractall(folder, filter='data')
    apps = folder / 'apps'
    names = {}
    for path in apps.iterdir():
        if path.suffix != '.svg':
            continue
        real = Path(os.path.realpath(path))
        if real.is_file() and real.parent == apps.resolve():
            names[path.stem] = real.stem
    return names


def upstream_dir():
    archive = UPSTREAM[-1]
    return CACHE / archive.name.split('.tar')[0] / 'apps'


@functools.lru_cache(maxsize=1)
def plan():
    """Return (core, apps).

    core: {name: (kind, color, context, aliases)} for the Eduka themes.
    apps: {'art': {art: svg path}, 'links': {name: art},
           'badges': {name: ('core', source asset) or ('upstream', art)}}
    """
    bulk = upstream()
    reserved = {}            # names drawn by Eduka -> catalog main name
    for main, (_, _, _, names) in CATALOG.items():
        reserved[main] = main
        for name in names.split():
            if generic(name):
                reserved[name] = main
    core, badges = {}, {}
    for main, (kind, color, context, names) in CATALOG.items():
        keep = []
        for name in names.split():
            if name.endswith('-symbolic'):
                continue
            target = bulk.get(name)
            if PROTECTED.match(name) or (generic(name) and (target is None or target in reserved)):
                keep.append(name)          # plain alias of Eduka artwork
                continue
            reserved.pop(name, None)
            if target is not None and target not in reserved and target == name:
                pass                       # the app has its own logo upstream
            elif target is not None and target not in reserved and not generic(target):
                pass                       # alias of another app's own logo upstream
            else:
                badges[name] = ('core', source_for(main, kind))
        core[main] = (kind, color, context, ' '.join(keep))
    # Upstream names that only alias an Eduka-drawn icon: generic ones join the
    # Eduka entry, applications get a monogram copy of it.
    for name, target in bulk.items():
        if name in reserved or name in badges:
            continue
        if target in reserved:
            main = reserved[target]
            kind, color, context, names = core[main]
            if generic(name):
                core[main] = (kind, color, context, f'{names} {name}'.strip())
                reserved[name] = main
            else:
                badges[name] = ('core', source_for(main, CATALOG[main][0]))
        elif name != target and not generic(name) and (generic(target) or not same_app(name, target)):
            badges[name] = ('upstream', target)   # another app's (or a generic) picture
    for name, base in EXTRA.items():
        if name in reserved and name not in badges:
            continue
        if name in bulk and bulk[name] not in reserved and bulk[name] == name:
            continue
        main = reserved.get(base, base)
        badges[name] = ('core', source_for(main, CATALOG[main][0]))
    covered = set(reserved) | set(badges) | {n for n in bulk if n not in reserved}
    for group in ('EDUKA_DESKTOP', 'LXQT', 'KDE', 'GNOME', 'POPULAR', 'DESKTOP_APPS'):
        for name in getattr(reference_names, group):
            if name not in covered and not generic(name):
                main = guess(name)
                badges[name] = ('core', source_for(main, CATALOG[main][0]))
                covered.add(name)
    art, links = {}, {}
    folder = upstream_dir() if bulk else None
    for name, target in bulk.items():
        if name in reserved or name in badges or target in reserved:
            continue
        art.setdefault(target, folder / (target + '.svg'))
        if name != target:
            links[name] = target
    for name, (source, base) in badges.items():
        if source == 'upstream':
            art.setdefault(base, folder / (base + '.svg'))
    return core, {'art': art, 'links': links, 'badges': badges}
