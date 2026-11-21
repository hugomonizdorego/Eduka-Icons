"""Eduka-Icons 1.0 clay artwork: media group.

video, headphones, volume, mic, image, flower, palette, paint, font.
Every function returns an SVG fragment on the 128 x 128 grid; tools/clay.py
sculpts each shape element separately. GPL-3.0.
"""
import math
import re
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_D = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_D, YELLOW = '#e0703a', '#b9552a', '#eec14f'
OLIVE, OLIVE_D = '#7d8c55', '#5f6c40'
AQUA, AQUA_D, CHARCOAL = '#8fc0c4', '#6a9ea3', '#3f3c37'


def group(transform, *parts):
    return f'<g transform="{transform}">' + ''.join(parts) + '</g>'


def ellipse(cx, cy, rx, ry, c, **kw):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    fill = c if c == 'none' or c.startswith('#') else f'url(#{c})'
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'


def turn(d, degrees, ox=0, oy=0, k=1):
    """Rotate, scale and move path data (absolute M L H V C Q A Z only).

    Turning the geometry instead of the element keeps the clay light and the
    soft shadow pointing the same way as on every other icon.
    """
    a = math.radians(degrees)
    c, s = math.cos(a) * k, math.sin(a) * k
    tokens = re.findall(r'[MLHVCQAZ]|-?\d*\.?\d+', d)
    out, i, x, y, cmd = [], 0, 0.0, 0.0, ''
    pt = lambda px, py: f'{ox + px * c - py * s:.2f} {oy + px * s + py * c:.2f}'
    while i < len(tokens):
        if tokens[i].isalpha():
            cmd = tokens[i]
            i += 1
            if cmd == 'Z':
                out.append('Z')
                continue
        if cmd in 'HV':
            v = float(tokens[i])
            i += 1
            x, y = (v, y) if cmd == 'H' else (x, v)
            out.append('L' + pt(x, y))
        elif cmd == 'A':
            rx, ry, rot = (float(t) for t in tokens[i:i + 3])
            x, y = float(tokens[i + 5]), float(tokens[i + 6])
            out.append(f'A{rx * k:.2f} {ry * k:.2f} {rot + degrees:.2f} {tokens[i + 3]} {tokens[i + 4]} {pt(x, y)}')
            i += 7
        else:
            n = {'M': 1, 'L': 1, 'Q': 2, 'C': 3}[cmd]
            nums = [float(t) for t in tokens[i:i + 2 * n]]
            i += 2 * n
            x, y = nums[-2], nums[-1]
            out.append(cmd + ' '.join(pt(nums[j], nums[j + 1]) for j in range(0, 2 * n, 2)))
    return ''.join(out)


def rr(x, y, w, h, r):
    """Path data of a rounded rectangle (for turn())."""
    return (f'M{x + r} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h - r}A{r} {r} 0 0 1 {x + w - r} {y + h}'
            f'H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}V{y + r}A{r} {r} 0 0 1 {x + r} {y}Z')


# --------------------------------------------------------------------------
def video():
    """Clapperboard with an open striped arm and a big play button."""
    def stripes(y, h):
        return ''.join(path(f'M{x} {y}H{x + 10}L{x + 4} {y + h}H{x - 6}Z', 'cream') for x in (33, 52, 71, 90))
    s = rect(22, 56, 85, 49, 10, 'cream-dark')                 # side / bottom face
    s += rect(19, 52, 85, 49, 10, 'cream')                     # slate face
    s += rect(19, 46, 85, 13, 5, 'charcoal') + stripes(46, 13)  # fixed bar
    s += group('rotate(-12 24 46)', rect(19, 32, 85, 13, 5, 'charcoal'), stripes(32, 13))
    s += circle(26, 46, 6, 'yellow-dark') + circle(26, 45, 4, 'yellow')   # hinge
    s += circle(63, 82, 15, 'orange-dark') + circle(62, 80, 15, 'orange')
    s += path('M56.5 71Q56.5 68.5 59 70L73 78Q75.5 80 73 82L59 90Q56.5 91.5 56.5 89Z', 'white')
    s += rect(27, 66, 14, 5, 2.5, 'olive') + rect(27, 76, 10, 5, 2.5, 'aqua-dark')
    s += circle(92, 68, 3.5, 'yellow') + circle(92, 80, 3.5, 'olive') + circle(92, 92, 3.5, 'aqua-dark')
    s += rect(27, 88, 14, 5, 2.5, 'cream-dark')
    return s


