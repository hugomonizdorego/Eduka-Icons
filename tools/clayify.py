"""Turn flat application icons into Eduka clay icons.

Used at build time for the vendored Papirus application catalog and at run
time by ``eduka-icons-clayify`` for applications installed later. Needs only
Pillow and librsvg (through ``render.py``).

* ``clay_svg``     sculpts every shape of an SVG with a soft clay lighting filter
* ``raster_clay``  silhouette clay for PNG sources (no SVG available)
* ``finish``       creamy clay colour grading per theme profile
* ``comfort``      eye-comfort edition: dark outline, warm low-blue tint, contrast
* ``monogram``     unique app chip for apps that would otherwise share artwork
"""
import hashlib
import io
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from render import render

SVG_NS = 'http://www.w3.org/2000/svg'
SHAPES = ('path', 'rect', 'circle', 'ellipse', 'polygon')
CHIP_COLORS = ('#df7541', '#e5b652', '#91b6ae', '#89965c', '#7fa9c9', '#9a8fc4', '#d99261', '#c66a7a', '#4f9a8f')
STOP_WORDS = {'org', 'com', 'io', 'net', 'de', 'kde', 'gnome', 'desktop', 'app', 'github', 'gitlab',
              'freedesktop', 'bin', 'the', 'and', 'for', 'linux', 'beta', 'dev', 'nightly', 'stable',
              'flatpak', 'snap', 'default', 'mate', 'xfce', 'xfce4', 'cinnamon', 'lxqt', 'gtk', 'qt5', 'kf5'}


def _filter(scale):
    """Clay lighting filter; ``scale`` is the SVG's user units per 64."""
    s = scale
    return f'''<filter id="eduka-clay" x="-15%" y="-15%" width="135%" height="140%" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceAlpha" stdDeviation="{1.0 * s:.3f}" result="h"/>
 <feDiffuseLighting in="h" surfaceScale="3" diffuseConstant="1.05" lighting-color="#fff8e8" result="l"><feDistantLight azimuth="235" elevation="52"/></feDiffuseLighting>
 <feComposite in="l" in2="SourceAlpha" operator="in" result="l"/>
 <feComposite in="SourceGraphic" in2="l" operator="arithmetic" k1="1.32" k2="0" k3="0" k4="0" result="s"/>
 <feTurbulence type="fractalNoise" baseFrequency="{1.3 / s:.3f}" numOctaves="2" seed="17" result="g"/>
 <feColorMatrix in="g" type="saturate" values="0" result="g"/>
 <feComposite in="g" in2="SourceAlpha" operator="in" result="g"/>
 <feComposite in="s" in2="g" operator="arithmetic" k1="0" k2=".96" k3=".05" k4="0" result="c"/>
 <feGaussianBlur in="SourceAlpha" stdDeviation="{0.8 * s:.3f}" result="d"/><feOffset in="d" dx="{0.6 * s:.3f}" dy="{1.3 * s:.3f}" result="d"/>
 <feFlood flood-color="#403d31" flood-opacity=".22"/><feComposite in2="d" operator="in" result="d"/>
 <feMerge><feMergeNode in="d"/><feMergeNode in="c"/></feMerge></filter>'''


def _opacity(element):
    style = element.get('style', '')
    match = re.search(r'(?:^|;)\s*opacity\s*:\s*([\d.]+)', style)
    value = match.group(1) if match else element.get('opacity')
    try:
        return float(value) if value is not None else 1.0
    except ValueError:
        return 1.0


def _fill(element):
    match = re.search(r'(?:^|;)\s*fill\s*:\s*([^;]+)', element.get('style', ''))
    return (match.group(1) if match else element.get('fill') or '').strip().lower()


def clay_svg(text):
    """Return the SVG with each solid shape sculpted in clay.

    Flat drop shadows (dark shapes with low opacity) are removed because the
    clay filter casts its own soft shadow; light glints stay flat.
    """
    ET.register_namespace('', SVG_NS)
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    root = ET.fromstring(text)
    box = (root.get('viewBox') or '').replace(',', ' ').split()
    width = float(box[2]) if len(box) == 4 else float(re.sub(r'[^\d.]', '', root.get('width', '64')) or 64)
    for parent in list(root.iter()):
        for element in list(parent):
            tag = element.tag.rsplit('}', 1)[-1]
            if tag not in SHAPES:
                continue
            opacity, fill = _opacity(element), _fill(element)
            if opacity <= 0.35 and fill in ('', '#000', '#000000', 'black'):
                parent.remove(element)
            elif opacity > 0.35:
                element.set('filter', 'url(#eduka-clay)')
    defs = ET.fromstring(f'<defs xmlns="{SVG_NS}">{_filter(width / 64)}</defs>')
    root.insert(0, defs)
    return ET.tostring(root, encoding='unicode')


def render_svg(text, size):
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / 'icon.svg'
        target = Path(directory) / 'icon.png'
        source.write_text(text)
        render(source, size, target)
        with Image.open(target) as image:
            return image.convert('RGBA')


