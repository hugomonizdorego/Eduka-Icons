"""Turn flat application icons into Eduka clay icons.

Used at build time for the vendored Papirus catalog and at run time by
``eduka-icons-clayify`` for applications installed later. Needs only Pillow
and librsvg (through ``render.py``).

* ``clay_svg``     sculpts every shape of an SVG with a soft clay lighting filter
* ``raster_clay``  silhouette clay for PNG sources (no SVG available)
* ``finish``       warm clay colour grading that keeps dark and saturated colours
* ``sharpen``      crisp small sizes
* ``comfort``      eye-comfort edition built from the master: anti-aliased dark
                   contour around the outer silhouette, warm low-blue colours
* ``monogram``     unique app chip for apps that would otherwise share artwork
* ``save_png``     small PNG files without touching transparency
"""
import hashlib
import io
import math
import os
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from render import render

SVG_NS = 'http://www.w3.org/2000/svg'
SHAPES = ('path', 'rect', 'circle', 'ellipse', 'polygon')
SKIP = ('defs', 'clipPath', 'mask', 'pattern', 'symbol', 'marker', 'linearGradient', 'radialGradient', 'filter')
MAX_SVG_BYTES = 2 * 1024 * 1024
MAX_PIXELS = 4096 * 4096
# Chip colours: every one gives the cream letters a contrast of at least 4.5:1.
CHIP_COLORS = ('#a8481e', '#85600c', '#35766c', '#5a673c', '#3a6a90', '#66569c', '#93521f', '#9c4458', '#2a756b')
CHIP_TEXT = '#fff6e4'
STOP_WORDS = {'org', 'com', 'io', 'net', 'de', 'kde', 'gnome', 'desktop', 'app', 'github', 'gitlab',
              'freedesktop', 'bin', 'the', 'and', 'for', 'linux', 'beta', 'dev', 'nightly', 'stable',
              'flatpak', 'snap', 'default', 'mate', 'xfce', 'xfce4', 'cinnamon', 'lxqt', 'gtk', 'qt5', 'kf5'}
IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
NUMBER = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'


def _filter(scale, width):
    """Clay lighting filter in root user space; ``scale`` is user units per 64."""
    s, margin = scale, 0.14 * width
    return f'''<filter id="eduka-clay" filterUnits="userSpaceOnUse" x="{-margin:.2f}" y="{-margin:.2f}" width="{width + 2 * margin:.2f}" height="{width + 2 * margin:.2f}" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceAlpha" stdDeviation="{1.0 * s:.3f}" result="h"/>
 <feDiffuseLighting in="h" surfaceScale="3" diffuseConstant="1.05" lighting-color="#fff8e8" result="l"><feDistantLight azimuth="235" elevation="52"/></feDiffuseLighting>
 <feComposite in="l" in2="SourceAlpha" operator="in" result="l"/>
 <feComposite in="SourceGraphic" in2="l" operator="arithmetic" k1="1.21" k2="0" k3="0" k4="0" result="s"/>
 <feTurbulence type="fractalNoise" baseFrequency="{1.3 / s:.3f}" numOctaves="2" seed="17" result="g"/>
 <feColorMatrix in="g" type="saturate" values="0" result="g"/>
 <feComposite in="g" in2="SourceAlpha" operator="in" result="g"/>
 <feComposite in="s" in2="g" operator="arithmetic" k1=".10" k2=".95" k3="0" k4="0" result="c"/>
 <feGaussianBlur in="SourceAlpha" stdDeviation="{0.8 * s:.3f}" result="d"/><feOffset in="d" dx="{0.6 * s:.3f}" dy="{1.3 * s:.3f}" result="d"/>
 <feFlood flood-color="#403d31" flood-opacity=".22"/><feComposite in2="d" operator="in" result="d"/>
 <feMerge><feMergeNode in="d"/><feMergeNode in="c"/></feMerge></filter>'''


def _style(element, key):
    match = re.search(rf'(?:^|;)\s*{key}\s*:\s*([^;]+)', element.get('style', ''))
    return (match.group(1) if match else element.get(key) or '').strip()


def _opacity(element):
    try:
        return float(_style(element, 'opacity') or 1.0)
    except ValueError:
        return 1.0


