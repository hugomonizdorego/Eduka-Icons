"""Eduka 1.0 clay artwork: dialog signs, emblems and small symbols. GPL-3.0."""
import math
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_DARK = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_DARK, YELLOW, YELLOW_DARK = '#e0703a', '#b9552a', '#eec14f', '#cf9f33'
OLIVE, OLIVE_DARK, AQUA, AQUA_DARK, CHARCOAL = '#7d8c55', '#5f6c40', '#8fc0c4', '#6a9ea3', '#3f3c37'


def rpoly_d(points, radius):
    """Path data of a polygon whose corners are rounded (radius: one value or one per corner)."""
    n, d = len(points), ''
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * n

    def toward(a, b, r):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        t = min(r, length / 2) / length
        return a[0] + dx * t, a[1] + dy * t

    for i in range(n):
        p0, p1, p2 = points[i - 1], points[i], points[(i + 1) % n]
        a, b = toward(p1, p0, radii[i]), toward(p1, p2, radii[i])
        d += f"{'M' if i == 0 else 'L'}{a[0]:.2f} {a[1]:.2f}Q{p1[0]:.2f} {p1[1]:.2f} {b[0]:.2f} {b[1]:.2f}"
    return d + 'Z'


def rpoly(points, radius, c, **kw):
    return path(rpoly_d(points, radius), c, **kw)


def scaled(points, k, cx, cy):
    return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in points]


def ring(cx, cy, r0, r1, a0, a1, c, **kw):
    """Annular wedge between two radii, angles in degrees (clockwise from east)."""
    a0, a1 = math.radians(a0), math.radians(a1)
    pt = lambda a, r: f'{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}'
    return path(f'M{pt(a0, r0)}L{pt(a0, r1)}A{r1} {r1} 0 0 1 {pt(a1, r1)}L{pt(a1, r0)}A{r0} {r0} 0 0 0 {pt(a0, r0)}Z', c, **kw)


class Tilt:
    """Rotate geometry (not the element) so light and shadow keep one direction."""

    def __init__(self, degrees, cx=64, cy=62, scale=1, dx=0, dy=0):
        a = math.radians(degrees)
        self.c, self.s, self.cx, self.cy = math.cos(a), math.sin(a), cx, cy
        self.k, self.ox, self.oy = scale, dx, dy

    def xy(self, x, y):
        dx, dy = (x - self.cx) * self.k, (y - self.cy) * self.k
        return self.cx + self.ox + dx * self.c - dy * self.s, self.cy + self.oy + dx * self.s + dy * self.c

    def p(self, x, y):
        return '%.2f %.2f' % self.xy(x, y)

    def rr(self, x, y, w, h, r, c, **kw):
        p, k = self.p, self.k
        r = round(r * k, 2)
        d = (f'M{p(x + r, y)}L{p(x + w - r, y)}A{r} {r} 0 0 1 {p(x + w, y + r)}'
             f'L{p(x + w, y + h - r)}A{r} {r} 0 0 1 {p(x + w - r, y + h)}'
             f'L{p(x + r, y + h)}A{r} {r} 0 0 1 {p(x, y + h - r)}'
             f'L{p(x, y + r)}A{r} {r} 0 0 1 {p(x + r, y)}Z')
        return path(d, c, **kw)

    def circ(self, x, y, r, c, **kw):
        px, py = self.xy(x, y)
        return circle(round(px, 2), round(py, 2), round(r * self.k, 2), c, **kw)

    def ln(self, points, colour, width, **kw):
        return line('M' + 'L'.join(self.p(x, y) for x, y in points), colour, round(width * self.k, 2), **kw)


def warning():
    tri = [(63, 9), (116, 99), (10, 99)]
    inner = scaled(tri, .70, 63, 69)
    return (
        # thick cream sign board
        rpoly(tri, 18, 'cream-dark', transform='translate(0 4.5)')
        + rpoly(tri, 18, 'cream')
        # raised yellow face
        + rpoly(inner, 10, 'yellow-dark', transform='translate(0 1.5)')
        + rpoly(inner, 10, 'yellow')
        # exclamation mark
        + path('M55 45.5Q55 38 63 38Q71 38 71 45.5L68.2 69.5Q67.6 74.5 63 74.5Q58.4 74.5 57.8 69.5Z', 'charcoal')
        + circle(63, 85, 6.2, 'charcoal')
        # rivets in the three corners
        + circle(63, 24.5, 2.6, 'orange')
        + circle(26, 91, 2.6, 'orange')
        + circle(100, 91, 2.6, 'orange')
    )


