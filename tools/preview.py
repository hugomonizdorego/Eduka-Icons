#!/usr/bin/env python3
"""Render screenshots of the built themes into build/screenshots/.

* overview-<variant>.png  - clay icons and panel glyphs on a matching background
* desktop-<variant>.png   - an Eduka-Desktop style session (menu, panel, tray)
* symbolic.png            - every symbolic glyph, light and dark
* variants.png            - Light, Dark and Bright side by side
"""
import argparse
import sys
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from render import render

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from settings import BUILD  # noqa: E402
VERSION = (ROOT / 'VERSION').read_text().strip()
OUT = BUILD / 'screenshots'
# Background, surface, text colour and accent per variant, after the Eduka-Desktop themes.
LOOK = {
    'Light': {'bg': ('#e9efe9', '#cfe2d8'), 'surface': '#fbfaf6', 'text': '#2f3a33', 'muted': '#6b776e',
              'accent': '#00a879', 'desktop': 'Eduka-Default-Theme'},
    'Dark': {'bg': ('#20262a', '#2f3b38'), 'surface': '#2c2c2c', 'text': '#f1ece2', 'muted': '#a9b2ab',
             'accent': '#26a69a', 'desktop': 'Edukasaun-Dark'},
    'Bright': {'bg': ('#fde9c8', '#c9ecf0'), 'surface': '#ffffff', 'text': '#2c3a35', 'muted': '#5f6f69',
               'accent': '#5b6ee1', 'desktop': 'Eduka-MultiColor'},
    'Comfort': {'bg': ('#f7efe0', '#ecdcc0'), 'surface': '#fffaf1', 'text': '#1d1a14', 'muted': '#4a4236',
                'accent': '#0f5c53', 'desktop': 'eye comfort and low vision'},
}
APPS = [
 ('gimp', 'GIMP'), ('inkscape', 'Inkscape'), ('krita', 'Krita'), ('blender', 'Blender'), ('org.kde.kolourpaint', 'KolourPaint'),
 ('tuxpaint', 'Tux Paint'), ('google-chrome', 'Chrome'), ('brave-browser', 'Brave'), ('firefox', 'Firefox'),
 ('google-earth-pro', 'Google Earth'), ('whatsapp', 'WhatsApp'), ('telegram', 'Telegram'), ('discord', 'Discord'),
 ('signal-desktop', 'Signal'), ('zoom', 'Zoom'), ('thunderbird', 'Thunderbird'), ('vlc', 'VLC'), ('audacity', 'Audacity'),
 ('obs', 'OBS'), ('kdenlive', 'Kdenlive'), ('spotify', 'Spotify'), ('steam', 'Steam'), ('supertuxkart', 'SuperTuxKart'),
 ('minetest', 'Minetest'), ('gcompris', 'GCompris'), ('kalzium', 'Kalzium'), ('marble', 'Marble'), ('kgeography', 'KGeography'),
 ('tuxmath', 'Tux Math'), ('kbruch', 'KBruch'), ('khangman', 'KHangMan'), ('ktuberling', 'KTuberling'), ('geogebra', 'GeoGebra'),
 ('stellarium', 'Stellarium'), ('anki', 'Anki'), ('scratch-desktop', 'Scratch'), ('libreoffice-base', 'Base'),
 ('onlyoffice-desktopeditors', 'ONLYOFFICE'), ('calibre', 'Calibre'), ('code', 'VS Code'), ('thonny', 'Thonny'),
 ('org.kde.dolphin', 'Dolphin'), ('org.gnome.Nautilus', 'Files'), ('pcmanfm-qt', 'PCManFM-Qt'), ('qterminal', 'QTerminal'),
 ('featherpad', 'FeatherPad'), ('lximage-qt', 'LXImage'), ('screengrab', 'ScreenGrab'), ('obconf-qt', 'Openbox'),
 ('synaptic', 'Synaptic'), ('gparted', 'GParted'), ('keepassxc', 'KeePassXC'), ('virtualbox', 'VirtualBox'),
 ('blueman-manager', 'Bluetooth'), ('fcitx5', 'Fcitx 5'),
]
GRID = [
 ('edukasaun', 'Edukasaun'), ('system-file-manager', 'Files'), ('internet-web-browser', 'Browser'),
 ('internet-mail', 'Mail'), ('eduka-konekta', 'Konekta'), ('utilities-terminal', 'Terminal'),
 ('preferences-system', 'Settings'), ('system-software-install', 'Software'), ('eduka-update-system', 'Update'),
 ('eduka-block', 'Eduka-Block'), ('eduka-lafa', 'Lafa'), ('edukasaun-welcome', 'Welcome'),
 ('libreoffice-writer', 'Writer'), ('libreoffice-calc', 'Calc'), ('libreoffice-impress', 'Impress'),
 ('x-office-calendar', 'Calendar'), ('accessories-calculator', 'Calculator'), ('accessories-notes', 'Notes'),
 ('multimedia-audio-player', 'Music'), ('multimedia-video-player', 'Videos'), ('cheese', 'Camera'),
 ('graphics-editor', 'Graphics'), ('multimedia-photo-manager', 'Photos'), ('applications-games', 'Games'),
 ('applications-science', 'Science'), ('preferences-desktop-locale', 'Language'), ('utilities-system-monitor', 'Monitor'),
 ('help-browser', 'Help'), ('dialog-password', 'Passwords'), ('user-trash', 'Trash'),
 ('folder', 'Folder'), ('user-home', 'Home'), ('folder-documents', 'Documents'), ('folder-download', 'Downloads'),
 ('folder-music', 'Music'), ('folder-pictures', 'Pictures'), ('folder-videos', 'Videos'), ('folder-desktop', 'Desktop'),
 ('application-pdf', 'PDF'), ('application-zip', 'Archive'), ('text-x-script', 'Script'), ('application-x-deb', 'Package'),
]
TRAY = ('network-wireless-signal-excellent', 'bluetooth-active', 'audio-volume-high', 'battery-full-charging',
        'notification-active', 'system-shutdown')
