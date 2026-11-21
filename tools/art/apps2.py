"""Eduka-Icons 1.0 clay artwork: applications, second group.

film, video-editor, theme, executable, tools, reboot, contacts, archive-box,
store-bag-download, shield-check, clipboard, dictionary, maps, translate,
screenshot, remote-desktop, virtual-machine, disk-usage, backup, bootable-usb.
Every function returns an SVG fragment on the 128 x 128 grid; tools/clay.py
sculpts each shape element separately. GPL-3.0.
"""
import math
import re
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_DARK = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_DARK, YELLOW, YELLOW_DARK = '#e0703a', '#b9552a', '#eec14f', '#cf9f33'
OLIVE, OLIVE_DARK, AQUA, AQUA_DARK, CHARCOAL = '#7d8c55', '#5f6c40', '#8fc0c4', '#6a9ea3', '#3f3c37'

_TOKEN = re.compile(r'[MLHVQCAZ]|-?\d*\.?\d+')
_ARGS = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'Q': 4, 'C': 6, 'A': 7, 'Z': 0}


class Tilt:
    """Rotate geometry (not the element) so light and shadow keep one direction."""

    def __init__(self, degrees, cx=64, cy=62, scale=1, dx=0, dy=0):
        a = math.radians(degrees)
        self.deg = degrees
        self.c, self.s, self.cx, self.cy = math.cos(a), math.sin(a), cx, cy
        self.k, self.ox, self.oy = scale, dx, dy

    def p(self, x, y):
        dx, dy = (x - self.cx) * self.k, (y - self.cy) * self.k
        return f'{self.cx + self.ox + dx * self.c - dy * self.s:.2f} {self.cy + self.oy + dx * self.s + dy * self.c:.2f}'

    def d(self, d):
        """Transform a path made of absolute M L H V Q C A Z commands."""
        tokens, out, i, x, y = _TOKEN.findall(d), [], 0, 0.0, 0.0
        command = 'M'
        while i < len(tokens):
            if tokens[i] in _ARGS:
                command = tokens[i]
                i += 1
                if command == 'Z':
                    out.append('Z')
                    continue
            n = _ARGS[command]
            v = [float(t) for t in tokens[i:i + n]]
            i += n
            if command == 'H':
                x = v[0]
                out.append('L' + self.p(x, y))
            elif command == 'V':
                y = v[0]
                out.append('L' + self.p(x, y))
            elif command == 'A':
                x, y = v[5], v[6]
                out.append(f'A{v[0] * self.k:.2f} {v[1] * self.k:.2f} {v[2] + self.deg:.1f} {int(v[3])} {int(v[4])} {self.p(x, y)}')
            else:
                pairs = [self.p(v[j], v[j + 1]) for j in range(0, n, 2)]
                x, y = v[-2], v[-1]
                out.append(command + ' '.join(pairs))
                if command == 'M':
                    command = 'L'
        return ''.join(out)

    def path(self, d, c, **kw):
        return path(self.d(d), c, **kw)

    def rr(self, x, y, w, h, r, c, **kw):
        return self.path(f'M{x + r} {y}H{x + w - r}A{r} {r} 0 0 1 {x + w} {y + r}V{y + h - r}A{r} {r} 0 0 1 {x + w - r} {y + h}'
                         f'H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}V{y + r}A{r} {r} 0 0 1 {x + r} {y}Z', c, **kw)

    def circ(self, x, y, r, c, **kw):
        px, py = self.p(x, y).split()
        return circle(px, py, round(r * self.k, 2), c, **kw)

    def ln(self, d, colour, width, **kw):
        return line(self.d(d), colour, round(width * self.k, 2), **kw)


def dashes(d, colour, width, dash, **kw):
    """A row of square clay blocks drawn as one dashed stroke."""
    return path(d, 'none', stroke=colour, stroke_width=width, stroke_dasharray=dash, **kw)


def shift(dx, dy):
    return f'translate({dx} {dy})'


