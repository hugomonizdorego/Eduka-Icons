"""Eduka-Icons 1.0 clay artwork: system group.

update, search, chart, clock, clock-settings, calculator, battery, logout,
hibernate, moon, puzzle.
Every function returns an SVG fragment on the 128 x 128 grid; tools/clay.py
sculpts each shape element separately. GPL-3.0.
"""
import math
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_D = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_D, YELLOW, YELLOW_D = '#e0703a', '#b9552a', '#eec14f', '#cf9f33'
OLIVE, OLIVE_D = '#7d8c55', '#5f6c40'
AQUA, AQUA_D, CHARCOAL = '#8fc0c4', '#6a9ea3', '#3f3c37'
NIGHT = '#4f7f86'          # side face of the aqua-dark night disc
ROUND = dict(stroke_width=4, stroke_linejoin='round')   # blunt, clay-like points


def group(transform, *parts):
    return f'<g transform="{transform}">' + ''.join(parts) + '</g>'


def polar(cx, cy, r, degrees):
    a = math.radians(degrees)
    return f'{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}'


def star(x, y, r, c, pinch=.22, **kw):
    """Four-point sparkle with concave sides."""
    k = r * pinch
    return path(f'M{x} {y - r}Q{x + k} {y - k} {x + r} {y}Q{x + k} {y + k} {x} {y + r}'
                f'Q{x - k} {y + k} {x - r} {y}Q{x - k} {y - k} {x} {y - r}Z', c, **kw)


def cog(cx, cy, outer, root, teeth, c, turn=0, **kw):
    """Gear outline with flat-topped teeth."""
    step, pts = 360 / teeth, []
    for i in range(teeth):
        a = turn + i * step
        for r, off in ((root, -.30), (outer, -.17), (outer, .17), (root, .30)):
            pts.append(polar(cx, cy, r, a + off * step))
    return path('M' + 'L'.join(pts) + 'Z', c, **kw)


def crescent(cx, cy, r, bx, by, br):
    """Moon: disc (cx cy r) with the disc (bx by br), up and to the right, bitten out."""
    dx, dy = bx - cx, by - cy
    d = math.hypot(dx, dy)
    a = (r * r - br * br + d * d) / (2 * d)
    h = math.sqrt(r * r - a * a)
    mx, my = cx + a * dx / d, cy + a * dy / d
    p1 = (mx + h * dy / d, my - h * dx / d)
    p2 = (mx - h * dy / d, my + h * dx / d)
    top, low = (p1, p2) if p1[1] < p2[1] else (p2, p1)
    return (f'M{top[0]:.2f} {top[1]:.2f}A{r} {r} 0 1 0 {low[0]:.2f} {low[1]:.2f}'
            f'A{br} {br} 0 0 1 {top[0]:.2f} {top[1]:.2f}Z')


# --------------------------------------------------------------------------
def update():
    """Two chunky arrows chasing each other around a yellow ball."""
    cx, cy, r, half = 63, 60, 31, 7

    def arrow(a0, c, edge, **kw):
        a1 = a0 + 112
        t = math.radians(a1)                       # the head leaves the arc along its tangent
        tip = f'{cx + (r - 2) * math.cos(t) - 22 * math.sin(t):.2f} {cy + (r - 2) * math.sin(t) + 22 * math.cos(t):.2f}'
        return path(
            f'M{polar(cx, cy, r + half, a0)}A{r + half} {r + half} 0 0 1 {polar(cx, cy, r + half, a1)}'
            f'L{polar(cx, cy, r + 15.5, a1)}L{tip}L{polar(cx, cy, r - 15.5, a1)}'
            f'L{polar(cx, cy, r - half, a1)}A{r - half} {r - half} 0 0 0 {polar(cx, cy, r - half, a0)}'
            f'A{half} {half} 0 0 1 {polar(cx, cy, r + half, a0)}Z', c,
            stroke=edge, stroke_width=3, stroke_linejoin='round', **kw)

    s = arrow(268, 'orange-dark', ORANGE_D, transform='translate(1 4)')
    s += arrow(88, 'aqua-dark', AQUA_D, transform='translate(1 4)')
    s += arrow(268, 'orange', ORANGE) + arrow(88, 'aqua', AQUA)
    s += circle(63.5, 62.5, 9.5, 'yellow-dark') + circle(63, 60, 9.5, 'yellow')
    return s


