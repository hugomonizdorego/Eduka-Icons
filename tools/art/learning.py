"""Eduka-Icons 1.0 clay artwork: learning group.

rocket, flask, game, weather, wand, atom, microscope, graduation, trophy,
abacus, dice, pencil-ruler, blocks, compass-draw, paintbox.
Every function returns an SVG fragment on the 128 x 128 grid; tools/clay.py
sculpts each shape element separately. GPL-3.0.
"""
import math
import re
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_D = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_D, YELLOW, YELLOW_D = '#e0703a', '#b9552a', '#eec14f', '#cf9f33'
OLIVE, OLIVE_D = '#7d8c55', '#5f6c40'
AQUA, AQUA_D, CHARCOAL, STONE = '#8fc0c4', '#6a9ea3', '#3f3c37', '#9a9c8b'

_TOKEN = re.compile(r'[MLHVCQAZ]|-?\d*\.?\d+')


def ellipse(cx, cy, rx, ry, c, **kw):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    fill = c if c == 'none' or c.startswith('#') else f'url(#{c})'
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'


class Xf:
    """Rotate / scale geometry (not the element) so light and shadow keep one direction."""

    def __init__(self, degrees=0, cx=64, cy=62, scale=1, dx=0, dy=0):
        a = math.radians(degrees)
        self.deg, self.c, self.s, self.cx, self.cy = degrees, math.cos(a), math.sin(a), cx, cy
        self.k, self.ox, self.oy = scale, dx, dy

    def xy(self, x, y):
        dx, dy = (x - self.cx) * self.k, (y - self.cy) * self.k
        return self.cx + self.ox + dx * self.c - dy * self.s, self.cy + self.oy + dx * self.s + dy * self.c

    def p(self, x, y):
        return '{:.2f} {:.2f}'.format(*self.xy(x, y))

    def d(self, d):
        """Transform an absolute path (M L H V C Q A Z)."""
        tokens, out, i, x, y, command = _TOKEN.findall(d), [], 0, 0.0, 0.0, 'M'
        take = lambda n: [float(v) for v in tokens[i:i + n]]
        while i < len(tokens):
            if tokens[i].isalpha():
                command = tokens[i]
                i += 1
                if command == 'Z':
                    out.append('Z')
                continue
            if command == 'H':
                x = take(1)[0]; i += 1
                out.append('L' + self.p(x, y))
            elif command == 'V':
                y = take(1)[0]; i += 1
                out.append('L' + self.p(x, y))
            elif command == 'A':
                rx, ry, rot, large, sweep, x, y = take(7); i += 7
                out.append(f'A{rx * self.k:.2f} {ry * self.k:.2f} {rot + self.deg:.2f} {int(large)} {int(sweep)} {self.p(x, y)}')
            else:
                n = {'M': 1, 'L': 1, 'Q': 2, 'C': 3}[command]
                values = take(2 * n); i += 2 * n
                x, y = values[-2:]
                out.append(command + ' '.join(self.p(values[j], values[j + 1]) for j in range(0, 2 * n, 2)))
                if command == 'M':
                    command = 'L'
        return ''.join(out)

    def path(self, d, c, **kw):
        return path(self.d(d), c, **kw)

    def rr(self, x, y, w, h, r, c, **kw):
        return path(self.d(f'M{x + r} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h - r}A{r} {r} 0 0 1 {x + w - r} {y + h}'
                           f'H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}V{y + r}A{r} {r} 0 0 1 {x + r} {y}Z'), c, **kw)

    def circ(self, x, y, r, c, **kw):
        px, py = self.xy(x, y)
        return circle(round(px, 2), round(py, 2), round(r * self.k, 2), c, **kw)

    def ln(self, d, colour, width, **kw):
        return line(self.d(d), colour, round(width * self.k, 2), **kw)


def rpoly(points, t=.3):
    """Closed polygon with clay-soft corners (each corner cut back by t of its edges)."""
    d, n = '', len(points)
    for i, (x, y) in enumerate(points):
        (px, py), (nx, ny) = points[i - 1], points[(i + 1) % n]
        d += ('M' if i == 0 else 'L') + f'{x + (px - x) * t:.2f} {y + (py - y) * t:.2f}Q{x:.2f} {y:.2f} {x + (nx - x) * t:.2f} {y + (ny - y) * t:.2f}'
    return d + 'Z'