def polar(cx, cy, r, degrees):
    a = math.radians(degrees)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def wedge(cx, cy, a0, a1, r0, r1, c, **kw):
    """Ring segment from angle a0 to a1 (degrees, clockwise on screen)."""
    pt = lambda a, r: '{:.2f} {:.2f}'.format(*polar(cx, cy, r, a))
    big = 1 if (a1 - a0) % 360 > 180 else 0
    return path(f'M{pt(a0, r0)}L{pt(a0, r1)}A{r1} {r1} 0 {big} 1 {pt(a1, r1)}L{pt(a1, r0)}A{r0} {r0} 0 {big} 0 {pt(a0, r0)}Z', c, **kw)


def cog(cx, cy, r_out, r_in, c, teeth=8, **kw):
    points, step = [], 360 / teeth
    for i in range(teeth):
        a = i * step
        for da, r in ((-step * .31, r_in), (-step * .17, r_out), (step * .17, r_out), (step * .31, r_in)):
            points.append('{:.2f} {:.2f}'.format(*polar(cx, cy, r, a + da)))
    return path('M' + 'L'.join(points) + 'Z', c, **kw)


def arc_arrow(cx, cy, r, a0, a1, width, colour, head=(13, 16), **kw):
    """Thick clockwise arc from a0 to a1 with an arrow head at a1."""
    pt = lambda a, rr=r: '{:.2f} {:.2f}'.format(*polar(cx, cy, rr, a))
    big = 1 if (a1 - a0) % 360 > 180 else 0
    half, length = head
    ex, ey = polar(cx, cy, r, a1)
    tx, ty = -math.sin(math.radians(a1)), math.cos(math.radians(a1))
    tip = f'{ex + tx * length:.2f} {ey + ty * length:.2f}'
    return (line(f'M{pt(a0)}A{r} {r} 0 {big} 1 {pt(a1)}', colour, width, **kw)
            + path(f'M{pt(a1, r - half)}L{tip}L{pt(a1, r + half)}Z', colour, stroke=colour, stroke_width=3,
                   stroke_linejoin='round', **kw))


# --------------------------------------------------------------------------
def film():
    """Film reel with five windows and a strip of frames running off it."""
    cx, cy = 55, 52
    windows = ''.join(circle(*['{:.2f}'.format(v) for v in polar(cx, cy, 19.5, -90 + 72 * i)], 7.6, 'charcoal') for i in range(5))
    return (
        # strip leaving the reel
        rect(48, 80, 62, 26, 5, 'ink')
        + rect(48, 77, 62, 26, 5, 'charcoal')
        + dashes('M77 81.2H108M53 98.8H108', CREAM, 3.2, '3.4 4.4')
        + rect(69, 85, 16, 10.5, 2.5, 'aqua')
        + rect(89.5, 85, 16, 10.5, 2.5, 'yellow')
        # reel flange
        + circle(cx + 2, cy + 4, 35.5, 'cream-dark')
        + circle(cx, cy, 35.5, 'cream')
        + circle(cx, cy, 31, 'none', stroke=CREAM_DARK, stroke_width=3)
        + windows
        + circle(cx, cy, 8.5, 'orange')
        + circle(cx, cy, 3.4, 'cream')
    )


def video_editor():
    """Editing desk: film strip on top, two tracks of clips and a playhead."""
    return (
        rect(18, 23, 92, 83, 12, 'cream-dark')
        + rect(18, 18, 92, 83, 12, 'cream')
        # source strip
        + rect(24, 24, 80, 24, 6, 'charcoal')
        + rect(29, 29, 20, 14, 3, 'aqua')
        + rect(54, 29, 20, 14, 3, 'orange')
        + path('M61 32L68.5 36L61 40Z', 'white')
        + rect(79, 29, 20, 14, 3, 'aqua')
        # tracks
        + rect(24, 60, 44, 12, 4, 'aqua-dark')
        + rect(71, 60, 22, 12, 4, 'yellow')
        + rect(36, 76, 24, 12, 4, 'yellow')
        + rect(63, 76, 41, 12, 4, 'olive')
        + dashes('M26 94H102', CREAM_DARK, 3.6, '3.5 5.5')
        # playhead
        + line('M54 60V95', ORANGE_DARK, 4.4)
        + rect(46, 50, 16, 10.5, 4, 'orange')
    )