GLYPHS = ('go-previous', 'go-next', 'view-refresh', 'system-search', 'list-add', 'edit-copy', 'edit-paste',
          'document-save', 'view-app-grid', 'open-menu', 'window-close', 'emblem-ok', 'media-playback-start',
          'display-brightness', 'night-light', 'airplane-mode', 'microphone-sensitivity-high', 'starred')


def font(size, bold=False):
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    try: return ImageFont.truetype(name, size)
    except OSError:
        try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + name, size)
        except OSError: return ImageFont.load_default()


def gradient(size, top, bottom):
    width, height = size
    base = Image.new('RGB', (1, 2))
    base.putpixel((0, 0), Image.new('RGB', (1, 1), top).getpixel((0, 0)))
    base.putpixel((0, 1), Image.new('RGB', (1, 1), bottom).getpixel((0, 0)))
    return base.resize((width, height), Image.Resampling.BICUBIC)


def theme_dir(variant):
    return BUILD / f'themes/Eduka-Icons-{variant}'


def _svg(path, size):
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / 'icon.png'
        render(path, size, target)
        with Image.open(target) as image:
            return image.convert('RGBA')


def icon(variant, name, size):
    """The file a desktop would show for this name at this size (clay PNG or flat SVG)."""
    theme = theme_dir(variant)
    apps = BUILD / 'themes' / ('Eduka-Icons-Apps-Comfort' if variant == 'Comfort' else 'Eduka-Icons-Apps')
    if size <= 24:
        for path in theme.glob(f'flat/small/*/{name}.svg'):
            return _svg(path, size)
    candidates = [*sorted(theme.glob('256x256/*')), *sorted(theme.glob('512x512/*')), *sorted(apps.glob('128x128/*'))]
    for directory in candidates:
        path = directory / (name + '.png')
        if path.exists():
            with Image.open(path) as image:
                return image.convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)
    for pattern in ('scalable/*', 'flat/24/*', 'flat/22/*', 'flat/16/*', 'symbolic/*'):
        for path in theme.glob(f'{pattern}/{name}.svg'):
            return _svg(path, size)
    raise FileNotFoundError(name)