def star(cx, cy, outer, inner, n=5, turn=-90, t=.3):
    points = []
    for i in range(2 * n):
        a, r = math.radians(turn + i * 180 / n), (outer if i % 2 == 0 else inner)
        points.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return rpoly(points, t)


def dot(x, y, r, colour, **kw):
    """Small free-floating bead (a round stroke, so its soft shadow is never clipped)."""
    return line(f'M{x} {y}h.01', colour, 2 * r, **kw)


def spark(cx, cy, r, c, **kw):
    """Four-point sparkle."""
    return path(star(cx, cy, r, r * .42, 4, -90, .22), c, **kw)


# --------------------------------------------------------------------------
def rocket():
    """Toy rocket climbing to the upper right: cream hull, orange nose and fins, aqua porthole, flame."""
    t = Xf(45, 64, 66, .78, 5, -6)
    body = 'M64 6C80 20 84 44 82 62L78 88H50L46 62C44 44 48 20 64 6Z'
    fin_l = 'M47 62L35 77Q31 82 31.5 89L32.5 101Q33 105 36.5 102.5L50 90Z'
    fin_r = 'M81 62L93 77Q97 82 96.5 89L95.5 101Q95 105 91.5 102.5L78 90Z'
    s = spark(31, 33, 10, 'yellow') + dot(50, 20, 3.4, AQUA) + dot(101, 86, 4.4, YELLOW) + dot(88, 101, 3.2, AQUA)
    s += t.path(fin_l, 'orange-dark', transform='translate(1.5 3)') + t.path(fin_r, 'orange-dark', transform='translate(1.5 3)')
    s += t.path(fin_l, 'orange') + t.path(fin_r, 'orange')
    s += t.path('M51 92C44 106 58 114 64 128C70 114 84 106 77 92Z', 'orange')            # flame
    s += t.path('M57 92C53 102 61 107 64 115C67 107 75 102 71 92Z', 'yellow')
    s += t.path('M52 86H76L73 96H55Z', 'olive-dark')                                     # nozzle
    s += t.path(body, 'cream-dark', transform='translate(2 3.5)')
    s += t.path(body, 'cream')
    s += t.path('M64 6C73 14 78.5 24 81 35H47C49.5 24 55 14 64 6Z', 'orange')            # nose cone
    s += t.path('M47.2 70H80.8L79.5 79H48.5Z', 'olive')                                  # hull band
    s += t.circ(64, 52, 12.5, 'yellow') + t.circ(64, 52, 8, 'aqua') + t.circ(61.2, 49.2, 2.8, 'white')
    return s

# --------------------------------------------------------------------------
def flask():
    """Bubbling Erlenmeyer flask: cream glass, aqua liquid, orange lip, bubbles drifting off."""
    body = 'M52 24H74V52L97 88Q104 103 90 103H36Q22 103 29 88L52 52Z'
    s = dot(91, 30, 6.5, YELLOW) + dot(102, 46, 4.2, ORANGE) + dot(86, 46, 3.2, AQUA)
    s += path(body, 'cream-dark', transform='translate(2 3)')
    s += path(body, 'cream')
    s += path('M41 69Q48.5 64 56 69Q63 74 70.5 69Q78 64 85 69L94 87Q98 98 89 98H37Q28 98 32 87Z', 'aqua')
    s += circle(47, 85, 5, 'white') + circle(62, 89, 3.4, 'white') + circle(57, 78, 3, 'white')
    s += line('M76 78H84M79 87H89', AQUA_D, 3.4)
    s += circle(66, 57, 4, 'aqua') + circle(68, 43, 3.2, 'aqua')
    s += line('M58 34V50', WHITE, 3.4)                                                   # glass glint
    s += rect(46, 20, 34, 10, 5, 'orange-dark') + rect(46, 18, 34, 9.5, 4.7, 'orange')
    return s


