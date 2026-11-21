"""Eduka-Icons 1.0 clay artwork: office documents and tools.

doc-writer, doc-draw, doc-math, doc-base, script, doc-audio, doc-image,
doc-video (one "document page" family: same sheet, folded corner and title
tab, each with its own accent colour and inner symbol), office-suite, editor
and charmap. Every function returns an SVG fragment on the 128 x 128 grid;
tools/clay.py sculpts each shape element separately. GPL-3.0.
"""
import math
import re
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_D = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_D, YELLOW, YELLOW_D = '#e0703a', '#b9552a', '#eec14f', '#cf9f33'
OLIVE, OLIVE_D = '#7d8c55', '#5f6c40'
AQUA, AQUA_D, CHARCOAL, ROSE = '#8fc0c4', '#6a9ea3', '#3f3c37', '#d98a7a'

_TOKEN = re.compile(r'[MLQCZ]|-?\d*\.?\d+')


class Tilt:
    """Rotate/scale geometry (not the element) so light and shadow keep one direction.

    Path data may only use absolute M L Q C Z, i.e. plain coordinate pairs.
    """

    def __init__(self, degrees=0, cx=64, cy=62, scale=1, dx=0, dy=0):
        a = math.radians(degrees)
        self.c, self.s, self.cx, self.cy = math.cos(a), math.sin(a), cx, cy
        self.k, self.ox, self.oy = scale, dx, dy

    def xy(self, x, y):
        dx, dy = (x - self.cx) * self.k, (y - self.cy) * self.k
        return (self.cx + self.ox + dx * self.c - dy * self.s,
                self.cy + self.oy + dx * self.s + dy * self.c)

    def d(self, data):
        out, pair = [], []
        for token in _TOKEN.findall(data):
            if token in 'MLQCZ':
                out.append(token)
                continue
            pair.append(float(token))
            if len(pair) == 2:
                out.append('%.2f %.2f ' % self.xy(*pair))
                pair = []
        return ''.join(out)

    def path(self, data, c, **kw):
        return path(self.d(data), c, **kw)

    def rr(self, x, y, w, h, r, c, **kw):
        return self.path(_round_rect(x, y, w, h, r), c, **kw)

    def circ(self, x, y, r, c, **kw):
        px, py = self.xy(x, y)
        return circle(round(px, 2), round(py, 2), round(r * self.k, 2), c, **kw)

    def ln(self, data, colour, width, **kw):
        return line(self.d(data), colour, round(width * self.k, 2), **kw)


FLAT = Tilt()


def _round_rect(x, y, w, h, r):
    return (f'M{x + r} {y}L{x + w - r} {y}Q{x + w} {y} {x + w} {y + r}L{x + w} {y + h - r}'
            f'Q{x + w} {y + h} {x + w - r} {y + h}L{x + r} {y + h}Q{x} {y + h} {x} {y + h - r}'
            f'L{x} {y + r}Q{x} {y} {x + r} {y}Z')


def ellipse(cx, cy, rx, ry, c, **kw):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    fill = c if c == 'none' or c.startswith('#') else f'url(#{c})'
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'


# --------------------------------------------------------------------------
# The shared sheet: 70 x 85 with a 20 unit dog-ear, drawn at x 27..97, y 16..101.
SHEET = 'M36 16L77 16L97 36L97 92Q97 101 88 101L36 101Q27 101 27 92L27 25Q27 16 36 16Z'
EAR = 'M77 16L77 30Q77 36 83 36L97 36Z'


def sheet(accent, t=FLAT, face='cream', side='cream-dark', tab=True, depth=4.5):
    """Thick clay page with an accent coloured dog-ear and title tab."""
    under = Tilt(0, dx=0, dy=depth)
    s = path(under.d(t.d(SHEET)), side)
    s += t.path(SHEET, face)
    s += t.path(EAR, accent)
    if tab:
        s += t.rr(35, 25, 30, 8, 4, accent)
    return s