def apps_sheet(variant):
    look = LOOK[variant]
    cols = 11
    rows = (len(APPS) + cols - 1) // cols
    canvas = gradient((1600, 210 + rows * 150), *look['bg']).convert('RGBA')
    draw = ImageDraw.Draw(canvas)
    draw.text((56, 40), f'Every application has its own clay icon · Eduka-Icons-{variant}', font=font(34, True), fill=look['text'])
    draw.text((58, 92), 'Graphics, internet, chat, media, games, education, office, development, LXQt, KDE and GNOME',
              font=font(19), fill=look['muted'])
    for i, (name, title) in enumerate(APPS):
        x, y = 50 + (i % cols) * 138, 150 + (i // cols) * 150
        canvas.alpha_composite(icon(variant, name, 96), (x + 16, y))
        width = draw.textlength(title, font=font(15))
        draw.text((x + 64 - width / 2, y + 104), title, font=font(15), fill=look['text'])
    return canvas


TRAY_NAMES = ('network-wireless-signal-excellent', 'network-wireless-signal-ok', 'network-wired', 'bluetooth',
              'audio-volume-high', 'audio-volume-muted', 'microphone-sensitivity-high', 'battery-full-charging',
              'battery-low', 'display-brightness', 'night-light', 'notification-active', 'airplane-mode',
              'system-lock-screen', 'system-reboot', 'system-shutdown', 'nm-signal-75', 'nm-device-wired',
              'blueman-active', 'package-install')
TOOLBAR_NAMES = ('go-previous', 'go-next', 'go-up', 'go-home', 'view-refresh', 'document-new', 'document-open',
                 'document-save', 'document-print', 'edit-undo', 'edit-redo', 'edit-cut', 'edit-copy', 'edit-paste',
                 'edit-delete', 'edit-find', 'zoom-in', 'zoom-out', 'view-fullscreen', 'list-add', 'list-remove',
                 'media-playback-start', 'media-playback-pause', 'starred', 'open-menu', 'window-close')


def _row(canvas, variant, names, size, x, y, step):
    for index, name in enumerate(names):
        try:
            canvas.alpha_composite(icon(variant, name, size), (x + index * step, y))
        except (FileNotFoundError, StopIteration):
            pass


def panel_sheet(temporary):
    """Normal flat tray, panel and toolbar icons at their real pixel sizes."""
    canvas = Image.new('RGBA', (1600, 900), '#f4f1ea')
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 450, 1600, 900), fill='#262b27')
    for half, (variant, color, bar) in enumerate((('Light', '#2f3a33', '#fbfaf6'), ('Dark', '#f1ece2', '#33383a'))):
        top = half * 450
        draw.text((40, top + 22), f'System tray, panel and toolbar icons · Eduka-Icons-{variant}', font=font(24, True), fill=color)
        draw.text((40, top + 58), 'Flat, one colour, pixel-reviewed at 16, 22 and 24 px (shown at real size and 2x). Clay artwork starts at 32 px.',
                  font=font(16), fill=color)
        for row, size in enumerate((16, 22, 24)):
            y = top + 96 + row * 44
            draw.rounded_rectangle((36, y - 6, 1564, y + size + 6), 10, fill=bar)
            draw.text((48, y + size / 2 - 8), f'{size}', font=font(13), fill=color)
            _row(canvas, variant, TRAY_NAMES + TOOLBAR_NAMES[:20], size, 84, y, 36)
        y = top + 246
        draw.rounded_rectangle((36, y - 8, 1564, y + 56), 14, fill=bar)
        _row(canvas, variant, TRAY_NAMES + TOOLBAR_NAMES[:5], 48, 52, y, 60)
        y = top + 330
        draw.text((40, y), 'The same names from 32 px up use clay artwork (dialogs, launchers, settings):', font=font(16), fill=color)
        _row(canvas, variant, ('bluetooth', 'battery', 'network-wireless', 'system-shutdown', 'system-reboot',
                               'system-lock-screen', 'system-log-out', 'system-suspend', 'audio-input-microphone',
                               'preferences-system-notifications', 'dialog-warning', 'dialog-error',
                               'dialog-information', 'help-browser'), 64, 44, y + 30, 84)
    return canvas