def info():
    bubble = ('M45 17H81Q109 17 109 45V58Q109 86 81 86H60L37 101Q31 104 32 97L34 84'
              'Q17 78 17 58V45Q17 17 45 17Z')
    face = ('M46 23H80Q103 23 103 46V57Q103 80 80 80H58L39.5 92.5L41.5 79.5'
            'Q23 74 23 57V46Q23 23 46 23Z')
    letter = 'M54 47H68.5Q70.5 47 70.5 49V66H75V74H54V66H58.5V55H54Z'
    return (
        # cream speech bubble with a raised aqua face
        path(bubble, 'cream-dark', transform='translate(0 4.5)')
        + path(bubble, 'cream')
        + path(face, 'aqua-dark', transform='translate(0 1.5)')
        + path(face, 'aqua')
        # letter i, raised
        + circle(64.5, 36, 7, 'aqua-dark')
        + path(letter, 'aqua-dark', transform='translate(1.5 2)')
        + circle(63, 34, 7, 'white')
        + path(letter, 'white')
    )


def help_():
    bands = ''.join(ring(63, 59, 30, 42.5, a - 15, a + 15, 'orange') for a in (45, 135, 225, 315))
    mark = 'M51 50Q51 38 63 38Q75 38 75 49Q75 56.5 63 60.5V65.5'
    return (
        # lifebuoy ring
        circle(63, 63.5, 42, 'cream-dark')
        + circle(63, 59, 42, 'cream')
        + bands
        # centre disc with the question mark
        + circle(63, 59, 31, 'aqua-dark')
        + line(mark, '#4f7f84', 10, transform='translate(1 2.5)')
        + circle(64, 82, 5.8, '#4f7f84')
        + line(mark, WHITE, 10)
        + circle(63, 80, 5.8, 'white')
    )


def error():
    def octagon(a, cx=63, cy=59):
        k = a * math.tan(math.radians(22.5))
        return [(cx - k, cy - a), (cx + k, cy - a), (cx + a, cy - k), (cx + a, cy + k),
                (cx + k, cy + a), (cx - k, cy + a), (cx - a, cy + k), (cx - a, cy - k)]
    cross = 'M48 44L78 74M78 44L48 74'
    return (
        rpoly(octagon(42.5), 7, 'orange-dark', transform='translate(0 4.5)')
        + rpoly(octagon(42.5), 7, 'cream')
        + rpoly(octagon(35.5), 5, 'orange')
        + line(cross, ORANGE_DARK, 10.5, transform='translate(1 2.5)')
        + line(cross, WHITE, 10.5)
    )


def check():
    def seal(cx, cy, r0, bump, n=12):
        pts = [(cx + r0 * math.cos(math.radians(360 / n * i - 90)), cy + r0 * math.sin(math.radians(360 / n * i - 90))) for i in range(n)]
        d = f'M{pts[0][0]:.2f} {pts[0][1]:.2f}'
        for x, y in pts[1:] + pts[:1]:
            d += f'A{bump} {bump} 0 0 1 {x:.2f} {y:.2f}'
        return d + 'Z'
    tick = 'M43 60L57 74L83 45'
    return (
        path(seal(63, 63.5, 40, 14), 'olive-dark')
        + path(seal(63, 59, 40, 14), 'olive')
        + circle(63, 59, 32, 'cream')
        + circle(63, 59, 27.5, 'olive')
        + line(tick, OLIVE_DARK, 10.5, transform='translate(1 2.5)')
        + line(tick, WHITE, 10.5)
    )


def power():
    return (
        # switch plate
        rect(18, 21.5, 90, 84, 26, 'cream-dark')
        + rect(18, 17, 90, 84, 26, 'cream')
        # well and push button
        + circle(63, 59, 36.5, 'olive-dark')
        + circle(63, 60.5, 32, 'orange-dark')
        + circle(63, 57.5, 32, 'orange')
        + path('M50.5 46A18.5 18.5 0 1 0 75.5 46', 'none', stroke=WHITE, stroke_width=8.5, stroke_linecap='round')
        + line('M63 37V57', WHITE, 8.5)
        # indicator light and screws
        + circle(97, 27, 3.2, 'yellow')
        + circle(29, 27, 3, 'cream-dark')
        + circle(29, 91, 3, 'cream-dark')
        + circle(97, 91, 3, 'cream-dark')
    )


def lock():
    shackle = 'M42 56V45C42 15.5 84 15.5 84 45V56'
    return (
        # steel shackle with a darker inner side
        line(shackle, '#8b8e7c', 13.5, transform='translate(0 3)')
        + line(shackle, '#b7bca6', 13.5)
        # collars where the shackle enters the body
        + rect(32, 44, 20, 11, 3, 'cream')
        + rect(74, 44, 20, 11, 3, 'cream')
        # body
        + rect(23, 54.5, 80, 51, 14, 'orange-dark')
        + rect(23, 50, 80, 51, 14, 'orange')
        + rect(23, 50, 80, 12.5, 6.25, 'yellow')
        # keyhole plate
        + circle(63, 80, 13.5, 'cream')
        + circle(63, 76.5, 5.2, 'charcoal')
        + path('M60.3 78H65.7L67.5 88.5H58.5Z', 'charcoal')
        # rivets
        + circle(33.5, 91, 3, 'yellow')
        + circle(92.5, 91, 3, 'yellow')
    )