def raster_clay(image):
    """Silhouette clay (Pillow only) for raster sources."""
    image = image.convert('RGBA')
    size = image.width
    alpha = image.getchannel('A')
    height = alpha.filter(ImageFilter.GaussianBlur(max(1, size / 36)))
    step = max(1, size // 72)
    lit = ImageChops.offset(height, -step, -step)
    dim = ImageChops.offset(height, step, step)
    shade = ImageChops.subtract(lit, dim, 1, 128)          # 128 = flat, light from top-left
    highlight = shade.point(lambda v: min(255, max(0, v - 128) * 4))
    shadow = shade.point(lambda v: 255 - min(150, max(0, 128 - v) * 4))
    rgb = image.convert('RGB')
    rgb = ImageChops.multiply(rgb, Image.merge('RGB', (shadow,) * 3))
    rgb = ImageChops.screen(rgb, Image.merge('RGB', (highlight.point(lambda v: v * 6 // 10),) * 3))
    grain = Image.effect_noise(image.size, 22).point(lambda v: 118 + v // 12)
    rgb = ImageChops.multiply(rgb, Image.merge('RGB', (grain.point(lambda v: min(255, v + 120)),) * 3))
    result = rgb.convert('RGBA')
    result.putalpha(alpha)
    return add_shadow(result)


def add_shadow(image):
    size = image.width
    alpha = image.getchannel('A')
    shadow = alpha.filter(ImageFilter.GaussianBlur(max(1, size / 80))).point(lambda v: v * 56 // 255)
    shadow = ImageChops.offset(shadow, max(1, size // 107), max(1, size // 49))
    base = Image.new('RGBA', image.size, (64, 61, 49, 0))
    base.putalpha(shadow)
    base.alpha_composite(image)
    return base


def finish(image, profile='standard'):
    """Creamy clay colour grading. ``profile``: standard, bright or comfort."""
    alpha = image.getchannel('A')
    rgb = image.convert('RGB')
    if profile == 'bright':
        rgb = ImageEnhance.Color(rgb).enhance(1.12)
        rgb = ImageEnhance.Brightness(rgb).enhance(1.04)
    else:
        rgb = ImageEnhance.Color(rgb).enhance(0.86)
        rgb = Image.blend(rgb, Image.new('RGB', rgb.size, '#f6ead2'), 0.12)
    rgb.putalpha(alpha)
    return rgb


def comfort(image):
    """Eye-comfort edition for low vision and long sessions.

    A dark contour separates every icon from any background, contrast is
    raised, blue light is reduced and glaring saturation is toned down.
    """
    image = image.convert('RGBA')
    size = image.width
    alpha = image.getchannel('A')
    solid = alpha.point(lambda v: 255 if v > 96 else 0)
    radius = max(1, round(size / 40))
    ring = solid.filter(ImageFilter.MaxFilter(radius * 2 + 1))
    rgb = image.convert('RGB')
    rgb = ImageEnhance.Contrast(rgb).enhance(1.14)
    rgb = ImageEnhance.Color(rgb).enhance(0.9)
    r, g, b = rgb.split()
    rgb = Image.merge('RGB', (r.point(lambda v: min(255, int(v * 1.03))), g, b.point(lambda v: int(v * 0.88))))
    outline = Image.new('RGBA', image.size, (34, 29, 22, 0))
    outline.putalpha(ring)
    body = rgb.convert('RGBA')
    body.putalpha(alpha)
    outline.alpha_composite(body)
    return outline


def _font(size):
    for name in ('DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def initials(name):
    """Two-letter monogram for an icon name (``pcmanfm-qt`` -> ``Pq``)."""
    words = [w for w in re.split(r'[^A-Za-z0-9]+', name) if w and w.lower() not in STOP_WORDS]
    words = words or [w for w in re.split(r'[^A-Za-z0-9]+', name) if w] or ['?']
    if len(words) >= 2:
        return (words[0][0].upper() + words[1][0].lower())
    word = words[0]
    return word[0].upper() + (word[1].lower() if len(word) > 1 else '')


def monogram(base, name):
    """Add a clay chip with the app's monogram so shared artwork stays unique."""
    image = base.convert('RGBA').copy()
    size = image.width
    digest = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)
    color = CHIP_COLORS[digest % len(CHIP_COLORS)]
    diameter = round(size * 0.46)
    chip = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(chip)
    draw.ellipse((0, 0, diameter - 1, diameter - 1), fill=color)
    text = initials(name)
    font = _font(round(diameter * (0.5 if len(text) > 1 else 0.6)))
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((diameter - box[2] - box[0]) / 2, (diameter - box[3] - box[1]) / 2 - diameter * 0.02),
              text, font=font, fill='#fff6e4')
    chip = raster_clay(chip)
    image.alpha_composite(chip, (size - diameter - round(size * 0.02), size - diameter - round(size * 0.02)))
    return image


def save_png(image, path, quantize=True):
    """Write the smaller of a lossless and a 256-colour PNG."""
    plain = io.BytesIO()
    image.save(plain, 'PNG', optimize=True)
    best = plain.getvalue()
    if quantize and image.width >= 32:
        palette = io.BytesIO()
        image.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(palette, 'PNG', optimize=True)
        if len(palette.getvalue()) < len(best):
            best = palette.getvalue()
    Path(path).write_bytes(best)
