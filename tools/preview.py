#!/usr/bin/env python3
"""Render screenshots of the built themes into build/screenshots/.

* overview-<variant>.png  - clay icons and panel glyphs on a matching background
* desktop-<variant>.png   - an Eduka-Desktop style session (menu, panel, tray)
* symbolic.png            - every symbolic glyph, light and dark
* variants.png            - Light, Dark and Bright side by side
"""
import argparse
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from render import render

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / 'VERSION').read_text().strip()
OUT = ROOT / 'build/screenshots'
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
    return ROOT / f'build/themes/Eduka-Icons-{variant}'


def icon(variant, name, size):
    apps = ROOT / 'build/themes' / ('Eduka-Icons-Apps-Comfort' if variant == 'Comfort' else 'Eduka-Icons-Apps')
    candidates = [*sorted(theme_dir(variant).glob('256x256/*')), *sorted(theme_dir(variant).glob('512x512/*')),
                  *apps.glob('128x128/apps')]
    for directory in candidates:
        path = directory / (name + '.png')
        if path.exists():
            with Image.open(path) as image:
                return image.convert('RGBA').resize((size, size), Image.Resampling.LANCZOS)
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


def panel_sheet(temporary):
    """Colourful clay panel icons and two-tone symbolic icons."""
    names = ('network-wireless-signal-excellent', 'bluetooth-active', 'audio-volume-high', 'battery-full-charging',
             'display-brightness', 'notification-active', 'system-shutdown', 'system-reboot', 'system-lock-screen',
             'edit-copy', 'edit-paste', 'edit-undo', 'document-save', 'document-open', 'list-add', 'go-next',
             'view-refresh', 'zoom-in', 'media-playback-start', 'starred', 'dialog-warning', 'night-light')
    canvas = Image.new('RGBA', (1600, 760), '#f4f1ea')
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 380, 1600, 760), fill='#262b27')
    for half, (variant, color) in enumerate((('Light', '#2f3a33'), ('Dark', '#f1ece2'))):
        top = half * 380
        draw.text((40, top + 24), f'Clay panel icons · {variant}', font=font(22, True), fill=color)
        for i, name in enumerate(names):
            canvas.alpha_composite(icon(variant, name, 52), (40 + i * 70, top + 70))
        draw.text((40, top + 160), 'Symbolic icons (two-tone; GTK and KDE recolour them automatically)', font=font(18), fill=color)
        for i, name in enumerate(names):
            canvas.alpha_composite(glyph(variant, name, 32, temporary), (50 + i * 70, top + 210))
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
        canvas.alpha_composite(icon(variant, name, 26), (996 + i * 32, 923))
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
    variants_strip().convert('RGB').save(output / 'variants.png', optimize=True)
    for path in sorted(output.glob('*.png')):
        print(path)


if __name__ == '__main__':
    main()