# --------------------------------------------------------------------------
def game():
    """Retro gamepad with cable, shoulder buttons, olive d-pad and four coloured buttons."""
    body = 'M40 40H88Q103 40 107 60L110 84Q111 102 98 99Q91 97 85 86L81 80H47L43 86Q37 97 30 99Q17 102 18 84L21 60Q25 40 40 40Z'
    s = line('M64 42C64 26 84 34 85 20', ORANGE, 4.8)
    s += rect(30, 34, 26, 14, 6, 'orange') + rect(72, 34, 26, 14, 6, 'orange')
    s += path(body, 'cream-dark', transform='translate(0 4)')
    s += path(body, 'cream')
    s += rect(28.5, 55.5, 23, 9, 3, 'olive') + rect(35.5, 48.5, 9, 23, 3, 'olive') + circle(40, 60, 2.6, 'olive-dark')
    s += circle(88, 50, 5.2, 'yellow') + circle(98, 60, 5.2, 'orange') + circle(78, 60, 5.2, 'aqua') + circle(88, 70, 5.2, 'olive')
    s += rect(55, 49, 7.5, 4.6, 2.3, 'cream-dark') + rect(65.5, 49, 7.5, 4.6, 2.3, 'cream-dark')
    s += circle(64, 66, 6, 'cream-dark') + circle(64, 65.5, 3.4, 'orange')
    return s


# --------------------------------------------------------------------------
def weather():
    """Spiky sun behind a plump two-layer cloud with three rain drops."""
    cloud = 'M38 86C18 86 16 63 34 60C35 42 61 37 71 55C89 51 103 62 98 76Q94 86 84 86Z'
    s = path(star(83, 42, 26.5, 19.5, 12, -90, .25), 'orange')
    s += circle(83, 42, 17, 'yellow')
    drops = ''.join(f'M{x} 93C{x + 6} 100 {x + 5} 106 {x} 106C{x - 5} 106 {x - 6} 100 {x} 93Z' for x in (38, 58, 78))
    s += path(drops + 'M57 66h2v2h-2Z', 'aqua')            # the hidden speck widens the shadow box
    s += path(cloud, 'cream-dark', transform='translate(1.5 3.5)')
    s += path(cloud, 'cream')
    s += path('M40 86C27 86 27 71 39 70C41 58 59 58 62 70C73 68 77 86 65 86Z', 'white')
    return s

# --------------------------------------------------------------------------
def wand():
    """Magic wand: olive stick with cream caps, a fat golden star and sparkles."""
    s = spark(36, 36, 10.5, 'orange') + spark(98, 86, 8.5, 'aqua')
    s += dot(57, 21, 3.4, AQUA) + dot(26, 64, 3.4, YELLOW) + dot(80, 96, 3.2, ORANGE)
    stick = 'M27 100L70 57'
    s += line(stick, CREAM_D, 11, transform='translate(1.5 3)') + line(stick, CREAM, 11)
    s += line('M37 90L60 67', OLIVE_D, 11, transform='translate(1.5 3)') + line('M37 90L60 67', OLIVE, 11)
    s += path(star(80, 44, 27, 12.5, 5, -90, .26), 'yellow-dark', transform='translate(2 3.5)')
    s += path(star(80, 44, 27, 12.5, 5, -90, .26), 'yellow')
    s += circle(80, 45, 5, 'cream')
    return s


# --------------------------------------------------------------------------
def atom():
    """Three aqua orbits with electrons around a clustered orange nucleus."""
    def orbit(turn, colour, **kw):
        a = math.radians(turn)
        x, y = 43 * math.cos(a), 43 * math.sin(a)
        return path(f'M{63 - x:.2f} {61 - y:.2f}A43 15.5 {turn} 1 0 {63 + x:.2f} {61 + y:.2f}A43 15.5 {turn} 1 0 {63 - x:.2f} {61 - y:.2f}',
                    'none', stroke=colour, stroke_width=5.2, **kw)

    def on(turn, at):
        a, b = math.radians(turn), math.radians(at)
        x, y = 43 * math.cos(b), 15.5 * math.sin(b)
        return 63 + x * math.cos(a) - y * math.sin(a), 61 + x * math.sin(a) + y * math.cos(a)

    s = ''.join(orbit(turn, AQUA_D, transform='translate(1.2 2.6)') for turn in (0, 60, 120))
    s += ''.join(orbit(turn, AQUA) for turn in (0, 60, 120))
    s += circle(65, 66, 13, 'orange-dark')
    s += circle(58, 57, 9.5, 'orange') + circle(70, 60, 8.5, 'yellow') + circle(61, 68, 8.5, 'orange')
    for turn, at, c in ((0, 150, 'yellow'), (60, -20, 'orange'), (120, 200, 'yellow')):
        x, y = on(turn, at)
        s += circle(round(x, 2), round(y, 2), 6, c)
    return s