# --------------------------------------------------------------------------
def search():
    """Magnifying glass: cream rim, aqua lens, orange handle with brass collar."""
    s = line('M74 73L97 96', ORANGE_D, 15, transform='translate(1.5 3)')
    s += line('M74 73L97 96', ORANGE, 15)                           # handle
    s += path('M90.5 77.5L78.5 89.5', 'none', stroke=ORANGE_D, stroke_width=4)
    s += path('M98.5 85.5L86.5 97.5', 'none', stroke=ORANGE_D, stroke_width=4)   # grip grooves
    s += line('M68 67L74 73', YELLOW_D, 18, transform='translate(1 2.5)')
    s += line('M68 67L74 73', YELLOW, 18)                           # collar
    s += circle(49.5, 50, 32, 'cream-dark') + circle(48, 47, 32, 'cream')   # rim
    s += circle(48, 47, 24, 'aqua-dark') + circle(48.5, 48, 22, 'aqua')     # recessed lens
    s += line(f'M{polar(48.5, 48, 14.5, 172)}A14.5 14.5 0 0 1 {polar(48.5, 48, 14.5, 262)}', WHITE, 5, opacity='.85')
    s += circle(60, 58.5, 3, 'white', opacity='.85')
    return s


# --------------------------------------------------------------------------
def chart():
    """System monitor: desk instrument with a pulse trace, level bars and a knob."""
    s = rect(27, 96, 18, 10, 4, 'olive-dark') + rect(81, 96, 18, 10, 4, 'olive-dark')   # feet
    s += rect(17, 21, 92, 80, 13, 'cream-dark') + rect(17, 17, 92, 80, 13, 'cream')
    s += rect(24, 24, 78, 43, 8, 'charcoal')
    s += line('M31 57H44L50 50L57 60L63 54H70', AQUA_D, 4, opacity='.9')          # quiet trace
    s += line('M30 46H45L52 33L60 57L67 41L72 46H84', YELLOW, 5)                  # pulse
    s += circle(92, 46, 4, 'orange')
    for i, (h, c) in enumerate(((8, 'olive'), (13, 'olive'), (17, 'yellow'), (11, 'olive'), (15, 'orange'))):
        s += rect(26 + i * 9, 91 - h, 6, h, 2.5, c)                                # level bars
    s += rect(73, 80, 9, 5, 2.5, 'aqua-dark')
    s += circle(93, 82.5, 8, 'orange-dark') + circle(93, 81.5, 7, 'orange')        # knob
    s += line('M93 81.5L96.5 77.5', WHITE, 3.2)
    return s


# --------------------------------------------------------------------------
def _face(cx, cy, r, hour=305, minute=60):
    """Clock dial: cream face, olive quarter marks, small hour dots, charcoal hands."""
    s = circle(cx, cy, r + 2, 'cream-dark') + circle(cx, cy + .5, r, 'cream')
    for i in range(12):
        a = i * 30 - 90
        if i % 3 == 0:
            s += line(f'M{polar(cx, cy, r - 3.5, a)}L{polar(cx, cy, r - 7.5, a)}', OLIVE, 4)
        else:
            x, y = polar(cx, cy, r - 5, a).split()
            s += circle(x, y, 1.7, OLIVE)
    s += line(f'M{cx} {cy}L{polar(cx, cy, r * .52, hour - 90)}', CHARCOAL, 5.5)
    s += line(f'M{cx} {cy}L{polar(cx, cy, r * .74, minute - 90)}', CHARCOAL, 5.5)
    return s


def clock():
    """Twin-bell alarm clock: orange case, yellow bells, hammer, olive feet."""
    cx, cy = 63, 65

    def bell(bx, by, r, c, **kw):
        a = math.degrees(math.atan2(by - cy, bx - cx))
        return path(f'M{polar(bx, by, r, a - 90)}A{r} {r} 0 0 1 {polar(bx, by, r, a + 90)}Z', c, **kw)

    s = line('M42 90L33 101', OLIVE_D, 9) + line('M84 90L93 101', OLIVE_D, 9)      # feet
    s += line('M63 34V23', CHARCOAL, 5) + rect(55, 16, 16, 9, 4, 'orange')         # hammer
    for bx in (37, 89):
        s += line(f'M{bx} 33L{cx + (bx - cx) * .55:.1f} 46', CREAM_D, 6)           # bell posts
        s += bell(bx + .8, 35, 15, 'yellow-dark') + bell(bx, 32, 15, 'yellow')
    s += circle(cx, cy + 4, 36, 'orange-dark') + circle(cx, cy, 36, 'orange')      # case
    s += _face(cx, cy, 27.5)
    s += line(f'M{cx} {cy}L{polar(cx, cy, 20, 110)}', ORANGE, 3.2)                 # alarm hand
    s += circle(cx, cy, 4.5, 'yellow')
    return s


