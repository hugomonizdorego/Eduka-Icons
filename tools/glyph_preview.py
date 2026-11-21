#!/usr/bin/env python3
"""Pixel review sheet for the flat line glyphs.

  python3 tools/glyph_preview.py                 # every glyph kind
  python3 tools/glyph_preview.py wifi-high bell  # selected kinds

Each cell: real 16, 22, 24 and 32 px renders on light and dark, plus the
16 px and 22 px renders enlarged 6x (nearest neighbour) to inspect pixels.
"""
import os
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import symbolic  # noqa: E402
from render import render  # noqa: E402


def glyph(kind, size, color, directory):
    source = Path(directory) / f'{kind}.svg'
    source.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">'
                      f'<path d="{symbolic.glyph_path(kind)}" fill="{color}"/></svg>')
    target = Path(directory) / f'{kind}-{size}-{color[1:]}.png'
    render(source, size, target)
    with Image.open(target) as image:
        return image.convert('RGBA')


def main():
    kinds = sys.argv[1:] or sorted(symbolic.BASE)
    cols = 4
    cell_w, cell_h = 420, 150
    rows = (len(kinds) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell_w, rows * cell_h), '#f4f1ea')
    draw = ImageDraw.Draw(sheet)
    with tempfile.TemporaryDirectory() as directory:
        for index, kind in enumerate(kinds):
            x, y = (index % cols) * cell_w, (index // cols) * cell_h
            draw.text((x + 6, y + 4), kind, fill='#000')
            cx = x + 6
            for size in (16, 22, 24, 32):
                image = glyph(kind, size, '#3d463b', directory)
                sheet.paste(image, (cx, y + 24), image)
                cx += size + 8
            draw.rectangle((x + 6, y + 64, x + 130, y + 104), fill='#262b27')
            cx = x + 10
            for size in (16, 22, 24, 32):
                image = glyph(kind, size, '#f3ecdf', directory)
                sheet.paste(image, (cx, y + 68), image)
                cx += size + 6
            for offset, size in ((140, 16), (250, 22)):
                image = glyph(kind, size, '#3d463b', directory)
                zoom = image.resize((size * 6, size * 6), Image.Resampling.NEAREST)
                sheet.paste(zoom, (x + offset, y + 10), zoom)
    output = Path(os.environ.get('ART_OUT', '.')) / 'glyphs.png'
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(output, len(kinds), 'glyphs')


if __name__ == '__main__':
    main()