# --------------------------------------------------------------------------
def microscope():
    """Lab microscope: tilted cream tube, orange eyepiece, olive base and stage, yellow focus knob."""
    t = Xf(-26, 64, 44, 1.05, -12, 7)
    arm = 'M88 92V62Q88 42 62 42'
    s = rect(22, 96, 84, 10, 5, 'olive-dark') + rect(22, 92, 84, 10, 5, 'olive')          # base
    s += rect(49, 85, 18, 9, 3.5, 'yellow')                                              # lamp
    s += line(arm, CREAM_D, 13, transform='translate(1.5 3)') + line(arm, CREAM, 13)     # arm
    s += rect(30, 80.5, 56, 8, 4, 'olive-dark') + rect(30, 78, 56, 7.5, 3.7, 'olive')     # stage
    s += rect(44, 75, 30, 4.6, 2, 'aqua')                                                # slide
    s += t.rr(60, 58, 8, 13, 2.5, 'charcoal')                                            # objective
    s += t.rr(57.5, 14, 13, 14, 3, 'cream-dark')                                         # draw tube
    s += t.rr(54, 22, 20, 34, 6, 'cream-dark', transform='translate(1.5 3)')
    s += t.rr(54, 22, 20, 34, 6, 'cream')                                                # body tube
    s += t.rr(51, 51, 26, 9, 4, 'yellow')                                                # nosepiece
    s += t.rr(56, 9, 16, 9, 3.5, 'orange')                                               # eyepiece
    s += t.rr(58, 30, 12, 5, 2.5, 'olive')
    s += circle(90.5, 65.5, 9, 'yellow-dark') + circle(89.5, 64, 9, 'yellow') + circle(89.5, 64, 3.4, 'orange')   # focus knob
    return s

# --------------------------------------------------------------------------
def graduation():
    """Mortarboard: olive board with visible thickness, skull cap with cream band, golden tassel."""
    board = rpoly([(64, 20), (110, 42), (64, 64), (18, 42)], .13)
    s = path('M35 48H93V78Q93 84 86 87Q64 97 42 87Q35 84 35 78Z', 'olive-dark')            # skull cap
    s += line('M38.5 77Q64 93 89.5 77', CREAM, 5.5)                                      # band
    s += path(board, 'olive-dark', transform='translate(0 5.5)')
    s += path(board, 'olive')
    s += line('M64 42L99 47V76', YELLOW_D, 4.4, transform='translate(1 2)')
    s += line('M64 42L99 47V76', YELLOW, 4.4)                                            # cord
    s += path('M94.5 80H103.5L106 99Q99 104 92 99Z', 'yellow')                            # tassel
    s += rect(93.5, 73, 11, 9, 3.5, 'orange')
    s += circle(64, 42.5, 6.5, 'yellow-dark') + circle(64, 41.5, 6, 'yellow')            # button
    return s


# --------------------------------------------------------------------------
def trophy():
    """Golden cup with two handles and an orange star on a cream and olive plinth."""
    cup = 'M37 21H91V40Q91 72 64 72Q37 72 37 40Z'
    left, right = 'M39 31H31Q23 31 23 40Q23 54 44 58', 'M89 31H97Q105 31 105 40Q105 54 84 58'
    s = line(left, YELLOW_D, 7, transform='translate(1 3)') + line(right, YELLOW_D, 7, transform='translate(1 3)')
    s += line(left, YELLOW, 7) + line(right, YELLOW, 7)
    s += path('M57 68H71L73 85H55Z', 'yellow-dark')                                       # stem
    s += rect(34, 92.5, 60, 13.5, 5, 'olive-dark') + rect(34, 89, 60, 13.5, 5, 'olive')   # plinth
    s += rect(43, 83, 42, 8.5, 4, 'cream')
    s += rect(52, 93, 24, 6, 2.5, 'yellow')                                              # plaque
    s += path(cup, 'yellow-dark', transform='translate(1.5 3.5)')
    s += path(cup, 'yellow')
    s += rect(53, 73, 22, 6.5, 3.2, 'yellow')                                            # knop
    s += rect(33, 18.5, 62, 10, 5, 'yellow-dark') + rect(33, 16.5, 62, 9.5, 4.7, 'yellow')   # rim
    s += path(star(64, 46, 13.5, 6.3, 5, -90, .26), 'orange')
    return s