def theme():
    """Paint roller resting over a card of colour swatches."""
    return (
        # swatch card
        rect(22, 46, 60, 60, 8, 'cream-dark')
        + rect(19, 42, 60, 60, 8, 'cream')
        + rect(26, 55, 46, 11, 4, 'yellow')
        + rect(26, 70, 46, 11, 4, 'olive')
        + rect(26, 85, 46, 11, 4, 'aqua')
        # wire frame and grip
        + line('M94 30H101Q107 30 107 36V50Q107 56 101 56H98Q92 56 92 62V70', OLIVE_DARK, 5)
        + rect(85, 69, 14, 37, 7, 'olive-dark')
        + rect(85, 66, 14, 37, 7, 'olive')
        + rect(85, 66, 14, 7, 3.5, 'yellow')
        # roller: core caps and paint-loaded cover
        + rect(16, 21, 80, 19, 8, 'cream')
        + rect(21, 20, 70, 27, 10, 'orange-dark')
        + rect(21, 16, 70, 27, 10, 'orange')
        + line('M30 23.5H72', '#f2a27a', 3.4)
    )


def executable():
    """Program window with a cog that carries a small run mark."""
    return (
        rect(18, 24, 92, 82, 12, 'cream-dark')
        + rect(18, 19, 92, 82, 12, 'cream')
        + path('M30 19H98Q110 19 110 31V40H18V31Q18 19 30 19Z', 'olive')
        + circle(30, 29.5, 3.6, 'cream')
        + circle(41, 29.5, 3.6, 'yellow')
        + circle(52, 29.5, 3.6, 'orange')
        + rect(78, 27, 22, 5, 2.5, 'olive-dark')
        + cog(65.5, 73, 25, 18.5, 'orange-dark')
        + cog(64, 70, 25, 18.5, 'orange')
        + circle(64, 70, 10.5, 'cream')
        + path('M60.5 64.5L70 70L60.5 75.5Z', 'olive-dark', stroke=OLIVE_DARK, stroke_width=1.5, stroke_linejoin='round')
    )


def tools():
    """Crossed open-end wrench and screwdriver."""
    w = Tilt(-42, 64, 60, 1.08, 0, 1)
    s = Tilt(42, 64, 60, 1.08, 0, 1)
    wrench = ('M56.5 12.5V28Q56.5 32 60.5 32H67.5Q71.5 32 71.5 28V12.5A19 19 0 0 1 71 47.7V85.1'
              'A13 13 0 1 1 57 85.1V47.7A19 19 0 0 1 56.5 12.5Z'
              'M64 90.5A5.5 5.5 0 1 0 64 101.5A5.5 5.5 0 1 0 64 90.5Z')
    blade = 'M60.5 62V25L58 15Q58 12 61 12H67Q70 12 70 15L67.5 25V62Z'
    return (
        w.path(wrench, 'aqua-dark', fill_rule='evenodd', transform=shift(1.5, 3.5))
        + w.path(wrench, 'aqua', fill_rule='evenodd')
        + s.path(blade, 'stone', transform=shift(1.5, 3))
        + s.path(blade, 'metal')
        + s.rr(53, 66, 22, 42, 10, 'orange-dark', transform=shift(1.5, 3.5))
        + s.rr(53, 66, 22, 42, 10, 'orange')
        + s.rr(55.5, 58, 17, 11, 3.5, 'yellow')
        + s.ln('M59.5 79V99', ORANGE_DARK, 3.4)
        + s.ln('M68.5 79V99', ORANGE_DARK, 3.4)
    )


def reboot():
    """One thick clockwise arrow around a small power knob."""
    return (
        arc_arrow(62, 65, 32.5, 8, 290, 16, ORANGE_DARK, head=(13.5, 17))
        + arc_arrow(62, 61.5, 32.5, 8, 290, 16, ORANGE, head=(13.5, 17))
        + circle(62, 64.5, 14.5, 'cream-dark')
        + circle(62, 61.5, 14.5, 'cream')
        + rect(58.5, 51.5, 7, 15, 3.5, 'olive')
    )