def clock_settings():
    """Aqua wall clock with an orange settings cog at its lower right."""
    cx, cy = 57, 55
    s = circle(cx + 1, cy + 4, 39, 'aqua-dark') + circle(cx, cy, 39, 'aqua')
    s += _face(cx, cy, 30)
    s += circle(cx, cy, 4.5, 'orange')
    gx, gy = 87, 84
    s += cog(gx, gy, 23, 18, 8, CREAM, turn=22.5, stroke=CREAM, stroke_width=5, stroke_linejoin='round')   # parting line
    s += cog(gx + 1, gy + 3, 19, 14, 8, 'orange-dark', turn=22.5, stroke=ORANGE_D, stroke_width=3, stroke_linejoin='round')
    s += cog(gx, gy, 19, 14, 8, 'orange', turn=22.5, stroke=ORANGE, stroke_width=3, stroke_linejoin='round')
    s += circle(gx, gy, 8, 'cream') + circle(gx, gy, 3.5, 'yellow')
    return s


# --------------------------------------------------------------------------
def calculator():
    """Pocket calculator: LCD showing 0, olive number keys, coloured function keys."""
    s = rect(31, 20, 68, 86, 12, 'cream-dark') + rect(28, 16, 68, 86, 12, 'cream')
    s += rect(34, 22, 56, 25, 7, 'charcoal') + rect(37.5, 25.5, 49, 18, 4, 'aqua')
    s += rect(72, 28.5, 9, 12, 3.5, 'none', stroke=CHARCOAL, stroke_width=3.2)     # the digit 0
    s += circle(42.5, 30.5, 2, CHARCOAL)
    xs, ys = (35, 49, 63, 77), (53, 65, 77, 89)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            if i == 3:
                if j == 3:
                    continue
                c = 'yellow'
            elif j == 0:
                c = 'orange' if i == 0 else 'aqua'
            else:
                c = 'olive'
            s += rect(x, y, 11, 21 if (i, j) == (3, 2) else 9, 3, c)
    return s


# --------------------------------------------------------------------------
def battery():
    """Charging battery lying on its side: olive cells and a big bolt."""
    bolt = 'M71 22L45 63H60L53 100L85 55H68Z'
    s = rect(96, 49, 13, 26, 5, 'yellow-dark') + rect(96, 46, 12, 26, 5, 'yellow')   # terminal
    s += rect(16, 35, 86, 56, 14, 'cream-dark') + rect(16, 31, 86, 56, 14, 'cream')
    s += rect(23, 38, 72, 42, 9, 'charcoal')
    for i in range(4):
        s += rect(27.5 + i * 16.5, 42.5, 13, 33, 4, 'olive')
    s += path(bolt, 'orange-dark', transform='translate(2 3)', stroke=ORANGE_D, stroke_width=3, stroke_linejoin='round')
    s += path(bolt, 'yellow', stroke=YELLOW, stroke_width=3, stroke_linejoin='round')
    return s


# --------------------------------------------------------------------------
def logout():
    """Door ajar in a cream frame with a big orange way-out arrow."""
    arrow = 'M56 55H83V44L108 62L83 80V69H56Z'
    s = rect(16, 97, 64, 9, 4.5, 'olive-dark')                                     # door step
    s += rect(21, 19, 56, 82, 9, 'cream-dark') + rect(19, 16, 56, 82, 9, 'cream')  # frame
    s += path('M26 23H68V98H26Z', 'charcoal')
    s += path('M26 23L55 31V93L26 98Z', 'olive')                                   # door leaf
    s += path('M31 31L50 36V58L31 57Z', 'olive-dark') + path('M31 64L50 64V87L31 91Z', 'olive-dark')
    s += circle(49.5, 61, 3, 'yellow')
    s += path(arrow, 'orange-dark', transform='translate(1.5 3.5)', stroke=ORANGE_D, stroke_width=3, stroke_linejoin='round')
    s += path(arrow, 'orange', stroke=ORANGE, stroke_width=3, stroke_linejoin='round')
    return s