def thick(shape, dark, light, dx=1.5, dy=2.5):
    """A clay slab: the dark copy peeks out below/right of the lit face."""
    return f'<g transform="translate({dx} {dy})">{shape(dark)}</g>' + shape(light)


# --------------------------------------------------------------------------
def doc_writer():
    """Text document: aqua tab, aqua text lines and a quill pen."""
    s = sheet('aqua')
    s += line('M37 46.5H87M37 60.5H80M37 74.5H64M37 88.5H52', AQUA_D, 5.5)
    # quill: notched two-tone vane, cream shaft, dark nib
    vane = 'C101.5 51 99.5 59 96 66L89.5 65.5L92.5 72C87.5 80 80 86 71 90Z'
    s += path('M66 87C62 66 78 47 100 43' + vane, 'aqua-dark', transform='translate(1.5 2.5)')
    s += path('M66 87C62 66 78 47 100 43' + vane, 'aqua')
    s += path('M69 88L100 43' + vane, 'aqua-dark')
    s += line('M61 95L95 50', WHITE, 4)
    s += line('M57 100L63 92', CHARCOAL, 4.6)
    return s


# --------------------------------------------------------------------------
def doc_draw():
    """Drawing document: yellow tab, orange circle, aqua square, yellow triangle."""
    s = sheet('yellow')
    s += circle(49, 58, 13, 'orange-dark') + circle(48, 56, 13, 'orange')
    s += rect(63, 49, 25, 25, 6, 'aqua-dark') + rect(62, 47, 25, 25, 6, 'aqua')
    tri = 'M40 94Q36 94 38.5 90L55 65Q58 61 61 65L77.5 90Q80 94 76 94Z'
    s += path(tri, 'yellow-dark', transform='translate(1.5 2.5)') + path(tri, 'yellow')
    return s


# --------------------------------------------------------------------------
def doc_math():
    """Formula document: olive tab, clay square root over an orange x."""
    s = sheet('olive')
    root = 'M35 70L42 68L51 90L61 47H89'
    s += line(root, OLIVE_D, 7.5, transform='translate(1.2 2.4)') + line(root, OLIVE, 7.5)
    cross = 'M68 61L84 81M84 61L68 81'
    s += line(cross, ORANGE_D, 6.5, transform='translate(1 2)') + line(cross, ORANGE, 6.5)
    return s


# --------------------------------------------------------------------------
def doc_base():
    """Database document: orange tab, three stacked orange drums."""
    s = sheet('orange')
    cx, rx, ry, h = 62, 25, 8, 9.5
    for top in (79, 64, 49):
        s += path(f'M{cx - rx} {top}V{top + h}A{rx} {ry} 0 0 0 {cx + rx} {top + h}V{top}Z', 'orange-dark',
                  transform='translate(0 2)')
        s += path(f'M{cx - rx} {top}V{top + h}A{rx} {ry} 0 0 0 {cx + rx} {top + h}V{top}Z', 'orange')
        s += ellipse(cx, top, rx, ry, 'orange')
        s += circle(cx - 14, top + h + 1.5, 2.6, 'yellow')
    s += ellipse(cx, 49, 15, 4.4, 'cream')
    return s


# --------------------------------------------------------------------------
def script():
    """Code file: charcoal tab, clay angle brackets and an orange slash."""
    s = sheet('charcoal')
    brackets = 'M51 53L37 68L51 83M73 53L87 68L73 83'
    s += line(brackets, '#2b2925', 7.5, transform='translate(1 2.2)') + line(brackets, CHARCOAL, 7.5)
    s += line('M67 49L57 87', ORANGE_D, 7, transform='translate(1 2.2)') + line('M67 49L57 87', ORANGE, 7)
    return s


