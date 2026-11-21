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
        + line('M40.5 42H61M40.5 49H54', OLIVE, 4)
        + circle(80, 38, 6, 'yellow')
        + rect(73, 48, 14, 5.5, 2.7, 'olive')
    )


def laptop_remote():
    arrow = 'M38 38H62V30L86 42.5L62 55V47H38Z'
    return _laptop(path(arrow, 'orange-dark', transform='translate(1.5 2)') + path(arrow, 'orange'))


def drive():
    arm = Tilt(0)
    return (
        rect(21, 20, 86, 86, 13, 'cream-dark')
        + rect(21, 16, 86, 86, 13, 'cream')
        # platter
        + circle(62, 50, 31, 'olive-dark')
        + circle(62, 49, 30, 'aqua')
        + circle(62, 49, 19.5, 'none', stroke=AQUA_DARK, stroke_width=4)
        + circle(62, 49, 10, 'cream')
        + circle(62, 49, 4.5, 'orange')
        # actuator arm
        + path('M87 85L64 63Q63 55 71 57L98 80Z', 'olive')
        + arm.rr(61, 55, 10, 8, 2.5, 'charcoal')
        + circle(93, 86, 8.5, 'yellow')
        + circle(93, 86, 3.2, 'yellow-dark')
        # label, activity light, screws
        + rect(28, 83, 38, 13, 4.5, 'orange')
        + line('M35 89.5H55', WHITE, 4)
        + circle(73, 94, 3, 'olive')
        + circle(29, 24, 2.8, 'cream-dark')
        + circle(99, 24, 2.8, 'cream-dark')
    )


def usb():
    t = Tilt(48, 64, 58, 1.04, -1.7, 1.5)
    return (
        # metal plug
        t.rr(48, 12, 32, 28, 3.5, 'stone', transform='translate(1.5 3)')
        + t.rr(48, 12, 32, 28, 3.5, 'metal')
        + t.rr(52.5, 17, 9, 10, 1.5, 'charcoal')
        + t.rr(66.5, 17, 9, 10, 1.5, 'charcoal')
        # body
        + t.rr(39, 32, 50, 68, 15, 'orange-dark', transform='translate(2 4)')
        + t.rr(39, 32, 50, 68, 15, 'orange')
        + t.rr(39, 32, 50, 13, 6, 'cream')
        # slider button with grip
        + t.rr(51, 53, 26, 28, 8.5, 'yellow-dark', transform='translate(1 2)')
        + t.rr(51, 53, 26, 28, 8.5, 'yellow')
        + t.ln([(58, 63), (70, 63)], '#cf9f33', 4)
        + t.ln([(58, 71), (70, 71)], '#cf9f33', 4)
        # lanyard hole
        + t.circ(64, 90.5, 4.2, 'charcoal')
    )


def printer():
    return (
        # rear tray and fresh paper
        rect(35, 20, 58, 30, 6, 'cream-dark')
        + rect(41, 16, 46, 34, 4, 'white')
        + line('M49 24.5H79M49 31.5H70', AQUA_DARK, 4)
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
        + line('M68 77H84M68 84H84M68 91H77', OLIVE, 4)
    )


def keyboard():
    row = lambda y, xs, c: ''.join(rect(x, y, 9.5, 9, 2.6, c) for x in xs)
    xs = [22 + 12 * i for i in range(7)]
    return (
        line('M60 42C60 30 78 34 80 25C81 19 88 17 94 20', ORANGE, 5)
        + rect(16, 43, 94, 61, 12, 'cream-dark')
        + rect(16, 38, 94, 61, 12, 'cream')
        + rect(22, 45.5, 9.5, 9, 2.6, 'orange') + row(45.5, xs[1:], 'olive')
        + row(57.5, xs[:6], 'olive')
        + row(69.5, xs[:6], 'olive')
        + rect(94, 57.5, 9.5, 21, 2.6, 'yellow')
        + row(81.5, xs[:2], 'olive') + rect(46, 81.5, 33.5, 9, 3, 'aqua') + row(81.5, xs[5:], 'olive')
    )


def mouse():
    body = 'M61 25C85 25 98 41 98 62V73C98 93 84 102 61 102C38 102 24 93 24 73V62C24 41 37 25 61 25Z'
    return (
        line('M61 29C60 17 80 15 84 24C87 31 98 33 103 24', ORANGE, 5)
        + path(body, 'olive-dark', transform='translate(0 4)')
        + path(body, 'olive')
        # two buttons with a seam
        + path('M58.8 25.1C38 26 25 41 24.1 60.5H58.8Z', 'cream')
        + path('M63.2 25.1C84 26 97 41 97.9 60.5H63.2Z', 'cream')
        # wheel
        + rect(53.5, 32, 15, 23, 7.5, 'charcoal')
        + rect(56.75, 35.5, 8.5, 16, 4.25, 'orange')
        # palm mark
        + circle(61, 82, 6.5, 'yellow')
    )


def smartphone():
    tiles = ''
    colours = ['orange', 'yellow', 'cream', 'cream', 'olive', 'orange']
    for i, c in enumerate(colours):
        tiles += rect(38.5 + 16 * (i % 3), 32.5 + 15.5 * (i // 3), 12.5, 12.5, 3.6, c)
    return (
        rect(89, 35, 8.5, 18, 3.2, 'orange')
        + rect(33, 20, 62, 86, 14, 'cream-dark')
        + rect(30, 16, 62, 86, 14, 'cream')
        + rect(34, 20, 54, 78, 10.5, 'aqua')
        + rect(51, 23, 20, 5, 2.5, 'charcoal')
        + tiles
        # wallpaper hills and home bar
        + path('M34 77Q47 63 61 72Q75 81 88 66V87.5Q88 98 77.5 98H44.5Q34 98 34 87.5Z', 'olive')
        + path('M34 85Q52 75 73 98H44.5Q34 98 34 87.5Z', 'olive-dark')
        + line('M51 92H71', WHITE, 4)
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
        + circle(63, 60, 27, 'none', stroke=AQUA_DARK, stroke_width=4, opacity='.7')
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