def _multiply(m, n):
    return (m[0] * n[0] + m[2] * n[1], m[1] * n[0] + m[3] * n[1], m[0] * n[2] + m[2] * n[3], m[1] * n[2] + m[3] * n[3],
            m[0] * n[4] + m[2] * n[5] + m[4], m[1] * n[4] + m[3] * n[5] + m[5])


def _transform(text):
    matrix = IDENTITY
    for name, arguments in re.findall(r'(\w+)\s*\(([^)]*)\)', text or ''):
        a = [float(x) for x in re.findall(NUMBER, arguments)]
        if name == 'matrix' and len(a) == 6: step = tuple(a)
        elif name == 'translate' and a: step = (1, 0, 0, 1, a[0], a[1] if len(a) > 1 else 0)
        elif name == 'scale' and a: step = (a[0], 0, 0, a[1] if len(a) > 1 else a[0], 0, 0)
        elif name == 'rotate' and a:
            c, s = math.cos(math.radians(a[0])), math.sin(math.radians(a[0]))
            step = (c, s, -s, c, 0, 0)
            if len(a) == 3: step = _multiply(_multiply((1, 0, 0, 1, a[1], a[2]), step), (1, 0, 0, 1, -a[1], -a[2]))
        elif name == 'skewX' and a: step = (1, 0, math.tan(math.radians(a[0])), 1, 0, 0)
        elif name == 'skewY' and a: step = (1, math.tan(math.radians(a[0])), 0, 1, 0, 0)
        else: step = IDENTITY
        matrix = _multiply(matrix, step)
    return matrix


def _inverse(m):
    det = m[0] * m[3] - m[1] * m[2]
    if abs(det) < 1e-9:
        return None
    a, b, c, d = m[3] / det, -m[1] / det, -m[2] / det, m[0] / det
    return (a, b, c, d, -(a * m[4] + c * m[5]), -(b * m[4] + d * m[5]))


def _matrix(m):
    return 'matrix(' + ' '.join(f'{v:.6g}' for v in m) + ')'


def _length(value, fallback):
    match = re.match(rf'\s*({NUMBER})\s*(px)?\s*$', value or '')
    return float(match.group(1)) if match else fallback


def clay_svg(text):
    """Return the SVG with each solid shape sculpted in clay.

    The filter runs in root user space, so strokes, rotated or mirrored groups
    and scaled parts are lit and shadowed like everything else. Translucent
    shapes (flat shading, glints, patterns) are kept as they are.
    """
    if len(text) > MAX_SVG_BYTES or '<!ENTITY' in text or '<!DOCTYPE' in text.upper().replace('<!DOCTYPE SVG', ''):
        raise ValueError('unsupported SVG (too large or uses entities)')
    ET.register_namespace('', SVG_NS)
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    root = ET.fromstring(text)
    box = [float(v) for v in re.findall(NUMBER, root.get('viewBox') or '')]
    if len(box) == 4 and box[2] > 0 and box[3] > 0:
        x, y, width, height = box
    else:
        x, y, width, height = 0.0, 0.0, _length(root.get('width'), 64.0), _length(root.get('height'), 64.0)
    side = max(width, height)

    def walk(parent, matrix, opacity):
        for element in list(parent):
            tag = element.tag.rsplit('}', 1)[-1]
            if tag in SKIP:
                continue
            visible = opacity * _opacity(element)
            if tag not in SHAPES:
                walk(element, _multiply(matrix, _transform(element.get('transform'))), visible)
                continue
            if visible <= 0.35:
                continue                      # flat shading or glint
            back = _inverse(matrix)
            if back is None:
                continue
            if matrix == IDENTITY and not element.get('transform'):
                element.set('filter', 'url(#eduka-clay)')
                continue
            outer = ET.Element(f'{{{SVG_NS}}}g', {'transform': _matrix(back), 'filter': 'url(#eduka-clay)'})
            inner = ET.SubElement(outer, f'{{{SVG_NS}}}g', {'transform': _matrix(matrix)})
            position = list(parent).index(element)
            parent.remove(element)
            inner.append(element)
            outer.tail, element.tail = element.tail, None
            parent.insert(position, outer)

    walk(root, IDENTITY, 1.0)
    # Square canvas with room for the clay shadow: the artwork keeps about 93 % of it.
    pad = side * 0.035
    root.set('viewBox', f'{x - pad - (side - width) / 2:.3f} {y - pad * 0.75 - (side - height) / 2:.3f} '
                        f'{side + 2 * pad:.3f} {side + 2 * pad:.3f}')
    root.set('width', '64')
    root.set('height', '64')
    defs = ET.fromstring(f'<defs xmlns="{SVG_NS}">{_filter(side / 64, side)}</defs>')
    filter_element = defs[0]
    margin = 0.14 * side
    filter_element.set('x', f'{x - margin:.2f}')
    filter_element.set('y', f'{y - margin:.2f}')
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