# --------------------------------------------------------------------------
CLOUD = ('M64 102Q54 102 54 93.5Q54 86 62 85.5Q64 75 75 75Q84 75 87.5 82Q92 78.5 97.5 80.5'
         'Q103 83 102.5 89Q109 90.5 109 96.5Q109 102 102 102Z')


def hibernate():
    """Night disc: cream crescent, Z z, sparkles and a drifting cloud."""
    s = circle(63, 63, 42, NIGHT) + circle(63, 59, 42, 'aqua-dark')
    shape = crescent(51, 58, 27, 65, 47, 23)
    s += path(shape, 'cream-dark', transform='translate(0 3.5)', stroke=CREAM_D, **ROUND)
    s += path(shape, 'cream', stroke=CREAM, **ROUND)
    for d, w in (('M76 27H91L76 44H91', 5.5), ('M87 53H96L87 63H96', 4.5)):
        s += line(d, YELLOW_D, w, transform='translate(1 2.5)') + line(d, YELLOW, w)
    s += circle(46, 27, 2.6, 'white') + circle(71, 61, 2.3, 'white') + circle(50, 92, 2.3, 'white')
    s += group('translate(22 26.5) scale(.76)', path(CLOUD, 'cream-dark', transform='translate(0 4)'), path(CLOUD, 'cream'))
    return s


# --------------------------------------------------------------------------
def moon():
    """Golden crescent with craters, two sparkles and a cream cloud."""
    shape = crescent(58, 58, 41, 79, 43, 35)
    s = path(shape, 'yellow-dark', transform='translate(0 4)', stroke=YELLOW_D, **ROUND)
    s += path(shape, 'yellow', stroke=YELLOW, **ROUND)
    s += circle(34, 52, 6, 'yellow-dark') + circle(45, 78, 4.5, 'yellow-dark') + circle(52, 33, 3.5, 'yellow-dark')
    s += star(86, 38, 12, 'cream-dark', transform='translate(1 2.5)') + star(86, 38, 12, 'white')
    s += star(101, 61, 6.5, 'white')
    s += path(CLOUD, 'cream-dark', transform='translate(0 3)') + path(CLOUD, 'cream')
    return s


# --------------------------------------------------------------------------
def _piece(x0, y0, size, knob=11, neck=7):
    x1, y1, xm, ym, r = x0 + size, y0 + size, x0 + size / 2, y0 + size / 2, 9
    return (f'M{x0 + r} {y0}H{xm - neck}A{knob} {knob} 0 1 1 {xm + neck} {y0}H{x1 - r}Q{x1} {y0} {x1} {y0 + r}'
            f'V{ym - neck}A{knob} {knob} 0 1 1 {x1} {ym + neck}V{y1 - r}Q{x1} {y1} {x1 - r} {y1}'
            f'H{xm + neck}A{knob} {knob} 0 1 0 {xm - neck} {y1}H{x0 + r}Q{x0} {y1} {x0} {y1 - r}'
            f'V{ym + neck}A{knob} {knob} 0 1 0 {x0} {ym - neck}V{y0 + r}Q{x0} {y0} {x0 + r} {y0}Z')


def puzzle():
    """One fat olive jigsaw piece carrying a yellow sparkle."""
    piece = _piece(21, 39, 62)
    edge = dict(stroke_width=2.5, stroke_linejoin='round')
    s = path(piece, 'olive-dark', transform='translate(0 4.5)', stroke=OLIVE_D, **edge)
    s += path(piece, 'olive', stroke=OLIVE, **edge)
    s += star(55, 68, 13, 'yellow-dark', transform='translate(.8 2.2)') + star(55, 68, 13, 'yellow')
    return s


ART = {'update': update, 'search': search, 'chart': chart, 'clock': clock, 'clock-settings': clock_settings,
       'calculator': calculator, 'battery': battery, 'logout': logout, 'hibernate': hibernate, 'moon': moon,
       'puzzle': puzzle}
