#!/usr/bin/env python3
"""Render a review sheet for one tools/art module (or any list of kinds).

  python3 tools/art_preview.py devices            # kinds of tools/art/devices.py
  python3 tools/art_preview.py --kinds clock bell # explicit kinds
  python3 tools/art_preview.py --badges badges    # folder badges of a module

Each row: 0.5 drawing, 1.0 drawing (large), then 64/48/32/24/16 px on light and
64/32/16 px on dark. Prints the alpha bounding box of the 1024 px master and
warns when artwork (or its shadow) touches the canvas edge.
"""
import argparse
import importlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clay  # noqa: E402
from render import render  # noqa: E402


def master(svg_text, size=512):
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / 'a.svg'
        source.write_text(svg_text)
        render(source, size, Path(directory) / 'a.png')
        with Image.open(Path(directory) / 'a.png') as image:
            return image.convert('RGBA')


def old_vector(kind):
    saved = dict(clay.OVERRIDES)
    clay.OVERRIDES.clear()
    try:
        return master(clay.vector(kind))
    except Exception:
        return None
    finally:
        clay.OVERRIDES.update(saved)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('module', nargs='?')
    parser.add_argument('--kinds', nargs='*')
    parser.add_argument('--badges', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.module:
        module = importlib.import_module(f'art.{args.module}')
        kinds = list((module.BADGES if args.badges else module.ART))
    else:
        kinds = args.kinds or []
    output = args.output or Path(os.environ.get('ART_OUT', '.')) / f'{args.module or "kinds"}{"-badges" if args.badges else ""}.png'
    row, pad = 190, 10
    sheet = Image.new('RGB', (1240, row * len(kinds) + 30), '#eef0e9')
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 6), 'kind | 0.5 | 1.0 | 64 48 32 24 16 on light | 64 32 16 on dark | 32 px zoomed x4', fill='#444')
    for index, kind in enumerate(kinds):
        y = 26 + index * row
        if args.badges:
            new = master(clay.folder_svg(kind))
            saved = dict(clay.BADGES); clay.BADGES.clear()
            try: old = master(clay.folder_svg(kind))
            except Exception: old = None
            finally: clay.BADGES.update(saved)
        else:
            new = master(clay.vector(kind))
            old = old_vector(kind)
        box = new.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
        edge = box and (box[0] <= 2 or box[1] <= 2 or box[2] >= new.width - 2 or box[3] >= new.height - 2)
        print(f'{kind:18} bbox={box} of {new.size}' + ('  WARNING: touches the canvas edge (will be clipped)' if edge else ''))
        draw.text((pad, y + 4), kind, fill='#000')
        x = 110
        for image in (old, new):
            if image is not None:
                big = image.resize((176, 176), Image.Resampling.LANCZOS)
                sheet.paste(big, (x, y + 6), big)
            x += 186
        for size in (64, 48, 32, 24, 16):
            small = new.resize((size, size), Image.Resampling.LANCZOS)
            sheet.paste(small, (x, y + 60), small)
            x += size + 12
        draw.rectangle((x + 4, y + 4, x + 150, y + row - 8), fill='#262b27')
        x += 14
        for size in (64, 32, 16):
            small = new.resize((size, size), Image.Resampling.LANCZOS)
            sheet.paste(small, (x, y + 60), small)
            x += size + 10
        x += 30
        zoom = new.resize((32, 32), Image.Resampling.LANCZOS).resize((128, 128), Image.Resampling.NEAREST)
        sheet.paste(zoom, (x, y + 30), zoom)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(output)


if __name__ == '__main__':
    main()