# --------------------------------------------------------------------------
def doc_audio():
    """Audio file: rose tab and a beamed pair of clay notes."""
    s = sheet('rose')

    def note(c):
        return (path('M51 49L85 42L85 54L51 61Z', c)
                + rect(51, 50, 6.5, 36, 3, c) + rect(78.5, 44, 6.5, 34, 3, c)
                + ellipse(47, 85, 10.5, 8, c, transform='rotate(-18 47 85)')
                + ellipse(74.5, 78, 10.5, 8, c, transform='rotate(-18 74.5 78)'))
    s += f'<g transform="translate(1.5 2.5)">{note("orange-dark")}</g>' + note('rose')
    return s


# --------------------------------------------------------------------------
def doc_image():
    """Image file: page with a framed landscape (sky, sun, two hills)."""
    s = sheet('aqua-dark')
    s += rect(35, 46, 54, 46, 6, 'cream-dark') + rect(34, 44, 54, 46, 6, 'white')
    s += rect(38.5, 48.5, 45, 37, 3.5, 'aqua')
    s += circle(73, 58.5, 5.5, 'yellow')
    s += rect(43, 53.5, 15, 5.5, 2.75, 'white')
    s += path('M38.5 76L50 61Q53 57.5 56 61L72 85.5H42Q38.5 85.5 38.5 82Z', 'olive')
    s += path('M56 85.5L68 73Q71 70.5 74 73L83.5 80V82Q83.5 85.5 80 85.5Z', 'olive-dark')
    return s


# --------------------------------------------------------------------------
def doc_video():
    """Video file: page with a film frame and a play triangle."""
    s = sheet('orange')
    s += rect(35, 45, 56, 48, 6, 'ink') + rect(34, 43, 56, 48, 6, 'charcoal')
    for i in range(5):
        x = 38 + i * 10.5
        s += rect(x, 46.5, 6, 5, 1.5, 'cream') + rect(x, 82.5, 6, 5, 1.5, 'cream')
    s += rect(38, 55, 48, 24, 3, 'orange')
    s += path('M56.5 60Q56.5 58 58.5 59L70 65.5Q72 67 70 68.5L58.5 75Q56.5 76 56.5 74Z', 'white')
    return s


# --------------------------------------------------------------------------
def office_suite():
    """Start centre: a fan of three pages (aqua text, olive table, cream chart)."""
    left = Tilt(-22, 62, 58.5, .76, -9, -1)
    right = Tilt(22, 62, 58.5, .76, 11, -1)
    front = Tilt(0, 62, 101, .82, 1, 1)
    s = sheet('cream', left, 'aqua', 'aqua-dark', tab=False, depth=3.5)
    s += left.ln('M37 34L62 34M37 50L88 50M37 66L88 66M37 82L88 82', WHITE, 5.5)
    s += sheet('cream', right, 'olive', 'olive-dark', tab=False, depth=3.5)
    s += right.ln('M36 48L89 48M36 64L89 64M36 80L89 80M77 40L77 92', CREAM, 5.5)
    s += sheet('orange', front, depth=4)
    # chart on the front page
    s += front.circ(50, 62, 14.5, 'orange-dark', transform='translate(1 2)')
    s += front.circ(50, 62, 14.5, 'orange')
    s += front.path('M50 62L50 47.5Q64.5 47.5 64.5 62Z', 'yellow')
    s += front.ln('M73 54L88 54M73 66L84 66', OLIVE, 5.5)
    s += front.ln('M37 86L87 86', AQUA_D, 5.5)
    return s


