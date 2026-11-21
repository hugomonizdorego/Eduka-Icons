"""Eduka 1.0 clay artwork: hardware devices. GPL-3.0."""
import math
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_DARK = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_DARK, YELLOW = '#e0703a', '#b9552a', '#eec14f'
OLIVE, OLIVE_DARK, AQUA, AQUA_DARK, CHARCOAL = '#7d8c55', '#5f6c40', '#8fc0c4', '#6a9ea3', '#3f3c37'


class Tilt:
    """Rotate geometry (not the element) so light and shadow keep one direction."""

    def __init__(self, degrees, cx=64, cy=62, scale=1, dx=0, dy=0):
        a = math.radians(degrees)
        self.c, self.s, self.cx, self.cy = math.cos(a), math.sin(a), cx, cy
        self.k, self.ox, self.oy = scale, dx, dy

    def p(self, x, y):
        dx, dy = (x - self.cx) * self.k, (y - self.cy) * self.k
        return f'{self.cx + self.ox + dx * self.c - dy * self.s:.2f} {self.cy + self.oy + dx * self.s + dy * self.c:.2f}'

    def rr(self, x, y, w, h, r, c, **kw):
        p, k = self.p, self.k
        r = round(r * k, 2)
        d = (f'M{p(x + r, y)}L{p(x + w - r, y)}A{r} {r} 0 0 1 {p(x + w, y + r)}'
             f'L{p(x + w, y + h - r)}A{r} {r} 0 0 1 {p(x + w - r, y + h)}'
             f'L{p(x + r, y + h)}A{r} {r} 0 0 1 {p(x, y + h - r)}'
             f'L{p(x, y + r)}A{r} {r} 0 0 1 {p(x + r, y)}Z')
        return path(d, c, **kw)

    def circ(self, x, y, r, c, **kw):
        px, py = self.p(x, y).split()
        return circle(px, py, round(r * self.k, 2), c, **kw)

    def ln(self, points, colour, width, **kw):
        return line('M' + 'L'.join(self.p(x, y) for x, y in points), colour, width, **kw)


def keys(d, colour, width, dash, **kw):
    """A row of square clay keys drawn as one dashed stroke."""
    return path(d, 'none', stroke=colour, stroke_width=width, stroke_dasharray=dash, **kw)


def monitor():
    return (
        # stand
        rect(55, 78, 18, 20, 4, 'olive-dark')
        + rect(36, 96, 56, 10, 5, 'olive-dark')
        + rect(36, 92, 56, 10, 5, 'olive')
        # cabinet with visible thickness
        + rect(18, 21, 92, 64, 13, 'cream-dark')
        + rect(18, 17, 92, 64, 13, 'cream')
        + rect(24, 23, 80, 45, 8, 'charcoal')
        + rect(27, 26, 74, 39, 5, 'aqua')
        # wallpaper: sun and two hills
        + circle(83, 38, 6, 'yellow')
        + path('M27 57Q41 41 56 53Q64 59 72 52Q86 40 101 53V60Q101 65 96 65H32Q27 65 27 60Z', 'olive')
        + path('M27 63Q40 51 56 59Q70 66 84 65H32Q27 65 27 63Z', 'olive-dark')
        # chin controls
        + circle(64, 74.5, 3.2, 'orange')
        + rect(84, 72.5, 14, 4, 2, 'cream-dark')
        + circle(31, 74.5, 2.4, 'olive')
    )


def _laptop(screen):
    lid = 'M31 17H95Q104 17 104 26V78H22V26Q22 17 31 17Z'
    return (
        # lid: rounded on top, square where it meets the deck
        path(lid, 'cream-dark', transform='translate(2.5 2)')
        + path(lid, 'cream')
        + rect(28, 23, 70, 40, 6, 'charcoal')
        + rect(31, 26, 64, 34, 4, 'aqua')
        + screen
        # deck
        + path('M22 79H104L109.5 98Q110 105 103 105H23Q16 105 16.5 98Z', 'cream-dark')
        + path('M22 74H104L109.5 93Q110 100 103 100H23Q16 100 16.5 93Z', 'cream')
        # hinge bar
        + rect(34, 68.5, 58, 7, 3.5, 'olive-dark')
        + keys('M27 81H99', OLIVE, 4.6, '5.6 2.7')
        + keys('M25 87.5H101', OLIVE, 4.6, '6 2.75')
        + rect(52, 92, 22, 5.5, 2.5, 'cream-dark')
    )