def open_raster(path):
    """Open an untrusted raster icon safely as RGBA."""
    with Image.open(path) as image:
        if image.width * image.height > MAX_PIXELS:
            raise ValueError('image too large')
        return image.convert('RGBA')


def _shift(image, dx, dy):
    """Translate without wrapping around the edges."""
    moved = Image.new(image.mode, image.size, 0)
    moved.paste(image, (dx, dy))
    return moved


def add_shadow(image):
    size = image.width
    alpha = image.getchannel('A')
    shadow = alpha.filter(ImageFilter.GaussianBlur(max(1, size / 80))).point(lambda v: v * 56 // 255)
    shadow = _shift(shadow, max(1, size // 107), max(1, size // 49))
    base = Image.new('RGBA', image.size, (64, 61, 49, 0))
    base.putalpha(shadow)
    base.alpha_composite(image)
    return base


def raster_clay(image, pad=True):
    """Silhouette clay (Pillow only) for raster sources; the result keeps the input size."""
    image = image.convert('RGBA')
    original = image.size
    if pad:    # room for the bevel and the shadow
        side = max(image.size)
        border = max(2, side // 14)
        canvas = Image.new('RGBA', (side + 2 * border, side + 2 * border), (0, 0, 0, 0))
        canvas.paste(image, (border + (side - image.width) // 2, border + (side - image.height) // 2))
        image = canvas
    size = image.width
    alpha = image.getchannel('A')
    height = alpha.filter(ImageFilter.GaussianBlur(max(1, size / 36)))
    step = max(1, size // 72)
    shade = ImageChops.subtract(_shift(height, -step, -step), _shift(height, step, step), 1, 128)  # light: top-left
    highlight = shade.point(lambda v: min(255, max(0, v - 128) * 4))
    shadow = shade.point(lambda v: 255 - min(150, max(0, 128 - v) * 4))
    rgb = image.convert('RGB')
    rgb = ImageChops.multiply(rgb, Image.merge('RGB', (shadow,) * 3))
    rgb = ImageChops.screen(rgb, Image.merge('RGB', (highlight.point(lambda v: v * 6 // 10),) * 3))
    result = rgb.convert('RGBA')
    result.putalpha(alpha)
    result = add_shadow(result)
    if pad:
        result = result.resize((max(original),) * 2, Image.Resampling.LANCZOS)
    return result


def finish(image, profile='standard'):
    """Warm clay grading by multiplication: black stays black, white becomes cream."""
    alpha = image.getchannel('A')
    rgb = image.convert('RGB')
    if profile == 'bright':
        rgb = ImageEnhance.Color(rgb).enhance(1.12)
    else:
        rgb = ImageEnhance.Color(rgb).enhance(0.92)
        cream = Image.new('RGB', rgb.size, '#f6ead2')
        rgb = Image.blend(rgb, ImageChops.multiply(rgb, cream), 0.35)
    rgb.putalpha(alpha)
    return rgb


def sharpen(image, size, up_to=48, percent=100):
    """Crisp small icons: unsharp mask on the colour channels only (alpha untouched)."""
    if size > up_to or percent <= 0:
        return image
    amount = percent if size <= 24 else round(percent * 0.6)
    alpha = image.getchannel('A')
    rgb = image.convert('RGB').filter(ImageFilter.UnsharpMask(radius=0.6, percent=amount, threshold=0))
    rgb.putalpha(alpha)
    return rgb


def rim(image, strength=0.74):
    """Darken the outer pixel ring so cream objects keep an edge on light backgrounds."""
    alpha = image.getchannel('A')
    inner = alpha.filter(ImageFilter.MinFilter(3))
    edge = ImageChops.subtract(alpha, inner)
    dark = ImageEnhance.Brightness(image.convert('RGB')).enhance(strength)
    rgb = Image.composite(dark, image.convert('RGB'), edge)
    rgb.putalpha(alpha)
    return rgb


def fit(image, margin=0.05):
    """Shrink and centre artwork whose opaque box comes closer than ``margin`` to the canvas edge."""
    size = image.width
    box = image.getchannel('A').point(lambda v: 255 if v > 16 else 0).getbbox()
    if box is None:
        return image
    limit = size * margin
    if min(box[0], box[1], size - box[2], size - box[3]) >= limit:
        return image
    width, height = box[2] - box[0], box[3] - box[1]
    scale = min(1.0, (size - 2 * limit) / max(width, height))
    part = image.crop(box)
    if scale < 1.0:
        part = part.resize((max(1, round(width * scale)), max(1, round(height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', image.size, (0, 0, 0, 0))
    canvas.paste(part, ((size - part.width) // 2, (size - part.height) // 2))
    return canvas


def _outer(alpha):
    """Outer silhouette of an alpha mask: enclosed openings are filled, the outside is not."""
    solid = alpha.point(lambda v: 255 if v > 96 else 0)
    padded = Image.new('L', (solid.width + 2, solid.height + 2), 0)
    padded.paste(solid, (1, 1))
    ImageDraw.floodfill(padded, (0, 0), 128)
    return padded.crop((1, 1, solid.width + 1, solid.height + 1)).point(lambda v: 0 if v == 128 else 255)


def comfort(master, size, outline='#221d16', contrast=1.14, saturation=0.9, blue=0.88,
            sharpen_up_to=48, sharpen_percent=100):
    """Eye-comfort icon of ``size`` pixels made from a larger master.

    The artwork is scaled into the canvas minus the contour, so nothing is cut
    off; the contour follows the outer silhouette only (openings stay open at
    small sizes), is anti-aliased, and carries a thin light halo from 32 px so
    it also separates the icon from dark panels.
    """
    master = master.convert('RGBA')
    ring = max(1.0, size * 0.04)
    halo = 1 if size >= 32 else 0
    inset = math.ceil(ring) + halo
    inner = max(4, size - 2 * inset)
    art = sharpen(master.resize((inner, inner), Image.Resampling.LANCZOS), size, sharpen_up_to, sharpen_percent)
    alpha = art.getchannel('A')
    rgb = art.convert('RGB')
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Color(rgb).enhance(saturation)
    r, g, b = rgb.split()
    rgb = Image.merge('RGB', (r.point(lambda v: min(255, int(v * 1.03))), g, b.point(lambda v: int(v * blue))))
    body = rgb.convert('RGBA')
    body.putalpha(alpha)
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    canvas.paste(body, (inset, inset))
    # Contour at 4x for anti-aliasing.
    factor = 4 if size <= 64 else (2 if size <= 128 else 1)
    big = canvas.getchannel('A').resize((size * factor, size * factor), Image.Resampling.BICUBIC)
    shape = _outer(big) if size <= 32 else big.point(lambda v: 255 if v > 96 else 0)

    def grow(radius):
        return shape.filter(ImageFilter.GaussianBlur(radius * factor)).point(lambda v: min(255, v * 6)) \
                    .resize((size, size), Image.Resampling.LANCZOS)

    result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    if halo:
        light = Image.new('RGBA', (size, size), ImageColor.getrgb('#f6ead2')[:3] + (0,))
        light.putalpha(grow(ring + 1.0).point(lambda v: v * 140 // 255))
        result.alpha_composite(light)
    dark = Image.new('RGBA', (size, size), ImageColor.getrgb(outline)[:3] + (0,))
    strength = 180 if size <= 24 else 255
    dark.putalpha(grow(ring).point(lambda v: v * strength // 255))
    result.alpha_composite(dark)
    result.alpha_composite(canvas)
    return result


def _font(size):
    for name in ('DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def initials(name):
    """Two-letter monogram for an icon name (``pcmanfm-qt`` -> ``Pq``, ``io.elementary.screenshot`` -> ``Sc``)."""
    text = name
    if name.count('.') >= 2:               # reverse-DNS application ID: the last meaningful component
        parts = [p for p in name.split('.') if p and p.lower() not in STOP_WORDS]
        text = parts[-1] if parts else name
    words = [w for w in re.split(r'[^A-Za-z0-9]+', text) if w and w.lower() not in STOP_WORDS]
    words = [w for w in words if not w.isdigit()] or words
    words = words or [w for w in re.split(r'[^A-Za-z0-9]+', name) if w] or ['?']
    if len(words) >= 2:
        return words[0][0].upper() + words[1][0].lower()
    word = words[0]
    return word[0].upper() + (word[1].lower() if len(word) > 1 else '')


def monogram(base, name, letters=2):
    """Add a clay chip with the app's monogram so shared artwork stays unique."""
    image = base.convert('RGBA').copy()
    size = image.width
    digest = int(hashlib.sha256(name.encode()).hexdigest()[:8], 16)
    color = CHIP_COLORS[digest % len(CHIP_COLORS)]
    diameter = round(size * 0.46)
    chip = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(chip)
    draw.ellipse((0, 0, diameter - 1, diameter - 1), fill=color)
    text = initials(name)[:letters]
    font = _font(round(diameter * (0.5 if len(text) > 1 else 0.66)))
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((diameter - box[2] - box[0]) / 2, (diameter - box[3] - box[1]) / 2 - diameter * 0.02),
              text, font=font, fill=CHIP_TEXT)
    chip = raster_clay(chip)
    margin = max(1, round(size * 0.04))
    image.alpha_composite(chip, (size - diameter - margin, size - diameter - margin))
    return image


def _posterize(image, bits):
    """Fewer colour levels (alpha untouched): much smaller PNG, error below 2**(8-bits)."""
    mask = 256 - (1 << (8 - bits))
    alpha = image.getchannel('A')
    rgb = image.convert('RGB').point(lambda v: (v & mask) | ((v & mask) >> bits))
    rgb = Image.composite(rgb, Image.new('RGB', image.size, 0), alpha.point(lambda v: 255 if v else 0))
    rgb.putalpha(alpha)
    return rgb


def _png(image):
    data = io.BytesIO()
    image.save(data, 'PNG', optimize=True)
    return data.getvalue()


def save_png(image, path, quality='fine'):
    """Write a compact PNG that never changes transparency.

    quality 'lossless': exact pixels. 'fine': 6 bits per colour channel (error <= 3).
    'small': 5 bits (error <= 7), or a 256-colour palette when that file is
    smaller and passes a safety check: opaque stays opaque, clear stays clear,
    and on visible pixels the colour error is small (mean <= 7 of 255,
    99 % of the pixels <= 28).
    """
    image = image.convert('RGBA')
    if quality == 'lossless':
        best = _png(image)
    elif quality == 'fine':
        best = _png(_posterize(image, 6))
    else:
        best = _png(_posterize(image, 5))
        palette = image.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        entries = palette.getpalette('RGBA')
        if entries:                      # the quantiser averages alpha: keep solid colours solid
            entries[3::4] = [255 if value >= 216 else value for value in entries[3::4]]
            palette.putpalette(entries, 'RGBA')
        back = palette.convert('RGBA')
        alpha, new_alpha = image.getchannel('A'), back.getchannel('A')
        opaque_kept = ImageChops.subtract(alpha.point(lambda v: 255 if v == 255 else 0), new_alpha).getextrema()[1] <= 8
        clear_kept = ImageChops.multiply(alpha.point(lambda v: 255 if v == 0 else 0), new_alpha).getextrema()[1] == 0
        alpha_kept = ImageChops.difference(alpha, new_alpha).getextrema()[1] <= 56
        bands = ImageChops.difference(image.convert('RGB'), back.convert('RGB')).split()
        worst = ImageChops.lighter(ImageChops.lighter(bands[0], bands[1]), bands[2])
        histogram = worst.histogram(alpha.point(lambda v: 255 if v > 48 else 0))
        visible = sum(histogram) or 1
        mean = sum(i * n for i, n in enumerate(histogram)) / visible
        tail = sum(histogram[29:]) / visible
        if opaque_kept and clear_kept and alpha_kept and mean <= 7 and tail <= 0.01:
            data = _png(palette)
            if len(data) < len(best):
                best = data
    path = Path(path)
    temporary = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    try:
        temporary.write_bytes(best)
        os.replace(temporary, path)          # readers never see a half-written icon
    finally:
        temporary.unlink(missing_ok=True)