# --------------------------------------------------------------------------
def abacus():
    """Counting frame: cream frame, three rods, orange / yellow / aqua beads pushed to both sides."""
    frame = ('M29 18H99Q110 18 110 29V91Q110 102 99 102H29Q18 102 18 91V29Q18 18 29 18Z'
             'M33 28Q28 28 28 33V87Q28 92 33 92H95Q100 92 100 87V33Q100 28 95 28Z')
    s = line('M26 40H102M26 60H102M26 80H102', OLIVE_D, 3.6)
    s += path(frame, 'cream-dark', fill_rule='evenodd', transform='translate(0 4)')
    s += path(frame, 'cream', fill_rule='evenodd')
    rows = ((40, 'orange', 'orange-dark', (34.5, 45.5, 56.5, 82.5, 93.5)),
            (60, 'yellow', 'yellow-dark', (34.5, 60.5, 71.5, 82.5, 93.5)),
            (80, 'aqua', 'aqua-dark', (34.5, 45.5, 56.5, 67.5, 93.5)))
    for y, c, dark, xs in rows:
        for x in xs:
            s += ellipse(x + .8, y + 1.6, 5.4, 7.6, dark) + ellipse(x, y, 5.4, 7.4, c)
    s += ''.join(circle(x, y, 2.8, 'olive') for x in (23.5, 104.5) for y in (23.5, 96.5))
    return s


# --------------------------------------------------------------------------
def dice():
    """Two tumbling dice: a big cream five and a small orange three."""
    a, b = Xf(-10, 50, 50), Xf(14, 82, 77)
    s = a.rr(22, 22, 56, 56, 13, 'cream-dark', transform='translate(2 4.5)')
    s += a.rr(22, 22, 56, 56, 13, 'cream')
    s += ''.join(a.circ(50 + dx, 50 + dy, 5, 'orange') for dx, dy in ((-15, -15), (15, -15), (0, 0), (-15, 15), (15, 15)))
    s += b.rr(61, 56, 42, 42, 11, 'orange-dark', transform='translate(2 4)')
    s += b.rr(61, 56, 42, 42, 11, 'orange')
    s += ''.join(b.circ(82 + d, 77 + d, 4.4, 'cream') for d in (-11, 0, 11))
    return s


# --------------------------------------------------------------------------
def pencil_ruler():
    """Yellow ruler and orange pencil crossed like an X."""
    r, p = Xf(-45, 64, 61), Xf(45, 64, 61)
    s = r.rr(15, 50, 98, 22, 4.5, 'yellow-dark', transform='translate(2 3.5)')
    s += r.rr(15, 50, 98, 22, 4.5, 'yellow')
    for i, x in enumerate(range(24, 105, 10)):
        s += r.ln(f'M{x} 53V{63 if i % 2 == 0 else 59}', OLIVE_D, 3.2)
    s += p.rr(15, 53, 78, 16, 4, 'orange-dark', transform='translate(2 3.5)')
    s += p.path('M91 53L107 59.5Q111 61 107 62.5L91 69Z', 'cream-dark', transform='translate(2 3.5)')
    s += p.rr(31, 53, 61, 16, 2, 'orange')                                               # barrel
    s += p.rr(31, 58.5, 61, 5, 1.5, 'orange-dark')                                       # facet
    s += p.path('M91 53L107 59.5Q111 61 107 62.5L91 69Z', 'cream')                       # sharpened wood
    s += p.path('M102 57.5L107 59.5Q111 61 107 62.5L102 64.5Z', 'charcoal')              # lead
    s += p.rr(23, 53, 10, 16, 2, 'metal')                                                # ferrule
    s += p.rr(14, 53, 11, 16, 5, 'rose')                                                 # eraser
    return s


