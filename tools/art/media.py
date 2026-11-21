"""Eduka-Icons 1.0 clay artwork: media group.

video, headphones, volume, mic, image, flower, palette, paint, font.
Every function returns an SVG fragment on the 128 x 128 grid; tools/clay.py
sculpts each shape element separately. GPL-3.0.
"""
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


# --------------------------------------------------------------------------
def video():
    """Clapperboard with an open striped arm and a big play button."""
    def stripes(y, h):
        return ''.join(path(f'M{x} {y}H{x + 10}L{x + 4} {y + h}H{x - 6}Z', 'cream') for x in (38, 60, 82))
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
    s = rect(41, 96, 48, 10, 5, 'olive-dark')
    s += rect(39, 93, 48, 10, 5, 'olive')                         # foot
    s += rect(59, 84, 10, 12, 3, 'cream-dark')                    # stem
    s += line('M36 54V60Q36 86 64 86Q92 86 92 60V54', OLIVE_D, 8)
    s += line('M35 52V58Q35 84 64 84Q93 84 93 58V52', OLIVE, 8)   # cradle
    s += rect(46, 19, 40, 57, 20, 'cream-dark')
    s += rect(44, 16, 40, 57, 20, 'cream')                        # body
    s += path('M44 46V36Q44 16 64 16Q84 16 84 36V46Z', 'orange')  # grille head
    s += line('M54 26H74M51 35H77', ORANGE_D, 4)
    s += rect(42, 43, 44, 8, 4, 'yellow')                         # ring
    s += rect(60, 56, 8, 12, 4, 'olive') + circle(64, 60, 2.6, 'yellow')
    s += circle(34.5, 53, 5, 'yellow') + circle(93.5, 53, 5, 'yellow')    # pivots
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
    spin = 'translate(63 61) rotate({}) scale(1.04)'
    s = ''.join(group(spin.format(i * 45), path(fold, dark)) for i, (_, dark) in enumerate(colours))
    s += ''.join(group(spin.format(i * 45), path(lit, light)) for i, (light, _) in enumerate(colours))
    s += circle(64, 62.5, 9.5, 'cream-dark') + circle(63, 61, 9.5, 'cream') + circle(63, 61, 4.5, 'yellow')
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
    return group('translate(0 -4)', s)


# --------------------------------------------------------------------------
def paint():
    """Big paint brush with brass ferrule laying down an aqua stroke."""
    s = line('M25 91Q40 104 66 97Q88 91 102 78', AQUA_D, 12)
    s += line('M24 88Q40 100 65 93Q87 87 101 75', AQUA, 12)
    s += circle(33, 38, 7, 'yellow') + circle(48, 26, 4.5, 'olive') + circle(24, 58, 4.5, 'orange')   # paint drops
    brush = path('M-5 -58Q0 -64 5 -58L8 -12H-8Z', 'orange-dark', transform='translate(2 3)')
    brush += path('M-5 -58Q0 -64 5 -58L8 -12H-8Z', 'orange')                        # handle
    brush += rect(-5.5, -52, 11, 6, 2, 'cream')                                    # end band
    brush += path('M-9 6H9Q14 22 7 34Q3 40 0 45Q-3 40 -7 34Q-14 22 -9 6Z', 'cream')  # bristles
    brush += path('M-11.5 21Q-6 17 0 21Q6 25 11.5 21Q11 29 7 34Q3 40 0 45Q-3 40 -7 34Q-11 29 -11.5 21Z', 'aqua')
    brush += rect(-10, -14, 20, 23, 4, 'yellow')                                   # ferrule
    brush += rect(-10, -8, 20, 3.5, 1.5, 'yellow-dark') + rect(-10, 0, 20, 3.5, 1.5, 'yellow-dark')
    return s + group('translate(58 64) rotate(42)', brush)


# --------------------------------------------------------------------------
def font():
    """Slab-serif clay capital A and a small a standing on a baseline bar."""
    s = rect(19, 95, 91, 10, 5, 'cream-dark') + rect(16, 92, 91, 10, 5, 'cream')     # baseline bar
    s += ''.join(rect(x, 95, 4, 4, 2, 'olive') for x in (24, 40, 56, 72, 88))
    big, bar = 'M28 84L48 27L68 84', 'M36 66H60'
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