# --------------------------------------------------------------------------
def headphones():
    """Over-ear headphones: cream band, orange head pad, olive cups."""
    band = 'M29 70V58C29 15 97 15 97 58V70'
    s = line('M31 72V60C31 19 99 19 99 60V72', CREAM_D, 11)       # band thickness
    s += line(band, CREAM, 11)
    s += line('M48 30Q63 23.5 78 30', ORANGE_D, 16)
    s += line('M48 28.5Q63 22 78 28.5', ORANGE, 14)              # head pad
    s += rect(23, 50, 12, 16, 4, 'yellow') + rect(91, 50, 12, 16, 4, 'yellow')   # sliders
    for x, cushion in ((16, 36), (88, 80)):
        s += rect(cushion, 63, 11, 34, 5.5, 'orange-dark')
        s += rect(cushion, 62, 11, 32, 5.5, 'orange')            # ear cushion
        s += rect(x, 61, 22, 42, 10, 'olive-dark')
        s += rect(x, 58, 22, 41, 10, 'olive')                    # cup shell
        s += rect(x + 6, 66, 10, 25, 5, 'olive-dark')
        s += circle(x + 11, 72, 3.5, 'yellow')
    return s


# --------------------------------------------------------------------------
def volume():
    """Loudspeaker horn seen at three quarters, with two sound waves."""
    s = line('M88 47Q98 62 88 77', AQUA_D, 7)
    s += line('M96 35Q113 62 96 89', AQUA, 7)
    s += path('M38 52L66 24H70V104H66L38 76Z', 'orange-dark')
    s += path('M36 49L64 21H68V99H64L36 73Z', 'orange')            # horn body
    s += ellipse(68, 62, 13, 42, 'cream-dark')
    s += ellipse(66, 61, 13, 42, 'cream')                         # rim
    s += ellipse(66, 61, 8.5, 35, 'orange-dark')                  # inside of the horn
    s += ellipse(65, 61, 4.5, 13, 'yellow')                       # dust cap
    s += rect(19, 49, 24, 30, 7, 'cream-dark')
    s += rect(17, 46, 24, 30, 7, 'cream')                         # magnet / driver box
    s += rect(36, 47, 7, 28, 3, 'olive')                          # collar
    s += circle(27, 55, 3.5, 'olive') + circle(27, 67, 3.5, 'orange')
    return s


# --------------------------------------------------------------------------
def mic():
    """Desk microphone: orange grille head, cream body, olive cradle and foot."""
    s = rect(37, 96, 56, 10, 5, 'olive-dark')
    s += rect(35, 93, 56, 10, 5, 'olive')                         # foot
    s += rect(58, 84, 12, 12, 3, 'cream-dark')                    # stem
    s += line('M31 54V59Q31 87 64 87Q97 87 97 59V54', OLIVE_D, 9)
    s += line('M30 52V57Q30 85 64 85Q98 85 98 57V52', OLIVE, 9)   # cradle
    s += rect(43, 19, 46, 58, 23, 'cream-dark')
    s += rect(41, 16, 46, 58, 23, 'cream')                        # body
    s += path('M41 47V39Q41 16 64 16Q87 16 87 39V47Z', 'orange')  # grille head
    s += line('M53 26.5H75M49.5 36H78.5', ORANGE_D, 4.5)
    s += rect(38.5, 43.5, 51, 9, 4.5, 'yellow')                   # ring
    s += rect(59.5, 57, 9, 13, 4.5, 'olive') + circle(64, 61.5, 2.8, 'yellow')
    s += circle(29.5, 53, 5.5, 'yellow') + circle(98.5, 53, 5.5, 'yellow')    # pivots
    return s


# --------------------------------------------------------------------------
def image():
    """Two instant photos; the front one shows sun, mountain and hill."""
    s = group('rotate(10 64 62)', rect(27, 25, 78, 70, 8, 'olive-dark'), rect(26, 23, 78, 70, 8, 'olive'))
    front = rect(22, 28, 84, 72, 9, 'cream-dark')
    front += rect(20, 25, 84, 72, 9, 'cream')
    front += rect(28, 33, 68, 48, 5, 'aqua')
    front += circle(81, 46, 7.5, 'yellow')
    front += path('M36 48Q30 48 30 53Q30 57 35 57H50Q55 57 55 52.5Q55 48 50 48Q49 43 43 43Q37 43 36 48Z', 'white')
    front += path('M28 78L48 53Q52 49 56 53L78 81H33Q28 81 28 78Z', 'orange')
    front += path('M44.5 57.5L48 53Q52 49 56 53L60 58.5L55.5 62L52 58.5L48.5 62Z', 'white')
    front += path('M50 81L70 63Q74 60 78 63L96 76Q96 81 91 81Z', 'olive')
    front += rect(30, 87, 26, 5, 2.5, 'cream-dark') + circle(92, 89.5, 3.5, 'orange')
    return s + group('rotate(-4 64 62)', front)


# --------------------------------------------------------------------------
def flower():
    """Photos pinwheel: eight folded clay blades around a button centre."""
    lit = 'M0 -5C-16 -11 -21 -29 -10 -39Q-5 -44 1 -42Z'      # trailing half, catches the light
    fold = 'M0 -5C13 -11 16 -29 6 -39Q3 -42 1 -42Z'          # leading half, tucked under the next blade
    colours = [('orange', 'orange-dark'), ('yellow', 'yellow-dark'), ('olive', 'olive-dark'), ('aqua', 'aqua-dark'),
               ('rose', 'orange-dark'), ('honey', 'gold'), ('mint', 'olive-dark'), ('sky', 'aqua-dark')]
    spin = lambda d, i: turn(d, i * 45, 63.5, 61, 1.06)
    s = ''.join(path(spin(fold, i), dark) for i, (_, dark) in enumerate(colours))
    s += ''.join(path(spin(lit, i), light) for i, (light, _) in enumerate(colours))
    s += circle(64.5, 62.5, 10, 'cream-dark') + circle(63.5, 61, 10, 'cream') + circle(63.5, 61, 4.8, 'yellow')
    return s