# --------------------------------------------------------------------------
def editor():
    """Plain text editor: clipboard with a notepad page, caret and pencil."""
    s = rect(20, 25, 78, 81, 10, 'olive-dark') + rect(20, 21, 78, 81, 10, 'olive')
    s += rect(27, 33, 64, 64, 5, 'cream-dark') + rect(27, 30, 64, 64, 5, 'white')
    # clip
    s += rect(42, 18, 34, 15, 5, 'yellow-dark') + rect(42, 16, 34, 15, 5, 'yellow')
    s += circle(59, 23, 3.4, 'olive-dark')
    # text and caret
    s += line('M35 46.5H64M35 60.5H51M35 74.5H68M35 86H54', OLIVE, 5)
    s += line('M59.5 54V67M56 53H63M56 68H63', ORANGE, 4)
    # pencil
    p = Tilt(40, 80, 76)
    s += p.rr(74, 46, 12, 34, 2, 'orange-dark', transform='translate(1.5 2.5)')
    s += p.rr(74, 40, 12, 9, 4, 'rose')
    s += p.rr(74, 46, 12, 6, 1, 'yellow')
    s += p.rr(74, 51, 12, 30, 1, 'orange')
    s += p.path('M74 81L86 81L80 95Z', 'sand')
    s += p.path('M77.5 89L82.5 89L80 95Z', 'charcoal')
    return s


# --------------------------------------------------------------------------
def charmap():
    """Character map: cream slab with four tiles (omega, star, heart, ampersand)."""
    s = rect(18, 21, 90, 85, 12, 'cream-dark') + rect(18, 16, 90, 85, 12, 'cream')
    for x, y, c in ((25, 23, 'white'), (66, 23, 'white'), (25, 62, 'white'), (66, 62, 'aqua-dark')):
        s += rect(x, y + 2.5, 35, 32, 7, '#4f7d82' if c == 'aqua-dark' else 'cream-dark') + rect(x, y, 35, 32, 7, c)
    # omega
    cx, cy = 42.5, 39
    s += line(f'M{cx - 10} {cy + 9}H{cx - 4}C{cx - 13} {cy + 2} {cx - 11} {cy - 10} {cx} {cy - 10}'
              f'C{cx + 11} {cy - 10} {cx + 13} {cy + 2} {cx + 4} {cy + 9}H{cx + 10}', OLIVE_D, 4.6)
    # star
    cx, cy = 83.5, 39.5
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 11.5 if i % 2 == 0 else 5.2
        pts.append(f'{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}')
    s += path('M' + 'L'.join(pts) + 'Z', 'yellow', stroke=YELLOW, stroke_width=2.4, stroke_linejoin='round')
    # heart
    cx, cy = 42.5, 78.5
    s += path(f'M{cx} {cy + 10}C{cx - 4} {cy + 7} {cx - 12} {cy + 2} {cx - 12} {cy - 4}'
              f'C{cx - 12} {cy - 9} {cx - 8} {cy - 11} {cx - 5.5} {cy - 11}C{cx - 3} {cy - 11} {cx - 1} {cy - 9.5} {cx} {cy - 7}'
              f'C{cx + 1} {cy - 9.5} {cx + 3} {cy - 11} {cx + 5.5} {cy - 11}C{cx + 8} {cy - 11} {cx + 12} {cy - 9} {cx + 12} {cy - 4}'
              f'C{cx + 12} {cy + 2} {cx + 4} {cy + 7} {cx} {cy + 10}Z', 'orange')
    # ampersand
    cx, cy = 83.5, 78
    s += line(f'M{cx + 9} {cy + 10}L{cx - 5} {cy - 4}C{cx - 9} {cy - 9} {cx + 3} {cy - 13} {cx + 3} {cy - 6}'
              f'C{cx + 3} {cy - 1} {cx - 9} {cy} {cx - 8} {cy + 6}C{cx - 7} {cy + 11} {cx + 4} {cy + 11} {cx + 9} {cy}', WHITE, 4.6)
    return s


ART = {
    'doc-writer': doc_writer,
    'doc-draw': doc_draw,
    'doc-math': doc_math,
    'doc-base': doc_base,
    'script': script,
    'doc-audio': doc_audio,
    'doc-image': doc_image,
    'doc-video': doc_video,
    'office-suite': office_suite,
    'editor': editor,
    'charmap': charmap,
}