def laptop():
    return _laptop(
        rect(35, 30, 32, 24, 3, 'white')
        + rect(35, 30, 32, 6.5, 3, 'orange')
        + line('M40 42H61M40 48H54', OLIVE, 3.2)
        + circle(80, 38, 6, 'yellow')
        + rect(73, 48, 14, 5.5, 2.7, 'olive')
    )


def laptop_remote():
    arrow = 'M38 38H62V30L86 42.5L62 55V47H38Z'
    return _laptop(path(arrow, 'orange-dark', transform='translate(1.5 2)') + path(arrow, 'orange'))


def drive():
    arm = Tilt(0)
    return (
        rect(25, 20, 78, 86, 12, 'cream-dark')
        + rect(25, 16, 78, 86, 12, 'cream')
        # platter
        + circle(64, 49, 29, 'olive-dark')
        + circle(64, 48, 28, 'aqua')
        + circle(64, 48, 18, 'none', stroke=AQUA_DARK, stroke_width=3)
        + circle(64, 48, 9, 'cream')
        + circle(64, 48, 4, 'orange')
        # actuator arm
        + path('M84 84L66 62Q66 55 73 57L94 80Z', 'olive')
        + arm.rr(64, 55, 9, 7, 2, 'charcoal')
        + circle(89, 85, 8, 'yellow')
        + circle(89, 85, 3, 'yellow-dark')
        # label, activity light, screws
        + rect(32, 82, 34, 12, 4, 'orange')
        + line('M38 88H55', WHITE, 4)
        + circle(72, 93, 2.6, 'olive')
        + circle(32, 23, 2.6, 'cream-dark')
        + circle(96, 23, 2.6, 'cream-dark')
        + circle(32, 95, 2.6, 'cream-dark')
    )


def usb():
    t = Tilt(35, 64, 62, 1.13, 0, -1)
    return (
        # key ring through the lanyard hole
        t.circ(64, 100, 7.5, 'none', stroke=OLIVE, stroke_width=4.5)
        # metal plug
        + t.rr(52, 18, 24, 24, 3, 'stone', transform='translate(1.5 2.5)')
        + t.rr(52, 18, 24, 24, 3, 'metal')
        + t.rr(55.5, 23, 6, 8, 1.2, 'charcoal')
        + t.rr(66.5, 23, 6, 8, 1.2, 'charcoal')
        # body
        + t.rr(45, 38, 38, 60, 12, 'orange-dark', transform='translate(2 3.5)')
        + t.rr(45, 38, 38, 60, 12, 'orange')
        + t.rr(45, 38, 38, 11, 5, 'cream')
        # slider button with grip
        + t.rr(54, 55, 20, 24, 7, 'yellow')
        + t.ln([(59, 63), (69, 63)], '#cf9f33', 3.4)
        + t.ln([(59, 70), (69, 70)], '#cf9f33', 3.4)
        # lanyard hole and light
        + t.circ(64, 89, 3.6, 'charcoal')
    )


def printer():
    return (
        # rear tray and fresh paper
        rect(35, 20, 58, 30, 6, 'cream-dark')
        + rect(41, 16, 46, 34, 4, 'white')
        + line('M49 25H79M49 32H72', AQUA_DARK, 3.2)
        # output tray
        + path('M28 84H100L105 99Q106 106 99 106H29Q22 106 23 99Z', 'olive-dark')
        + path('M30 82H98L102 96Q103 101 97 101H31Q25 101 26 96Z', 'olive')
        # body
        + rect(18, 44, 92, 44, 12, 'cream-dark')
        + rect(18, 40, 92, 44, 12, 'cream')
        + rect(34, 40, 60, 6, 3, 'charcoal')
        + rect(41, 36, 46, 8, 2, 'white')
        # controls
        + rect(25, 50, 22, 9, 4, 'aqua')
        + circle(88, 54.5, 3.6, 'yellow')
        + circle(99, 54.5, 3.6, 'orange')
        # output slot and printed page
        + rect(30, 65, 68, 10, 5, 'charcoal')
        + rect(37, 69, 54, 30, 4, 'white')
        + rect(43, 76, 18, 16, 3, 'orange')
        + line('M67 78H84M67 84H84M67 90H78', OLIVE, 3.2)
    )