# --------------------------------------------------------------------------
def palette():
    """Painter's palette with a real thumb hole, five paints and a brush."""
    outline = 'M105 56C103 24 44 18 26 44C10 70 36 101 62 101C80 101 87 90 78 82C68 72 86 70 96 69Q106 68 105 56Z'
    hole = 'M44 70A8 8 0 1 0 44 86A8 8 0 1 0 44 70Z'
    s = group('translate(2 4)', path(outline, 'cream-dark'))
    s += path(outline + hole, 'cream', fill_rule='evenodd')
    for x, y, c, a in ((31, 57, 'rose', -60), (40, 41, 'orange', -40), (58, 32, 'yellow', -10),
                       (78, 34, 'olive', 20), (93, 48, 'aqua', 55)):
        s += ellipse(x, y, 8.5, 7, c, transform=f'rotate({a} {x} {y})')
    s += line('M86 84L103 100', ORANGE_D, 8) + line('M85 82L102 98', ORANGE, 7)       # brush handle
    s += line('M74 72L82 80', YELLOW, 9)                                             # ferrule
    s += path('M61 59Q63 55 69 61L79 71L72 78L63 69Q58 63 61 59Z', 'aqua-dark')       # loaded tip
    return group('translate(-6.5 -9.5) scale(1.09)', s)


# --------------------------------------------------------------------------
def paint():
    """Chunky artist's brush with brass ferrule laying down a fat aqua stroke."""
    s = line('M26 96.5Q47 103 70 96Q92 89.5 103 74.5', AQUA_D, 14)
    s += line('M25 94Q46 100.5 69 93.5Q91 87 102 72', AQUA, 14)
    s += circle(34, 36, 8.5, 'yellow') + circle(53, 23, 5.5, 'olive') + circle(22, 57, 5.5, 'orange')   # paint drops
    t = lambda d: turn(d, 45, 60, 62, 0.97)
    handle = 'M-6 -60Q0 -67 6 -60Q12 -36 10 -8H-10Q-12 -36 -6 -60Z'
    s += path(t(handle), 'orange-dark', transform='translate(2.5 3)')
    s += path(t(handle), 'orange')                                              # handle
    s += path(t(rr(-7.5, -55, 15, 6.5, 2.5)), 'cream')                           # end band
    s += path(t('M-12 6H12Q19 25 10 39Q4 46 0 54Q-4 46 -10 39Q-19 25 -12 6Z'), 'cream')   # bristles
    s += path(t('M-15.5 26Q-8 20 0 26Q8 32 15.5 26Q14 33 10 39Q4 46 0 54Q-4 46 -10 39Q-14 33 -15.5 26Z'), 'aqua')
    s += path(t(rr(-13.5, -14, 27, 25, 5)), 'yellow-dark', transform='translate(1.5 2.5)')
    s += path(t(rr(-13.5, -14, 27, 25, 5)), 'yellow')                            # ferrule
    s += path(t(rr(-13.5, -8, 27, 4.5, 2)), 'yellow-dark') + path(t(rr(-13.5, 1, 27, 4.5, 2)), 'yellow-dark')
    return s


# --------------------------------------------------------------------------
def font():
    """Slab-serif clay capital A and a small a standing on a baseline bar."""
    s = rect(19, 95, 91, 10, 5, 'cream-dark') + rect(16, 92, 91, 10, 5, 'cream')     # baseline bar
    s += ''.join(rect(x, 95, 4, 4, 2, 'olive') for x in (24, 40, 56, 72, 88))
    big, bar = 'M28 84L48 23L68 84', 'M36 65H60'
    s += group('translate(3 3)', line(big, ORANGE_D, 12), rect(18, 80, 22, 9, 3, 'orange-dark'),
               rect(56, 80, 22, 9, 3, 'orange-dark'))
    s += line(bar, ORANGE_D, 9, transform='translate(2 3)') + line(bar, ORANGE, 9)
    s += line(big, ORANGE, 12) + rect(18, 80, 22, 9, 3, 'orange') + rect(56, 80, 22, 9, 3, 'orange')
    s += circle(93, 75, 9, 'none', stroke=AQUA_D, stroke_width=8, transform='translate(2 2)')
    s += line('M104 64V85', AQUA_D, 8, transform='translate(2 2)')
    s += circle(93, 75, 9, 'none', stroke=AQUA, stroke_width=8) + line('M104 63V84', AQUA, 8)
    return s


ART = {'video': video, 'headphones': headphones, 'volume': volume, 'mic': mic, 'image': image,
       'flower': flower, 'palette': palette, 'paint': paint, 'font': font}