def key():
    t = Tilt(38, 64, 62, 1.02, 3.3, -1.0)
    blade = [(52, 54), (107, 54), (114, 62), (107, 70), (104, 70), (104, 81), (95, 81), (95, 75),
             (90, 75), (90, 85), (80, 85), (80, 70), (52, 70)]
    blade_d = rpoly_d([t.xy(x, y) for x, y in blade], 2.6)
    bow = lambda c, **kw: t.circ(36, 62, 20, 'none', stroke=c, stroke_width=13.6, **kw)
    bx, by = t.xy(36, 62)
    rx, ry, rr = bx - 8, by + 21, 11.5
    ux, uy = 8 / math.hypot(8, 21), -21 / math.hypot(8, 21)
    near, far = (rx + rr * ux, ry + rr * uy), (rx - rr * ux, ry - rr * uy)
    front = f'M{near[0]:.2f} {near[1]:.2f}A{rr} {rr} 0 0 0 {far[0]:.2f} {far[1]:.2f}'
    tag = Tilt(10, rx - 2, ry + 21)
    return (
        # key ring, far half
        circle(round(rx, 2), round(ry, 2), rr, 'none', stroke=OLIVE_DARK, stroke_width=5)
        # name tag
        + tag.rr(rx - 10, ry + 7, 16, 26, 5.5, 'orange-dark', transform='translate(1 3)')
        + tag.rr(rx - 10, ry + 7, 16, 26, 5.5, 'orange')
        + tag.rr(rx - 6.5, ry + 18.5, 9, 10, 2.5, 'cream')
        # key
        + path(blade_d, 'yellow-dark', transform='translate(1 4)')
        + bow(YELLOW_DARK, transform='translate(1 4)')
        + path(blade_d, 'yellow')
        + bow(YELLOW)
        + t.rr(54, 50, 9.5, 24, 3, 'orange')
        + t.ln([(68, 60), (100, 60)], YELLOW_DARK, 3.2)
        # key ring, near half over the bow and the tag
        + line(front, OLIVE, 5)
    )


def star():
    def pts(r_out, r_in, cx=63, cy=63.5):
        out = []
        for i in range(10):
            a = math.radians(-90 + 36 * i)
            r = r_in if i % 2 else r_out
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return out
    big, radii = pts(50.5, 26), [10, 5] * 5
    small = pts(28, 14.5, 62.5, 62.5)

    def sparkle(x, y, s, c):
        k = s * .2
        return path(f'M{x} {y - s}Q{x + k} {y - k} {x + s} {y}Q{x + k} {y + k} {x} {y + s}'
                    f'Q{x - k} {y + k} {x - s} {y}Q{x - k} {y - k} {x} {y - s}Z', c)
    return (
        rpoly(big, radii, 'yellow-dark', transform='translate(0 4.5)')
        + rpoly(big, radii, 'yellow')
        + rpoly(small, [6, 3] * 5, '#f7d978')
        + sparkle(97, 28, 10, 'orange')
    )


def heart():
    shape = ('M63 101C48 92 17 72 17 46C17 28 30 18 43 18C52 18 59 22 63 29'
             'C67 22 74 18 83 18C96 18 109 28 109 46C109 72 78 92 63 101Z')
    seam = ('M63 90C50 82 26.5 65 26.5 46C26.5 34.5 34 27.5 44 27.5C52 27.5 58.5 32 63 41'
            'C67.5 32 74 27.5 82 27.5C92 27.5 99.5 34.5 99.5 46C99.5 65 76 82 63 90Z')
    core = ('M63 77C54 71 38 59 38 47C38 41 42 37.5 47 37.5C53 37.5 58 42 63 51'
            'C68 42 73 37.5 79 37.5C84 37.5 88 41 88 47C88 59 72 71 63 77Z')
    return (
        path(shape, 'orange-dark', transform='translate(0 4.5)')
        + path(shape, 'orange')
        + path(core, '#ee9163')
        + path(seam, 'none', stroke=CREAM, stroke_width=3.2, stroke_dasharray='6 6.5', stroke_linecap='round')
    )


def bell():
    body = 'M63 29C85 29 93 44 93 60V66C93 74 98 79 104 83H22C28 79 33 74 33 66V60C33 44 41 29 63 29Z'
    return (
        # hanging loop
        circle(63, 25, 6.2, 'none', stroke=ORANGE, stroke_width=5.6)
        # clapper
        + circle(63, 94.5, 9.5, 'orange')
        # body
        + path(body, 'yellow-dark', transform='translate(3 2)')
        + path(body, 'yellow')
        + rect(33.5, 56, 59, 8.5, 0, 'orange')
        + ''.join(circle(x, 60.2, 2.6, 'yellow') for x in (43, 53, 63, 73, 83))
        # lip
        + rect(17, 81, 92, 11.5, 5.75, 'yellow-dark')
        + rect(17, 77.5, 92, 11.5, 5.75, 'yellow')
        # shine
        + line('M45 50Q45 40 53.5 36', WHITE, 4.5)
    )


ART = {
    'warning': warning,
    'info': info,
    'help': help_,
    'error': error,
    'check': check,
    'power': power,
    'lock': lock,
    'key': key,
    'star': star,
    'heart': heart,
    'bell': bell,
}