def contacts():
    """Address book with index tabs and a person on the cover."""
    return (
        rect(25, 21, 72, 85, 9, 'olive-dark')
        + rect(27, 21, 67, 80, 6, 'paper')
        # index tabs
        + rect(86, 27, 21, 16, 5, 'orange')
        + rect(86, 47, 21, 16, 5, 'yellow')
        + rect(86, 67, 21, 16, 5, 'aqua')
        # cover and spine
        + rect(19, 16, 72, 85, 9, 'olive')
        + path('M28 16H34V101H28Q19 101 19 92V25Q19 16 28 16Z', 'olive-dark')
        + circle(26.5, 34, 3.2, 'yellow')
        + circle(26.5, 83, 3.2, 'yellow')
        # person
        + path('M42 85Q42 64 62 64Q82 64 82 85Q82 89 78 89H46Q42 89 42 85Z', 'cream')
        + circle(62, 46, 12.5, 'cream')
    )


def archive_box():
    """Storage box with a lid, a zipper down the front and a label."""
    return (
        rect(23, 52, 82, 54, 9, 'yellow-dark')
        + rect(23, 47, 82, 54, 9, 'yellow')
        + rect(29, 74, 20, 17, 4, 'white')
        + line('M34 80H44M34 86H41', ORANGE, 3)
        + rect(80, 70, 18, 8, 4, 'yellow-dark')
        # lid
        + rect(17, 30, 94, 25, 8, 'cream-dark')
        + rect(17, 25, 94, 25, 8, 'cream')
        # zipper
        + rect(56, 25, 16, 76, 3, 'olive')
        + dashes('M64 29V98', CREAM, 7, '3.2 3.4')
        + rect(55, 51, 18, 12, 4, 'orange')
        + rect(58.5, 60, 11, 22, 5.5, 'orange-dark')
        + rect(58.5, 58, 11, 22, 5.5, 'orange')
        + circle(64, 73, 2.6, 'cream')
    )


def store_bag_download():
    """Shopping bag with a big download arrow."""
    arrow = 'M48 58H64V75H75L56 96L37 75H48Z'
    return (
        line('M47 48V36C47 18 79 18 79 36V48', YELLOW_DARK, 6.5)
        # side gusset and front
        + path('M32 42H96L105 47L108 97Q108 106 100 106H40Z', 'olive')
        + path('M22 42H90L94 97Q94.5 106 86 106H26Q17.5 106 18 97Z', 'cream')
        + path('M22 42H90L90.7 51H21.3Z', 'cream-dark')
        + line('M40 50V36C40 16 72 16 72 36V50', YELLOW, 6.5)
        + circle(40, 50, 4.6, 'olive')
        + circle(72, 50, 4.6, 'olive')
        + path(arrow, 'orange-dark', transform=shift(1.5, 3), stroke=ORANGE_DARK, stroke_width=3, stroke_linejoin='round')
        + path(arrow, 'orange', stroke=ORANGE, stroke_width=3, stroke_linejoin='round')
    )


def _shield(top, bottom, half, shoulder):
    cx = 64
    mid = top + (bottom - top) * .50
    return (f'M{cx} {top}Q{cx + half * .5} {shoulder} {cx + half - 3} {shoulder}Q{cx + half} {shoulder} {cx + half} {shoulder + 3}'
            f'V{mid}Q{cx + half} {bottom - (bottom - top) * .17} {cx} {bottom}Q{cx - half} {bottom - (bottom - top) * .17} {cx - half} {mid}'
            f'V{shoulder + 3}Q{cx - half} {shoulder} {cx - half + 3} {shoulder}Q{cx - half * .5} {shoulder} {cx} {top}Z')


