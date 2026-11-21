"""Eduka-Icons 1.0 clay artwork: Eduka-Desktop suite launchers and file sheets.

Suite launchers (eduka-menu, eduka-panel, eduka-settings, eduka-about,
eduka-desktop, eduka-session, eduka-welcome, eduka-appstore-tile) share cream
slabs, the olive/orange brand backpack and round clay buttons.

The neutral and special file sheets reuse the document page of art/office.py
(same sheet, dog-ear and thickness); each one has its own accent colour and a
single bold symbol so that they stay apart at 24 px. Every function returns an
SVG fragment on the 128 x 128 grid. GPL-3.0.
"""
import math
from artwork import path, rect, circle, line
from .office import Tilt, FLAT, SHEET, EAR, sheet, thick, ellipse

CREAM, WHITE, CREAM_D = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_D, YELLOW, YELLOW_D = '#e0703a', '#b9552a', '#eec14f', '#cf9f33'
OLIVE, OLIVE_D = '#7d8c55', '#5f6c40'
AQUA, AQUA_D, CHARCOAL, ROSE, STONE = '#8fc0c4', '#6a9ea3', '#3f3c37', '#d98a7a', '#9a9c8b'
HEX = {'cream': CREAM, 'white': WHITE, 'cream-dark': CREAM_D, 'orange': ORANGE, 'orange-dark': ORANGE_D,
       'yellow': YELLOW, 'yellow-dark': YELLOW_D, 'olive': OLIVE, 'olive-dark': OLIVE_D, 'aqua': AQUA,
       'aqua-dark': AQUA_D, 'charcoal': CHARCOAL, 'rose': ROSE, 'stone': STONE, 'ivory': '#f0e2c4',
       'sand': '#e6d3ad', 'ink': '#49453e'}
DARK = {'cream': 'cream-dark', 'white': 'cream-dark', 'orange': 'orange-dark', 'yellow': 'yellow-dark',
        'olive': 'olive-dark', 'aqua': 'aqua-dark', 'rose': 'orange-dark', 'charcoal': 'ink',
        'ivory': 'cream-dark', 'stone': 'olive-dark', 'aqua-dark': 'aqua-dark', 'olive-dark': 'olive-dark'}


# --------------------------------------------------------------------------
# small shared parts
def soft(d, c, w=3, **kw):
    """Filled shape whose corners are rounded by a stroke of its own colour."""
    return path(d, c, stroke=HEX[c], stroke_width=w, stroke_linejoin='round', **kw)


def slab(shape, c, dx=1.5, dy=2.5):
    """shape(colour) twice: the darker copy peeks out below/right of the lit face."""
    return thick(shape, DARK[c], c, dx, dy)


def tile(x, y, s, c, r=None, depth=2.5):
    r = s * .28 if r is None else r
    return rect(x, y + depth, s, s, r, DARK[c]) + rect(x, y, s, s, r, c)


def dashed(d, colour, width, dash, **kw):
    return path(d, 'none', stroke=colour, stroke_width=width, stroke_dasharray=dash,
                stroke_linecap='round', stroke_linejoin='round', **kw)


def gear_d(cx, cy, outer, root, teeth, turn=0.0):
    pts = []
    step = math.pi / teeth
    for i in range(teeth):
        a = turn + 2 * step * i
        for radius, da in ((root, -.60), (outer, -.34), (outer, .34), (root, .60)):
            pts.append(f'{cx + radius * math.cos(a + da * step):.2f} {cy + radius * math.sin(a + da * step):.2f}')
    return 'M' + 'L'.join(pts) + 'Z'


def gear(cx, cy, outer, c, side, hub, teeth=8, depth=2.4, dot=None):
    d = gear_d(cx, cy, outer, outer * .74, teeth, math.pi / teeth)
    s = soft(d, side, max(2.4, outer * .16), transform=f'translate(1.2 {depth})') + soft(d, c, max(2.4, outer * .16))
    s += circle(cx, cy, round(outer * .42, 2), hub)
    if dot:
        s += circle(cx, cy, round(outer * .17, 2), dot)
    return s


def sparkle(x, y, r, c='yellow'):
    k = r * .2
    return path(f'M{x} {y - r}Q{x + k} {y - k} {x + r} {y}Q{x + k} {y + k} {x} {y + r}'
                f'Q{x - k} {y + k} {x - r} {y}Q{x - k} {y - k} {x} {y - r}Z', c)