def folders_sheet():
    """Folder colours selectable with eduka-icons-select --folder-colour."""
    import settings
    colours = settings.load()['folders']['colours']
    kinds = ('folder', 'folder-documents', 'folder-download', 'folder-music', 'folder-pictures', 'folder-videos')
    look = LOOK['Light']
    canvas = gradient((1600, 150 + len(colours) * 118), *look['bg']).convert('RGBA')
    draw = ImageDraw.Draw(canvas)
    draw.text((56, 36), 'Folder colours · eduka-icons-select --folder-colour <name>', font=font(34, True), fill=look['text'])
    default = settings.load()['folders']['default']
    for row, colour in enumerate(colours):
        y = 120 + row * 118
        draw.text((60, y + 38), colour + (' (default)' if colour == default else ''), font=font(22, True), fill=look['text'])
        for column, kind in enumerate(kinds):
            name = kind if colour == default else kind.replace('folder', f'folder-{colour}', 1)
            canvas.alpha_composite(icon('Light', name, 104), (300 + column * 150, y))
        for column, size in enumerate((48, 32, 24, 16)):
            name = 'folder' if colour == default else f'folder-{colour}'
            canvas.alpha_composite(icon('Light', name, size), (1240 + column * 70, y + 52 - size // 2))
    return canvas


def artwork_sheet(variant='Light'):
    """Every Eduka-drawn clay artwork of a variant."""
    look = LOOK[variant]
    assets = sorted(p for p in (theme_dir(variant) / 'assets/256').glob('*.png') if '@' not in p.stem)
    cols = 14
    rows = (len(assets) + cols - 1) // cols
    canvas = gradient((1600, 150 + rows * 112), *look['bg']).convert('RGBA')
    draw = ImageDraw.Draw(canvas)
    draw.text((56, 36), f'{len(assets)} Eduka clay artworks · Eduka-Icons-{variant}', font=font(34, True), fill=look['text'])
    for index, path in enumerate(assets):
        with Image.open(path) as image:
            image = image.convert('RGBA').resize((96, 96), Image.Resampling.LANCZOS)
        canvas.alpha_composite(image, (50 + (index % cols) * 108, 120 + (index // cols) * 112))
    return canvas


def types_sheet(variant='Light'):
    """File types and devices from the shared catalog."""
    look = LOOK[variant]
    names = ('text-x-generic', 'text-x-python', 'text-x-csrc', 'text-html', 'text-css', 'application-json',
             'application-x-shellscript', 'text-markdown', 'application-pdf', 'application-epub+zip',
             'application-msword', 'application-vnd.ms-excel', 'application-vnd.ms-powerpoint',
             'application-vnd.oasis.opendocument.text', 'application-zip', 'application-x-7z-compressed',
             'application-x-deb', 'application-x-rpm', 'application-x-iso', 'application-x-executable',
             'image-x-generic', 'image-svg+xml', 'image-x-xcf', 'audio-x-generic', 'audio-midi', 'video-x-generic',
             'font-x-generic', 'application-x-sqlite3', 'application-x-java', 'text-x-sql', 'application-x-blender',
             'application-pgp-keys', 'computer', 'computer-laptop', 'drive-harddisk', 'drive-removable-media',
             'media-optical', 'printer', 'scanner', 'input-keyboard', 'input-mouse', 'input-gaming', 'input-tablet',
             'audio-headphones', 'audio-input-microphone', 'camera-photo', 'camera-web', 'phone', 'tablet',
             'multimedia-player', 'network-wireless', 'bluetooth', 'battery', 'video-display', 'tv', 'smartwatch')
    cols = 14
    canvas = gradient((1600, 170 + ((len(names) + cols - 1) // cols) * 116), *look['bg']).convert('RGBA')
    draw = ImageDraw.Draw(canvas)
    draw.text((56, 36), f'File types and devices · Eduka-Icons-{variant}', font=font(34, True), fill=look['text'])
    shown = 0
    for name in names:
        try: image = icon(variant, name, 88)
        except (FileNotFoundError, StopIteration): continue
        canvas.alpha_composite(image, (52 + (shown % cols) * 108, 124 + (shown // cols) * 116))
        shown += 1
    return canvas


def glyph(variant, name, size, temporary):
    theme = theme_dir(variant)
    source = next(theme.glob(f'symbolic/*/{name}-symbolic.svg'))
    target = Path(temporary) / f'{variant}-{name}-{size}.png'
    render(source, size, target)
    with Image.open(target) as image:
        return image.convert('RGBA')


def shadow_card(canvas, box, radius, fill, blur=18, opacity=60):
    x0, y0, x1, y1 = box
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle((x0, y0 + 8, x1, y1 + 8), radius, fill=(0, 0, 0, opacity))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(canvas).rounded_rectangle(box, radius, fill=fill)


def overview(variant, temporary):
    look = LOOK[variant]
    canvas = gradient((1600, 1000), *look['bg']).convert('RGBA')
    draw = ImageDraw.Draw(canvas)
    draw.text((64, 48), f'Eduka-Icons-{variant}', font=font(46, True), fill=look['text'])
    draw.text((66, 110), f'{VERSION} · official clay icons of Edukasaun OS · pairs with {look["desktop"]}',
              font=font(20), fill=look['muted'])
    cols = 14
    for i, (name, title) in enumerate(GRID):
        x, y = 54 + (i % cols) * 107, 170 + (i // cols) * 200
        canvas.alpha_composite(icon(variant, name, 88), (x + 8, y))
        width = draw.textlength(title, font=font(15))
        draw.text((x + 52 - width / 2, y + 100), title, font=font(15), fill=look['text'])
    shadow_card(canvas, (54, 790, 1546, 940), 26, look['surface'], opacity=35)
    draw = ImageDraw.Draw(canvas)
    draw.text((86, 810), 'Symbolic panel and toolbar icons (GTK, Qt and KDE recolour-ready)', font=font(18),
              fill=look['muted'])
    for i, name in enumerate(TRAY + GLYPHS):
        canvas.alpha_composite(glyph(variant, name, 32, temporary), (90 + i * 60, 866))
    return canvas


def desktop(variant, temporary):
    look = LOOK[variant]
    width, height = 1600, 1000
    canvas = gradient((width, height), *look['bg']).convert('RGBA')
    # Soft wallpaper shapes.
    blobs = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(blobs)
    bd.ellipse((900, -200, 1800, 600), fill=look['accent'] + '40')
    bd.ellipse((-300, 500, 700, 1300), fill=look['accent'] + '2a')
    canvas.alpha_composite(blobs.filter(ImageFilter.GaussianBlur(60)))
    draw = ImageDraw.Draw(canvas)
    # Desktop icons.
    for i, (name, title) in enumerate((('user-home', 'Home'), ('folder-documents', 'Documents'),
                                       ('folder-download', 'Downloads'), ('user-trash', 'Trash'))):
        x, y = 40, 40 + i * 130
        canvas.alpha_composite(icon(variant, name, 72), (x + 14, y))
        tw = draw.textlength(title, font=font(15))
        draw.text((x + 50 - tw / 2, y + 80), title, font=font(15), fill=look['text'])
    # Eduka-Menu.
    menu = (440, 150, 1160, 860)
    shadow_card(canvas, menu, 28, look['surface'] + 'f2')
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((474, 184, 1126, 232), 24, fill=look['bg'][0], outline=look['accent'], width=2)
    canvas.alpha_composite(glyph(variant, 'system-search', 22, temporary), (494, 197))
    draw.text((528, 196), 'Search applications', font=font(18), fill=look['muted'])
    draw.text((476, 258), 'Pinned', font=font(18, True), fill=look['text'])
    for i, (name, title) in enumerate(GRID[:24]):
        x, y = 470 + (i % 6) * 108, 296 + (i // 6) * 120
        canvas.alpha_composite(icon(variant, name, 64), (x + 22, y))
        tw = draw.textlength(title, font=font(14))
        draw.text((x + 54 - tw / 2, y + 72), title, font=font(14), fill=look['text'])
    draw.line((474, 784, 1126, 784), fill=look['muted'] + '55', width=1)
    canvas.alpha_composite(icon(variant, 'system-users', 40), (478, 798))
    draw.text((528, 808), 'Student', font=font(18), fill=look['text'])
    for i, name in enumerate(('system-lock-screen', 'system-reboot', 'system-shutdown')):
        canvas.alpha_composite(glyph(variant, name, 24, temporary), (1010 + i * 40, 808))
    # Eduka-Panel.
    panel = (300, 900, 1300, 972)
    shadow_card(canvas, panel, 24, look['surface'] + 'e8', blur=14)
    draw = ImageDraw.Draw(canvas)
    canvas.alpha_composite(icon(variant, 'edukasaun', 52), (316, 910))
    for i, name in enumerate(('system-file-manager', 'internet-web-browser', 'utilities-terminal',
                              'libreoffice-writer', 'multimedia-audio-player', 'preferences-system')):
        canvas.alpha_composite(icon(variant, name, 48), (392 + i * 64, 912))
        if i < 3:
            draw.rounded_rectangle((408 + i * 64, 963, 424 + i * 64, 966), 2, fill=look['accent'])
    for i, name in enumerate(TRAY):
        canvas.alpha_composite(icon(variant, name, 22), (998 + i * 32, 925))
    draw.text((1196, 924), '10:24', font=font(18, True), fill=look['text'])
    caption = f'Eduka-Desktop · {look["desktop"]} · Eduka-Icons-{variant}'
    draw.text((width - 40 - draw.textlength(caption, font=font(16)), 24), caption, font=font(16), fill=look['muted'])
    return canvas


def symbolic_sheet(temporary):
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from symbolic import SYMBOLS
    names = sorted({name for name in SYMBOLS})
    cols, cell = 24, 60
    rows = (len(names) + cols - 1) // cols
    canvas = Image.new('RGBA', (cols * cell + 40, rows * cell * 2 + 140), '#f4f1ea')
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, rows * cell + 70, canvas.width, canvas.height), fill='#262b27')
    for half, (variant, color) in enumerate((('Light', '#2f3a33'), ('Dark', '#f1ece2'))):
        top = 20 + half * (rows * cell + 70)
        draw.text((20, top), f'{len(names)} symbolic icons · {variant}', font=font(20, True), fill=color)
        for i, name in enumerate(names):
            x, y = 20 + (i % cols) * cell, top + 40 + (i // cols) * cell
            canvas.alpha_composite(glyph(variant, name, 32, temporary), (x + 14, y + 10))
    return canvas


def variants_strip():
    canvas = Image.new('RGBA', (2000, 420), '#ffffff')
    names = ('folder', 'user-home', 'edukasaun', 'internet-web-browser', 'preferences-system', 'multimedia-audio-player')
    for column, variant in enumerate(('Light', 'Dark', 'Bright', 'Comfort')):
        look = LOOK[variant]
        part = gradient((500, 420), *look['bg']).convert('RGBA')
        draw = ImageDraw.Draw(part)
        draw.text((32, 26), f'Eduka-Icons-{variant}', font=font(28, True), fill=look['text'])
        draw.text((34, 66), f'for {look["desktop"]}', font=font(16), fill=look['muted'])
        for i, name in enumerate(names):
            part.alpha_composite(icon(variant, name, 120), (40 + (i % 3) * 145, 110 + (i // 3) * 145))
        canvas.alpha_composite(part, (column * 500, 0))
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--output', type=Path, default=OUT)
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        for variant in LOOK:
            overview(variant, temporary).convert('RGB').save(output / f'overview-{variant.lower()}.png', optimize=True)
            desktop(variant, temporary).convert('RGB').save(output / f'desktop-{variant.lower()}.png', optimize=True)
            apps_sheet(variant).convert('RGB').save(output / f'apps-{variant.lower()}.png', optimize=True)
        symbolic_sheet(temporary).convert('RGB').save(output / 'symbolic.png', optimize=True)
        panel_sheet(temporary).convert('RGB').save(output / 'panel.png', optimize=True)
    folders_sheet().convert('RGB').save(output / 'folders.png', optimize=True)
    artwork_sheet().convert('RGB').save(output / 'artwork.png', optimize=True)
    types_sheet().convert('RGB').save(output / 'types.png', optimize=True)
    variants_strip().convert('RGB').save(output / 'variants.png', optimize=True)
    for path in sorted(output.glob('*.png')):
        print(path)


if __name__ == '__main__':
    main()