def shield_check():
    """Cream-rimmed olive shield with a bold check."""
    outer, inner = _shield(15, 102, 40, 27), _shield(26.5, 91.5, 30, 35.5)
    check = 'M47 59L59 71L82 46'
    return (
        path(outer, 'cream-dark', transform=shift(0, 4))
        + path(outer, 'cream')
        + path(inner, 'olive-dark')
        + path(inner, 'olive', transform=shift(0, 2.5))
        + line(check, YELLOW_DARK, 10.5, transform=shift(0, 3.5))
        + line(check, YELLOW, 10.5)
    )


def clipboard():
    """Clipboard with a spring clip and a ticked list."""
    clip = 'M45 38V29Q45 25 49 25H55Q55 16 64 16Q73 16 73 25H79Q83 25 83 29V38Q83 41 80 41H48Q45 41 45 38Z'
    return (
        rect(24, 28, 80, 78, 10, 'aqua-dark')
        + rect(24, 24, 80, 78, 10, 'aqua')
        + rect(34, 37, 62, 59, 4, 'cream-dark', transform='rotate(4 64 66)')
        + rect(32, 35, 64, 60, 4, 'white')
        + rect(39, 50, 10, 10, 3, 'orange')
        + line('M56 55H88', OLIVE, 4)
        + rect(39, 65, 10, 10, 3, 'yellow')
        + line('M56 70H88', OLIVE, 4)
        + rect(39, 80, 10, 10, 3, 'olive')
        + line('M56 85H77', OLIVE, 4)
        + path(clip, 'yellow-dark', transform=shift(0, 3))
        + path(clip, 'yellow')
        + circle(64, 26, 3.6, 'charcoal')
    )


def dictionary():
    """Thick closed book with a ribbon and a magnifier on the cover."""
    return (
        line('M86 89L100 102', OLIVE_DARK, 9)
        + rect(26, 22, 72, 84, 9, 'orange-dark')
        + rect(27, 22, 67, 79, 6, 'paper')
        + rect(19, 16, 72, 84, 9, 'orange')
        + path('M28 16H34V100H28Q19 100 19 91V25Q19 16 28 16Z', 'orange-dark')
        + rect(19, 28, 15, 5.5, 2, 'yellow')
        + rect(19, 83, 15, 5.5, 2, 'yellow')
        # title plate and ribbon
        + line('M42 30H62M42 40H55', CREAM, 5)
        + path('M70 16H82V47L76 41L70 47Z', 'yellow')
        # magnifier
        + line('M84 87L99 101', OLIVE_DARK, 9)
        + circle(72, 77, 19, 'cream-dark')
        + circle(70.5, 74.5, 19, 'cream')
        + circle(70.5, 74.5, 13, 'aqua')
        + line('M63 71Q65 66.5 70 66', WHITE, 3.4)
    )


def maps():
    """Three-fold map with water, a park, a route and a location pin."""
    p1, p2, p3 = 'M17 48L46 38V96L17 106Z', 'M46 38L80 48V106L46 96Z', 'M80 48L109 38V96L80 106Z'
    pin = 'M66 79Q48 55 48 40A18 18 0 1 1 84 40Q84 55 66 79Z'
    return (
        path('M17 48L46 38L80 48L109 38V96L80 106L46 96L17 106Z', 'cream-dark', transform=shift(0, 3))
        + path(p1, 'cream')
        + path(p2, 'sand')
        + path(p3, 'cream')
        + path('M17 80Q32 72 46 78V96L17 106Z', 'aqua')
        + path('M46 78Q64 86 80 84V106L46 96Z', 'aqua-dark')
        + path('M80 84Q96 78 109 66V96L80 106Z', 'olive')
        + circle(31, 62, 6.5, 'olive')
        + dashes('M99 50Q92 66 76 78', ORANGE, 4, '5 5', stroke_linecap='round')
        + path(pin, 'orange-dark', transform=shift(2, 3))
        + path(pin, 'orange')
        + circle(66, 40, 7, 'cream')
    )