def backpack(cx, cy, k=1.0, pockets=True):
    """Simplified brand backpack (about 52 x 62 units at k=1, centred on cx, cy)."""
    t = Tilt(0, 0, 0, k, cx, cy)
    s = t.ln('M-7 -25C-7 -37 7 -37 7 -25', YELLOW, 4.6)
    if pockets:
        s += t.rr(-26, 1, 10, 20, 4, 'orange') + t.rr(16, 1, 10, 20, 4, 'orange')
    s += t.rr(-21, -23, 42, 52, 12, 'olive-dark')
    s += t.rr(-21, -26, 42, 50, 12, 'olive')
    s += t.path('M-21 -14Q-21 -26 -9 -26L9 -26Q21 -26 21 -14L21 -9Q21 -3 15 -3L-15 -3Q-21 -3 -21 -9Z', 'cream')
    s += t.rr(-3, -7, 6, 12, 2.5, 'olive-dark')
    s += t.rr(-14, 3, 28, 17, 6, 'orange')
    s += t.circ(0, 4.5, 3.3, 'yellow')
    return s


# --------------------------------------------------------------------------
# suite launchers
def eduka_menu():
    """Start menu: cream launcher panel, search bar and six colourful app tiles."""
    s = rect(18, 21, 92, 84, 13, 'cream-dark') + rect(18, 16, 92, 84, 13, 'cream')
    s += rect(25, 23, 78, 15, 7.5, 'cream-dark') + rect(25, 22, 78, 14.5, 7.2, 'white')
    s += circle(34.5, 28.6, 3.6, 'none', stroke=AQUA_D, stroke_width=3)
    s += line('M37.6 31.6L40.4 34', AQUA_D, 3) + line('M47 29.2H72', CREAM_D, 4)
    colours = ('orange', 'yellow', 'olive', 'aqua', 'rose', 'olive-dark')
    for i, c in enumerate(colours):
        s += tile(25 + 28 * (i % 3), 43 + 27 * (i // 3), 22, c)
    # a tiny cream mark on every tile: six different "apps"
    s += circle(36, 54, 4.4, 'white')
    s += rect(59.5, 49.5, 9, 9, 2.6, 'white')
    s += soft('M89 50.5L96 54L89 57.5Z', 'white', 2)
    s += line('M31.5 78H40.5M31.5 84H37', WHITE, 3.2)
    s += line('M64 76.5V85.5M59.5 81H68.5', WHITE, 3.2)
    s += circle(92, 81, 4.4, 'yellow')
    return s


def eduka_panel():
    """Desktop panel: a fat taskbar (start button, tasks, tray) docked under a screen."""
    s = rect(22, 21, 84, 62, 11, 'cream-dark') + rect(22, 17, 84, 62, 11, 'cream')
    s += rect(27, 22, 74, 48, 7, 'aqua')
    s += circle(84, 35, 6, 'yellow')
    s += path('M27 57Q42 41 58 53Q72 63 86 51Q94 45 101 49V63Q101 70 94 70H34Q27 70 27 63Z', 'olive')
    s += rect(16, 72, 94, 32, 14, 'cream-dark') + rect(16, 68, 94, 32, 14, 'cream')
    s += rect(21, 73, 84, 22, 10, 'charcoal')
    s += circle(33, 84, 7.6, 'orange') + circle(33, 84, 2.8, 'cream')
    for x, c in ((45.5, 'cream'), (59.5, 'cream'), (73.5, 'aqua')):
        s += rect(x, 78.5, 11, 11, 3.5, c)
    s += circle(91.5, 84, 2.8, 'yellow') + circle(98.5, 84, 2.8, 'olive')
    return s


def eduka_settings():
    """Suite settings: a window with clay sliders, a toggle and a small gear."""
    s = rect(16, 23, 88, 80, 12, 'cream-dark') + rect(16, 18, 88, 80, 12, 'cream')
    s += path('M28 18H92Q104 18 104 30V35H16V30Q16 18 28 18Z', 'olive')
    s += circle(27, 26.5, 3.2, 'orange') + circle(37, 26.5, 3.2, 'yellow') + circle(47, 26.5, 3.2, 'cream')
    s += line('M27 48H93', CREAM_D, 6) + line('M27 48H62', AQUA_D, 6) + circle(63, 48, 7, 'aqua-dark') + circle(63, 48, 6.4, 'white')
    s += line('M27 64H66', CREAM_D, 6) + line('M27 64H40', ORANGE, 6) + circle(42, 64, 7, 'orange-dark') + circle(42, 64, 6.4, 'orange')
    s += rect(24, 75, 27, 14, 7, 'olive') + circle(43.5, 82, 5, 'white')
    s += gear(87, 83, 20, 'ivory', 'olive-dark', 'yellow', dot='orange')
    return s


def eduka_about():
    """About dialog: info card with the brand backpack and a round "i" badge."""
    s = rect(16, 27, 90, 78, 12, 'cream-dark') + rect(16, 22, 90, 78, 12, 'cream')
    s += backpack(44, 63, .84)
    s += line('M73 57H96M73 68H96', OLIVE, 5) + rect(72, 78, 25, 10, 5, 'orange')
    s += circle(93, 33, 15, 'aqua-dark') + circle(92, 31, 15, 'aqua')
    s += circle(92, 24, 3, 'white') + rect(89.3, 29, 5.4, 12, 2.7, 'white')
    return s


def eduka_desktop():
    """The desktop: monitor with wallpaper hill, a panel bar and two desktop icons."""
    s = rect(54, 84, 20, 15, 4, 'olive-dark')
    s += rect(38, 97, 52, 9, 4.5, 'olive-dark') + rect(38, 94, 52, 9, 4.5, 'olive')
    s += rect(16, 20, 94, 70, 12, 'cream-dark') + rect(16, 16, 94, 70, 12, 'cream')
    s += rect(21, 21, 84, 60, 8, 'charcoal') + rect(23.5, 23.5, 79, 55, 6, 'aqua')
    s += circle(85, 37, 6, 'yellow')
    s += path('M23.5 60Q40 44 58 56Q72 66 86 53Q95 46 102.5 51V70H23.5Z', 'olive')
    s += path('M23.5 67.5H102.5V72.5Q102.5 78.5 96.5 78.5H29.5Q23.5 78.5 23.5 72.5Z', 'cream')
    s += circle(30.5, 73, 3, 'orange') + rect(37.5, 70.4, 5.4, 5.4, 1.6, 'olive') + rect(45.5, 70.4, 5.4, 5.4, 1.6, 'aqua-dark')
    s += circle(95.5, 73, 2.4, 'olive')
    s += rect(29, 28.5, 11, 10, 3, 'orange') + rect(29, 43, 11, 10, 3, 'white')
    return s


def eduka_session():
    """Session dialog: card with an avatar and power, restart and lock buttons."""
    s = rect(16, 34, 94, 70, 13, 'cream-dark') + rect(16, 30, 94, 70, 13, 'cream')
    s += circle(63, 33, 15, 'cream-dark') + circle(63, 31, 15, 'cream') + circle(63, 31, 11.5, 'aqua')
    s += circle(63, 27.5, 4.4, 'white') + path('M54.6 38.5Q56.5 32.6 63 32.6Q69.5 32.6 71.4 38.5Q67.5 42.5 63 42.5Q58.5 42.5 54.6 38.5Z', 'white')
    s += line('M50 54H76', CREAM_D, 5)
    for x, c in ((36, 'orange'), (63, 'yellow'), (90, 'olive')):
        s += circle(x, 80, 13, DARK[c]) + circle(x, 77, 13, c)
    s += path('M31.4 73.4A6.6 6.6 0 1 0 40.6 73.4', 'none', stroke=WHITE, stroke_width=3.8, stroke_linecap='round')
    s += line('M36 69.5V77', WHITE, 3.8)
    s += path('M69.4 78.6A6.6 6.6 0 1 1 66.4 71.4', 'none', stroke=WHITE, stroke_width=3.8, stroke_linecap='round')
    s += soft('M70.6 67.6V75.2H63Z', 'white', 1.8)
    s += path('M86 76V73.2A4 4 0 0 1 94 73.2V76', 'none', stroke=WHITE, stroke_width=3.4, stroke_linecap='round')
    s += rect(83.6, 75.4, 12.8, 10, 3, 'white')
    return s


def eduka_welcome():
    """Welcome: the brand backpack popping out of an open gift box, with sparkles."""
    s = rect(25, 62, 78, 18, 7, 'cream-dark')
    s += backpack(64, 51, .88)
    s += path('M24 74H104V95Q104 104 95 104H33Q24 104 24 95Z', 'cream')
    s += rect(18, 70.5, 92, 14, 6, 'cream-dark') + rect(18, 68, 92, 14, 6, 'cream')
    s += rect(56.5, 68, 15, 36, 2, 'orange')
    s += circle(38, 93, 3.2, 'yellow') + circle(90, 93, 3.2, 'aqua')
    s += sparkle(26, 33, 10) + sparkle(102, 28, 8) + circle(105, 50, 3.4, 'orange') + circle(21, 54, 3, 'aqua')
    return s


def eduka_appstore_tile():
    """All applications: nine clay tiles in a 3 x 3 grid, the centre one marked."""
    colours = ('orange', 'yellow', 'aqua', 'olive', 'cream', 'orange', 'aqua', 'olive', 'yellow')
    s = ''
    for i, c in enumerate(colours):
        s += tile(17 + 31.5 * (i % 3), 16 + 31 * (i // 3), 25, c, 7)
    s += circle(61, 59.5, 6.2, 'yellow') + circle(61, 59.5, 2.6, 'orange')
    return s


# --------------------------------------------------------------------------
# neutral and special file sheets
def blank_file():
    """Unknown/binary file: empty page with a quiet dotted block pattern."""
    s = sheet('sand', tab=False)
    for y, dash in ((40, '9 8 .1 8'), (52, '.1 8 14 8 .1 8'), (64, '6 8 .1 8 .1 8'), (76, '.1 8 .1 8 11 8'), (88, '8 8 .1 8')):
        s += dashed(f'M38 {y}H{84 if y > 40 else 66}', CREAM_D, 5, dash)
    return s


def symlink_file():
    """Symbolic link: page with a curved link arrow leaving a small origin dot."""
    s = sheet('aqua')
    shaft, head = 'M41 90C41 70 52 60 72 60', 'M70 46L90 60L70 74Z'
    s += (f'<g transform="translate(1.4 2.6)">{line(shaft, "#4f8187", 9)}'
          f'{path(head, "aqua-dark", stroke="#4f8187", stroke_width=3, stroke_linejoin="round")}</g>')
    s += line(shaft, AQUA_D, 9) + soft(head, 'aqua-dark', 3)
    s += circle(41, 90, 6.5, 'orange')
    return s


def device_file():
    """Device node: page with a clay chip (yellow pins, aqua core)."""
    s = sheet('stone')
    s += line('M52 45V93M62 45V93M72 45V93M38 59H86M38 69H86M38 79H86', YELLOW, 4.2)
    s += rect(45, 54.5, 34, 34, 7, 'ink') + rect(45, 52, 34, 34, 7, 'charcoal')
    s += rect(54, 61, 16, 16, 4, 'aqua') + circle(51, 58, 2.2, 'yellow')
    return s


def pipe_file():
    """Named pipe (FIFO): page with a clay pipe elbow, flanges and a coupling."""
    s = sheet('olive')
    tube = 'M38 54H62Q76 54 76 68V92'
    s += path(tube, 'none', stroke=OLIVE_D, stroke_width=16, transform='translate(1.2 2.4)')
    s += path(tube, 'none', stroke=OLIVE, stroke_width=16)
    s += rect(34, 43, 8, 22.5, 3, 'yellow') + rect(64.5, 87.5, 23, 8, 3, 'yellow')
    s += rect(51, 45, 6.5, 18.5, 2.5, 'orange') + rect(66.5, 71, 19, 6.5, 2.5, 'orange')
    return s


def socket_file():
    """Socket: page with a two-pin clay plug and its cord."""
    s = sheet('orange')
    s += line('M62 80C62 96 46 84 39 93', CHARCOAL, 5)
    s += rect(53, 42, 5.5, 16, 2, 'metal') + rect(66, 42, 5.5, 16, 2, 'metal')
    s += rect(45, 56.5, 34, 22, 8, 'orange-dark') + rect(45, 54, 34, 22, 8, 'orange')
    s += rect(55, 74, 14, 10, 3.5, 'orange-dark')
    s += line('M53 65H71', WHITE, 4)
    return s


def certificate_file():
    """Certificate: page with text lines, a wax seal rosette and two ribbon tails."""
    s = sheet('yellow')
    s += line('M37 46H86M37 56H72', CREAM_D, 5)
    s += path('M56 80L50 98L58 95L62 100L67 83Z', 'orange-dark') + path('M78 80L84 98L76 95L72 100L67 83Z', 'orange-dark')
    pts = []
    for i in range(20):
        a = i * math.pi / 10
        r = 15.5 if i % 2 == 0 else 12.6
        pts.append(f'{67 + r * math.cos(a):.2f} {75 + r * math.sin(a):.2f}')
    rosette = 'M' + 'L'.join(pts) + 'Z'
    s += soft(rosette, 'orange-dark', 2.4, transform='translate(1.2 2.2)') + soft(rosette, 'orange', 2.4)
    s += circle(67, 75, 7.5, 'yellow')
    return s


def key_file():
    """Key file: page with a chunky clay key."""
    s = sheet('yellow-dark')
    t = Tilt(-40, 62, 68, 1, 0, 1)

    def key(c):
        return (t.rr(52, 64.2, 40, 7.6, 3, c) + t.rr(74, 68, 6, 11, 2, c) + t.rr(84, 68, 6, 8.5, 2, c)
                + t.circ(42, 68, 13.5, c))
    s += f'<g transform="translate(1.5 2.6)">{key("yellow-dark")}</g>' + key('yellow')
    s += t.circ(38.5, 68, 4.6, 'cream')
    return s


def template_file():
    """Template: page whose title and blocks are dashed placeholders."""
    s = sheet('aqua', tab=False)
    s += dashed('M39 29H61', AQUA_D, 5, '.1 9.3')
    box = lambda x, y, w, h, r=4: f'M{x + r} {y}H{x + w - r}Q{x + w} {y} {x + w} {y + r}V{y + h - r}Q{x + w} {y + h} {x + w - r} {y + h}H{x + r}Q{x} {y + h} {x} {y + h - r}V{y + r}Q{x} {y} {x + r} {y}Z'
    s += dashed(box(36, 42, 52, 24), AQUA_D, 4, '6 5.2')
    s += dashed(box(36, 73, 22, 20), AQUA_D, 4, '6 5.2') + dashed(box(66, 73, 22, 20), AQUA_D, 4, '6 5.2')
    s += line('M62 49V59M57 54H67', ORANGE, 4)
    return s


def log_file():
    """Log file: page with stacked entries and a small clock."""
    s = sheet('olive-dark')
    for y, x1 in ((46, 86), (57, 78), (68, 56), (79, 50), (90, 46)):
        s += circle(38.5, y, 2.6, 'orange') + line(f'M46 {y}H{x1}', OLIVE_D, 4.6)
    s += circle(76, 83, 14.5, 'olive-dark') + circle(75, 81, 14.5, 'olive') + circle(75, 81, 10.5, 'white')
    s += line('M75 74.5V81L79.5 84', ORANGE, 3.4)
    return s


def config_file():
    """Configuration file: page with three sliders and a small gear."""
    s = sheet('stone')
    for y, x, c in ((47, 70, 'orange'), (61, 48, 'yellow'), (75, 44, 'aqua')):
        x1 = 86 if y < 60 else (66 if y < 70 else 56)
        s += line(f'M37 {y}H{x1}', CREAM_D, 5.4) + circle(x, y + 1, 6, DARK[c]) + circle(x, y, 6, c)
    s += gear(76, 80, 14.5, 'stone', 'olive-dark', 'yellow', depth=2)
    return s


def database_file():
    """Database file: page with a stacked aqua cylinder."""
    s = sheet('aqua-dark')
    cx, rx, ry, h = 62, 24, 8, 10
    for top in (79, 64, 49):
        s += path(f'M{cx - rx} {top}V{top + h}A{rx} {ry} 0 0 0 {cx + rx} {top + h}V{top}Z', 'aqua-dark')
        s += ellipse(cx, top, rx, ry, 'aqua')
        s += circle(cx - 13, top + h + 2.5, 2.4, 'yellow')
    s += ellipse(cx, 49, 14, 4.2, 'white')
    return s


def ebook_file():
    """E-book: the page is a book with an olive spine and an orange bookmark."""
    s = sheet('sand', tab=False)
    s += path('M36 16H42V101H36Q27 101 27 92V25Q27 16 36 16Z', 'olive')
    s += rect(27, 30, 15, 5, 1.5, 'yellow') + rect(27, 82, 15, 5, 1.5, 'yellow')
    s += path('M54 16H69V50L61.5 43L54 50Z', 'orange-dark', transform='translate(1.2 2)') + path('M54 16H69V50L61.5 43L54 50Z', 'orange')
    s += line('M51 62H88M51 73H88M51 84H76', OLIVE, 5)
    return s


def font_file():
    """Font file: page with a slab-serif clay "A"."""
    s = sheet('orange')

    def glyph(c):
        return (path('M55.5 41H68.5L86 91H73.5L70.4 81H53.6L50.5 91H38ZM57 70.5H67L62 54.5Z', c, fill_rule='evenodd')
                + rect(34, 87, 21, 7, 3, c) + rect(69, 87, 21, 7, 3, c))
    s += f'<g transform="translate(1.5 2.6)">{glyph("orange-dark")}</g>' + glyph('orange')
    return s


def disk_image_file():
    """Disk image (ISO): page with a clay disc."""
    s = sheet('aqua-dark')
    cx, cy = 62, 68

    def wedge(a0, a1, r0, r1, c, **kw):
        a0, a1 = math.radians(a0), math.radians(a1)
        pt = lambda a, r: f'{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}'
        return path(f'M{pt(a0, r0)}L{pt(a0, r1)}A{r1} {r1} 0 0 1 {pt(a1, r1)}L{pt(a1, r0)}A{r0} {r0} 0 0 0 {pt(a0, r0)}Z', c, **kw)
    s += circle(cx + 1.2, cy + 2.6, 26, 'aqua-dark') + circle(cx, cy, 26, 'white') + circle(cx, cy, 22.5, 'aqua')
    s += wedge(-72, -40, 10, 22.5, 'white', opacity='.75') + wedge(-40, -22, 10, 22.5, 'yellow', opacity='.85')
    s += wedge(108, 140, 10, 22.5, 'white', opacity='.75') + wedge(140, 158, 10, 22.5, 'orange', opacity='.85')
    s += circle(cx, cy, 10, 'cream') + circle(cx, cy, 4.2, 'charcoal')
    return s


def virtual_disk_file():
    """Virtual disk: page with a small hard drive."""
    s = sheet('olive')
    s += rect(37, 45, 50, 50, 9, 'olive-dark') + rect(37, 42, 50, 50, 9, 'olive')
    s += circle(60, 61, 15.5, 'aqua-dark') + circle(60, 60, 15, 'aqua') + circle(60, 60, 5.5, 'cream') + circle(60, 60, 2.4, 'orange')
    s += line('M79 82L67 67', YELLOW, 4.6) + circle(79, 82, 5.2, 'yellow')
    s += rect(42, 79, 24, 8, 3.5, 'orange')
    return s


def torrent_file():
    """Torrent: page with a download arrow and an upload arrow."""
    s = sheet('yellow')
    down = 'M43 45H52V68H59.5L47.5 91L35.5 68H43Z'
    up = 'M77.5 42L89.5 65H82V88H73V65H65.5Z'
    s += soft(down, 'orange-dark', 3.4, transform='translate(1.4 2.6)') + soft(down, 'orange', 3.4)
    s += soft(up, 'olive-dark', 3.4, transform='translate(1.4 2.6)') + soft(up, 'olive', 3.4)
    return s


def calendar_file():
    """Calendar file: page with a small ring-bound calendar."""
    s = sheet('orange')
    s += rect(35, 49, 54, 46, 7, 'cream-dark') + rect(35, 46, 54, 46, 7, 'white')
    s += path('M42 46H82Q89 46 89 53V59H35V53Q35 46 42 46Z', 'orange')
    s += rect(46, 41, 5.5, 11, 2.7, 'yellow') + rect(72.5, 41, 5.5, 11, 2.7, 'yellow')
    for i in range(8):
        c = 'orange' if i == 5 else 'olive'
        s += rect(41 + 11.3 * (i % 4), 64 + 12 * (i // 4), 7.6, 7.6, 2.2, c)
    return s


def contact_file():
    """Contact card: page with a person silhouette."""
    s = sheet('rose')
    bust = 'M39 91C39 76 49 70 62 70C75 70 85 76 85 91Q85 94 82 94H42Q39 94 39 91Z'
    s += path(bust, 'orange-dark', transform='translate(1.4 2.4)') + path(bust, 'rose')
    s += path('M54.5 70.6L62 81L69.5 70.6Z', 'white')
    s += circle(63.2, 57.4, 11.5, 'orange-dark') + circle(62, 55, 11.5, 'rose')
    return s


def web_file():
    """Web page: page with a globe."""
    s = sheet('aqua')
    cx, cy = 62, 68
    s += circle(cx + 1.2, cy + 2.6, 25, 'aqua-dark') + circle(cx, cy, 25, 'aqua')
    s += path('M45 55Q52 46 62 47Q66 52 60 56Q62 62 55 64Q52 72 46 68Q41 62 45 55Z', 'olive')
    s += path('M70 62Q78 58 85 64Q88 72 82 82Q76 88 72 82Q74 74 68 70Q66 65 70 62Z', 'olive')
    s += path('M52 80Q58 78 62 84Q62 90 58 92Q52 90 50 85Z', 'olive')
    return s


def xml_file():
    """XML/markup: page with clay angle brackets around a yellow node."""
    s = sheet('orange')
    for d in ('M52 52L38 68L52 84', 'M72 52L86 68L72 84'):
        s += line(d, ORANGE_D, 7, transform='translate(1.2 2.2)') + line(d, ORANGE, 7)
    s += circle(62.8, 69.6, 6, 'yellow-dark') + circle(62, 68, 6, 'yellow')
    return s


def subtitles_file():
    """Subtitles: page with a dark frame and two caption bars."""
    s = sheet('charcoal')
    s += rect(34, 47, 56, 47, 8, 'ink') + rect(34, 44, 56, 47, 8, 'charcoal')
    s += circle(44, 54, 3, 'orange') + line('M52 54H64', '#6b665c', 4)
    s += line('M42 69H82', WHITE, 5.6) + line('M48 80.5H76', YELLOW, 5.6)
    return s


def patch_file():
    """Patch/diff: page with added (olive, plus) and removed (orange, minus) rows."""
    s = sheet('olive')
    for y, c in ((42, 'olive'), (59, 'orange'), (76, 'olive')):
        s += rect(35, y + 2.2, 54, 13, 5, DARK[c]) + rect(35, y, 54, 13, 5, c)
        s += line(f'M39.8 {y + 6.5}H47.2' + (f'M43.5 {y + 2.8}V{y + 10.2}' if c == 'olive' else ''), WHITE, 3.2)
        s += line(f'M54 {y + 6.5}H{82 if c == "olive" else 72}', WHITE, 3.2, opacity='.6')
    return s


def playlist_file():
    """Playlist: page with a clay note and list lines."""
    s = sheet('rose')

    def note(c):
        return (rect(52, 44, 6.5, 40, 3, c) + path('M52 44H58.5Q66 46 68 56Q63 51 58.5 52H52Z', c)
                + ellipse(47, 84, 10.5, 8, c, transform='rotate(-18 47 84)'))
    s += f'<g transform="translate(1.5 2.5)">{note("orange-dark")}</g>' + note('rose')
    s += line('M72 62H88M66 74H88M66 86H82', OLIVE, 5)
    return s


ART = {
    'eduka-menu': eduka_menu,
    'eduka-panel': eduka_panel,
    'eduka-settings': eduka_settings,
    'eduka-about': eduka_about,
    'eduka-desktop': eduka_desktop,
    'eduka-session': eduka_session,
    'eduka-welcome': eduka_welcome,
    'eduka-appstore-tile': eduka_appstore_tile,
    'blank-file': blank_file,
    'symlink-file': symlink_file,
    'device-file': device_file,
    'pipe-file': pipe_file,
    'socket-file': socket_file,
    'certificate-file': certificate_file,
    'key-file': key_file,
    'template-file': template_file,
    'log-file': log_file,
    'config-file': config_file,
    'database-file': database_file,
    'ebook-file': ebook_file,
    'font-file': font_file,
    'disk-image-file': disk_image_file,
    'virtual-disk-file': virtual_disk_file,
    'torrent-file': torrent_file,
    'calendar-file': calendar_file,
    'contact-file': contact_file,
    'web-file': web_file,
    'xml-file': xml_file,
    'subtitles-file': subtitles_file,
    'patch-file': patch_file,
    'playlist-file': playlist_file,
}
