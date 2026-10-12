#!/usr/bin/env python3
"""Preview actual theme files; output stays outside the source allowlist."""
from pathlib import Path
import tempfile
from PIL import Image, ImageDraw, ImageFont
from render import render

ROOT = Path(__file__).resolve().parents[1]
GRID = [
 ('folder', 'places', 'Folder'), ('user-home', 'places', 'Home'),
 ('edukasaun', 'apps', 'Edukasaun'), ('cheese', 'apps', 'Camera'),
 ('internet-web-browser', 'apps', 'Browser'),
 ('system-file-manager', 'apps', 'Files'), ('folder-documents', 'places', 'Documents'),
 ('folder-download', 'places', 'Downloads'), ('multimedia-audio-player', 'apps', 'Music'),
 ('multimedia-video-player', 'apps', 'Video'),
 ('utilities-terminal', 'apps', 'Terminal'), ('preferences-system', 'apps', 'Settings'),
 ('internet-mail', 'apps', 'Mail'), ('eduka-konekta', 'apps', 'Konekta'),
 ('system-software-install', 'apps', 'Software'),
 ('libreoffice-writer', 'apps', 'Writer'), ('x-office-calendar', 'apps', 'Calendar'),
 ('eduka-block', 'apps', 'Block'), ('eduka-lafa', 'apps', 'Lafa'), ('user-trash', 'places', 'Trash')]

def font(size):
    try: return ImageFont.truetype('DejaVuSans.ttf', size)
    except OSError: return ImageFont.load_default()

def preview():
    image = Image.new('RGB', (1800, 1140), '#edf0e9')
    draw = ImageDraw.Draw(image)
    draw.rectangle((900, 0, 1800, 1140), fill='#282d27')
    with tempfile.TemporaryDirectory() as temporary:
        for variant, left in (('Light', 0), ('Dark', 900)):
            color = '#3d463b' if variant == 'Light' else '#f3ecdf'
            draw.text((left + 48, 30), f'Eduka-Icons {variant}', font=font(36), fill=color)
            draw.text((left + 48, 83), '0.3.0 · Standalone · HiDPI 2×', font=font(19), fill=color)
            theme = ROOT / f'build/themes/Eduka-Icons-{variant}'
            for i, (name, context, title) in enumerate(GRID):
                x, y = left + 40 + (i % 5) * 167, 150 + (i // 5) * 205
                with Image.open(theme / '256x256' / context / (name + '.png')) as icon:
                    icon = icon.convert('RGBA').resize((146, 146), Image.Resampling.LANCZOS)
                    image.paste(icon, (x + 12, y), icon)
                draw.text((x + 10, y + 154), title, font=font(17), fill=color)
            for i, name in enumerate(('network-wireless-signal-excellent', 'audio-volume-high', 'battery-full')):
                destination = Path(temporary) / (name + variant + '.png')
                render(theme / 'scalable/status' / (name + '.svg'), 28, destination)
                with Image.open(destination) as icon:
                    image.paste(icon, (left + 50 + i * 52, 1040), icon)
            draw.text((left + 235, 1041), 'Own artwork · PNG + symbolic SVG', font=font(18), fill=color)
    output = ROOT / 'build/preview.png'
    image.save(output)
    print(output)

if __name__ == '__main__': preview()