def translate():
    """Two overlapping speech tiles carrying different scripts."""
    a = 'M28 16H62Q74 16 74 28V54Q74 66 62 66H42L28 79Q24 82 24 77V65.3Q16 63 16 54V28Q16 16 28 16Z'
    b = 'M64 44H98Q110 44 110 56V80Q110 89.5 102 91.5V99Q102 104 98.5 101L86 92H64Q52 92 52 80V56Q52 44 64 44Z'
    return (
        path(a, 'aqua-dark', transform=shift(0, 3.5))
        + path(a, 'aqua')
        + line('M33 55L45 27L57 55M38.5 45H51.5', WHITE, 5.5)
        + path(b, 'orange-dark', transform=shift(0, 3.5))
        + path(b, 'orange')
        + line('M67 59H97M82 52V59M71 82Q88 78 92 65M72 65Q76 78 94 82', WHITE, 5)
        # swap arrows
        + line('M83 22Q98 22 98 33', OLIVE, 5)
        + path('M91.5 32H104.5L98 40Z', OLIVE, stroke=OLIVE, stroke_width=2.5, stroke_linejoin='round')
        + line('M44 99Q30 99 30 91', OLIVE, 5)
        + path('M23.5 92H36.5L30 84Z', OLIVE, stroke=OLIVE, stroke_width=2.5, stroke_linejoin='round')
    )


def screenshot():
    """Captured view framed by four corner brackets with a shutter button."""
    brackets = 'M20 41V28Q20 20 28 20H41M85 20H98Q106 20 106 28V41M20 78V91Q20 99 28 99H41M85 99H98Q106 99 106 91V78'
    return (
        rect(29, 32, 68, 58, 7, 'aqua-dark')
        + rect(29, 29, 68, 58, 7, 'aqua')
        + circle(84, 42, 5.5, 'yellow')
        + path('M29 74Q44 60 60 70Q76 80 97 64V80Q97 87 90 87H36Q29 87 29 80Z', 'olive')
        + line(brackets, ORANGE_DARK, 8, transform=shift(0, 3))
        + line(brackets, ORANGE, 8)
        + circle(63, 61, 14, 'cream-dark')
        + circle(63, 58.5, 14, 'white')
        + circle(63, 58.5, 8, 'orange')
    )


def _screen(x, y, w, h, inner):
    """Small monitor: cabinet x,y,w,h plus neck and foot below it."""
    cx = x + w / 2
    return (
        rect(cx - 6, y + h - 2, 12, 10, 2, 'olive-dark')
        + rect(cx - 16, y + h + 6, 32, 7, 3.5, 'olive')
        + rect(x, y + 3, w, h, 8, 'cream-dark')
        + rect(x, y, w, h, 8, 'cream')
        + rect(x + 5, y + 5, w - 10, h - 15, 4, 'aqua')
        + inner
        + circle(cx, y + h - 5.2, 2.6, 'orange')
    )


def remote_desktop():
    """Two monitors, the far one reaching the near one through an arrow."""
    far = _screen(16, 16, 56, 42, circle(57, 28, 4.5, 'yellow') + path('M21 43Q34 30 46 39Q56 46 67 38V44Q67 48 63 48H25Q21 48 21 44Z', 'olive'))
    near = _screen(52, 51, 58, 42, rect(63, 61, 36, 18, 3, 'white') + rect(63, 61, 36, 6, 3, 'orange'))
    return (
        far
        + line('M79 27H88Q96 27 96 35V37', ORANGE, 6.5)
        + path('M88 36H104L96 46Z', ORANGE, stroke=ORANGE, stroke_width=3, stroke_linejoin='round')
        + near
    )


def virtual_machine():
    """A complete little computer living inside a host frame."""
    return (
        rect(16, 21, 94, 85, 14, 'olive-dark')
        + rect(16, 16, 94, 85, 14, 'olive')
        + rect(24, 24, 78, 62, 8, 'olive-dark')
        # guest computer
        + rect(59, 68, 10, 10, 2, 'cream-dark')
        + rect(47, 75, 34, 7, 3.5, 'cream')
        + rect(35, 33, 58, 40, 7, 'cream-dark')
        + rect(35, 30, 58, 40, 7, 'cream')
        + rect(40, 35, 48, 26, 4, 'aqua')
        # the guest shows a cube
        + path('M64 37.5L75 43L64 48.5L53 43Z', 'yellow')
        + path('M53 43L64 48.5V59.5L53 54Z', 'orange')
        + path('M64 48.5L75 43V54L64 59.5Z', 'orange-dark')
        + circle(64, 65.5, 2.5, 'olive')
        # host controls
        + circle(31, 93.5, 3, 'yellow')
        + circle(41, 93.5, 3, 'cream')
        + rect(76, 91, 22, 5, 2.5, 'cream')
    )