# --------------------------------------------------------------------------
def blocks():
    """Three toy cubes stacked in a pyramid, each stamped with a shape."""
    top = Xf(-7, 64, 38)
    s = rect(18, 62, 44, 44, 8, 'orange-dark') + rect(18, 58, 44, 44, 8, 'orange')
    s += rect(24.5, 64.5, 31, 31, 5, 'none', stroke=ORANGE_D, stroke_width=3)
    s += circle(40, 80, 9.5, 'cream')
    s += rect(64, 62, 44, 44, 8, 'aqua-dark') + rect(64, 58, 44, 44, 8, 'aqua')
    s += rect(70.5, 64.5, 31, 31, 5, 'none', stroke=AQUA_D, stroke_width=3)
    s += path(rpoly([(86, 69), (97, 89), (75, 89)], .2), 'cream')
    s += top.rr(43, 17, 42, 42, 8, 'yellow-dark', transform='translate(0 4)')
    s += top.rr(43, 17, 42, 42, 8, 'yellow')
    s += top.rr(49.5, 23.5, 29, 29, 5, 'none', stroke=YELLOW_D, stroke_width=3)
    cx, cy = top.xy(64, 38)
    s += path(star(cx, cy, 11, 5.2, 5, -97, .26), 'orange')
    return s


# --------------------------------------------------------------------------
def compass_draw():
    """Drawing compass with yellow hinge, needle and pencil legs, tracing an aqua arc."""
    s = line('M22 92Q64 114 106 92', AQUA, 5.4)
    left, right = 'M59 36L37 85', 'M69 36L89 78'
    s += rect(58.5, 16, 11, 14, 4, 'cream')                                              # handle
    s += line('M36 87L33.5 96.5', STONE, 4.4)                                            # needle
    s += line(left, OLIVE_D, 11, transform='translate(1.5 3)') + line(right, OLIVE_D, 11, transform='translate(1.5 3)')
    s += line(left, OLIVE, 11) + line(right, OLIVE, 11)
    s += line('M48 63Q64 55 81 63', CREAM, 4.8) + circle(82, 63, 5, 'yellow')             # spreader bar
    s += line('M88.5 77L93 89', ORANGE, 11)                                              # pencil clamp
    s += line('M94 92L95.4 96.5', CHARCOAL, 4.6)
    s += circle(64, 33, 11, 'yellow-dark') + circle(64, 31.5, 11, 'yellow') + circle(64, 31.5, 4.2, 'orange')
    return s

# --------------------------------------------------------------------------
def paintbox():
    """Open watercolour tin: olive shell, enamel lid with mixed puddles, eight pans and a brush."""
    s = path('M27 16H101Q107 16 108 22L110 44H18L20 22Q21 16 27 16Z', 'olive')              # lid
    s += rect(25, 20.5, 78, 19, 6, 'white')
    s += ellipse(40, 30, 9, 5.5, 'aqua') + ellipse(63, 30.5, 8, 5, 'rose') + ellipse(86, 30, 9, 5.5, 'yellow')
    s += rect(16, 46, 94, 60, 10, 'olive-dark') + rect(16, 42.5, 94, 60, 10, 'olive')     # tray shell
    s += rect(29, 39, 13, 7, 3, 'yellow') + rect(86, 39, 13, 7, 3, 'yellow')              # hinges
    s += rect(21, 48, 84, 49, 6, 'cream')
    pans = (('orange', 'yellow', 'olive', 'aqua'), ('rose', 'yellow-dark', 'aqua-dark', 'charcoal'))
    for j, row in enumerate(pans):
        for i, c in enumerate(row):
            s += rect(25 + 20 * i, 51.5 + 15.5 * j, 16, 12.5, 3.5, c)
    s += line('M28 89H68', ORANGE, 5.6)                                                  # brush
    s += rect(66, 85.2, 11, 7.6, 2.5, 'yellow')
    s += path('M77 85.2Q92 86 100 89Q92 92 77 92.8Z', 'charcoal')
    return s


ART = {'rocket': rocket, 'flask': flask, 'game': game, 'weather': weather, 'wand': wand,
       'atom': atom, 'microscope': microscope, 'graduation': graduation, 'trophy': trophy,
       'abacus': abacus, 'dice': dice, 'pencil-ruler': pencil_ruler, 'blocks': blocks,
       'compass-draw': compass_draw, 'paintbox': paintbox}