def keyboard():
    row = lambda y, xs, c: ''.join(rect(x, y, 9, 8, 2.5, c) for x in xs)
    xs = [22 + 12 * i for i in range(7)]
    return (
        line('M64 46C64 34 46 40 45 28C44 19 56 17 60 24', ORANGE, 4.8)
        + rect(16, 48, 94, 56, 11, 'cream-dark')
        + rect(16, 43, 94, 56, 11, 'cream')
        + rect(22, 50, 9, 8, 2.5, 'orange') + row(50, xs[1:], 'olive')
        + row(61, xs[:6], 'olive')
        + row(72, xs[:6], 'olive')
        + rect(94, 61, 9, 19, 2.5, 'yellow')
        + row(83, xs[:2], 'olive') + rect(46, 83, 33, 8, 3, 'aqua') + row(83, xs[5:], 'olive')
    )


def mouse():
    body = 'M60 28C80 28 90 42 90 60V76C90 94 78 102 60 102C42 102 30 94 30 76V60C30 42 40 28 60 28Z'
    return (
        line('M60 30C60 12 85 16 87 30C88 40 100 39 102 28', ORANGE, 4.8)
        + path(body, 'olive-dark', transform='translate(0 4)')
        + path(body, 'olive')
        # two buttons with a seam
        + path('M58 28.2C42 29 31 41 30.2 59H58Z', 'cream')
        + path('M62 28.2C78 29 89 41 89.8 59H62Z', 'cream')
        # wheel
        + rect(54, 35, 12, 20, 6, 'charcoal')
        + rect(56.5, 38, 7, 14, 3.5, 'orange')
        # palm mark
        + circle(60, 82, 5.5, 'yellow')
    )


def smartphone():
    tiles = ''
    colours = ['orange', 'yellow', 'cream', 'cream', 'olive', 'orange']
    for i, c in enumerate(colours):
        tiles += rect(42.5 + 14.5 * (i % 3), 33 + 14 * (i // 3), 11, 11, 3.3, c)
    return (
        rect(87, 34, 8, 17, 3, 'orange')
        + rect(37, 20, 56, 86, 13, 'cream-dark')
        + rect(34, 16, 56, 86, 13, 'cream')
        + rect(38, 20, 48, 78, 9.5, 'aqua')
        + rect(53, 23, 18, 4.8, 2.4, 'charcoal')
        + tiles
        # wallpaper hills and home bar
        + path('M38 77Q50 64 62 72Q74 80 86 67V88.5Q86 98 76.5 98H47.5Q38 98 38 88.5Z', 'olive')
        + path('M38 86Q54 76 72 98H47.5Q38 98 38 88.5Z', 'olive-dark')
        + line('M53 92H71', WHITE, 3.6)
    )


def disc():
    def wedge(a0, a1, r0, r1, c, **kw):
        a0, a1 = math.radians(a0), math.radians(a1)
        pt = lambda a, r: f'{63 + r * math.cos(a):.2f} {60 + r * math.sin(a):.2f}'
        return path(f'M{pt(a0, r0)}L{pt(a0, r1)}A{r1} {r1} 0 0 1 {pt(a1, r1)}L{pt(a1, r0)}A{r0} {r0} 0 0 0 {pt(a0, r0)}Z', c, **kw)
    return (
        circle(64, 64, 42, 'aqua-dark')
        + circle(63, 60, 42, 'cream')
        + circle(63, 60, 37, 'aqua')
        + circle(63, 60, 27, 'none', stroke=AQUA_DARK, stroke_width=3, opacity='.7')
        + wedge(-72, -38, 16, 37, 'white', opacity='.75')
        + wedge(-38, -22, 16, 37, 'yellow', opacity='.8')
        + wedge(108, 142, 16, 37, 'white', opacity='.75')
        + wedge(142, 158, 16, 37, 'orange', opacity='.8')
        + circle(63, 60, 16, 'cream')
        + circle(63, 60, 10.5, 'cream-dark')
        + circle(63, 60, 5.5, 'charcoal')
    )


ART = {
    'monitor': monitor,
    'laptop': laptop,
    'drive': drive,
    'usb': usb,
    'printer': printer,
    'keyboard': keyboard,
    'mouse': mouse,
    'smartphone': smartphone,
    'disc': disc,
    'laptop-remote': laptop_remote,
}