def disk_usage():
    """Disk drawn as a donut chart with one slice pulled out."""
    cx, cy = 62, 61
    ox, oy = polar(0, 0, 4.5, -45)
    return (
        circle(cx + 1, cy + 4, 42, 'cream-dark')
        + circle(cx, cy, 42, 'cream')
        + wedge(cx, cy, 2, 88, 15, 36, 'olive')
        + wedge(cx, cy, 92, 148, 15, 36, 'aqua')
        + wedge(cx, cy, 152, 268, 15, 36, 'yellow')
        + wedge(cx + ox, cy + oy, -88, -2, 15, 38, 'orange-dark', transform=shift(1, 3))
        + wedge(cx + ox, cy + oy, -88, -2, 15, 38, 'orange')
        + circle(cx, cy, 11, 'cream-dark')
        + circle(cx, cy, 5, 'charcoal')
    )


def backup():
    """External drive under a dial that winds back in time."""
    return (
        # drive
        rect(17, 66, 94, 40, 10, 'cream-dark')
        + rect(17, 61, 94, 40, 10, 'cream')
        + rect(24, 82, 80, 12, 5, 'olive')
        + circle(32, 88, 3, 'yellow')
        + dashes('M70 88H98', CREAM, 4.5, '3.5 4')
        # time dial
        + circle(64, 48, 27, 'cream-dark')
        + circle(64, 45, 27, 'white')
        + arc_arrow(64, 45, 21.5, -60, 196, 9.5, AQUA_DARK, head=(9, 12))
        + line('M64 33V45L73 51', ORANGE, 4.5)
        + circle(64, 45, 3.4, 'charcoal')
    )


def bootable_usb():
    """USB stick charged with a boot spark."""
    t = Tilt(35, 64, 62, 1.1, 2, 0)
    star = lambda x, y, r: path(f'M{x} {y - r}Q{x + r * .22} {y - r * .22} {x + r} {y}Q{x + r * .22} {y + r * .22} {x} {y + r}'
                                f'Q{x - r * .22} {y + r * .22} {x - r} {y}Q{x - r * .22} {y - r * .22} {x} {y - r}Z', 'yellow')
    return (
        t.rr(52, 18, 24, 24, 3, 'stone', transform=shift(1.5, 2.5))
        + t.rr(52, 18, 24, 24, 3, 'metal')
        + t.rr(55.5, 23, 6, 8, 1.2, 'charcoal')
        + t.rr(66.5, 23, 6, 8, 1.2, 'charcoal')
        + t.rr(45, 38, 38, 62, 12, 'olive-dark', transform=shift(2, 3.5))
        + t.rr(45, 38, 38, 62, 12, 'olive')
        + t.rr(45, 38, 38, 11, 5, 'cream')
        + t.path('M68 53L54 74H63L59 92L75 68H66Z', 'yellow', stroke=YELLOW, stroke_width=2.5, stroke_linejoin='round')
        + star(34, 34, 11)
        + star(98, 92, 8)
    )


ART = {
    'film': film,
    'video-editor': video_editor,
    'theme': theme,
    'executable': executable,
    'tools': tools,
    'reboot': reboot,
    'contacts': contacts,
    'archive-box': archive_box,
    'store-bag-download': store_bag_download,
    'shield-check': shield_check,
    'clipboard': clipboard,
    'dictionary': dictionary,
    'maps': maps,
    'translate': translate,
    'screenshot': screenshot,
    'remote-desktop': remote_desktop,
    'virtual-machine': virtual_machine,
    'disk-usage': disk_usage,
    'backup': backup,
    'bootable-usb': bootable_usb,
}
