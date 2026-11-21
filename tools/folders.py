"""Folder colour variants.

The aqua clay of the folder master is re-tinted (hue, saturation and value
shift of the aqua pixels only), so the cream sheets, the orange button and the
olive badge keep their colours.
"""
from PIL import Image, ImageChops

# name -> (hue in degrees, saturation factor, value factor). Aqua is the master itself.
COLOURS = {
    'aqua': None,
    'olive': (78, 1.15, 0.86),
    'orange': (22, 1.9, 1.02),
    'yellow': (43, 1.75, 1.06),
    'rose': (352, 1.25, 1.0),
    'blue': (214, 1.35, 0.96),
    'plum': (268, 0.95, 0.92),
    'grey': (40, 0.22, 0.92),
}
AQUA_HUE = (150, 215)     # degrees covered by the master's aqua clay


def _lut(function):
    return [max(0, min(255, int(round(function(v))))) for v in range(256)]


def tint(image, colour):
    """Return the folder image in another clay colour."""
    spec = COLOURS[colour]
    if spec is None:
        return image
    hue, saturation, value = spec
    alpha = image.getchannel('A')
    h, s, v = image.convert('RGB').convert('HSV').split()
    low, high = (round(d / 360 * 255) for d in AQUA_HUE)
    in_hue = h.point(_lut(lambda x: 255 if low <= x <= high else 0))
    coloured = s.point(_lut(lambda x: 255 if x >= 28 else (0 if x < 16 else (x - 16) * 21)))
    mask = ImageChops.multiply(in_hue, coloured)
    new_h = Image.new('L', image.size, round(hue / 360 * 255))
    new_s = s.point(_lut(lambda x: x * saturation))
    new_v = v.point(_lut(lambda x: x * value))
    recoloured = Image.merge('HSV', (new_h, new_s, new_v)).convert('RGB')
    result = Image.composite(recoloured, image.convert('RGB'), mask).convert('RGBA')
    result.putalpha(alpha)
    return result
