"""Eduka-Icons 1.0 clay artwork: more hardware devices.

tablet, scanner, webcam, television, media-player, router, chip, memory,
sdcard, floppy, camcorder, speaker, ups, joystick, projector, smartwatch,
drawing-tablet, network-card.
Every function returns an SVG fragment on the 128 x 128 grid; tools/clay.py
sculpts each shape element separately. GPL-3.0.
"""
import math
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_DARK = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_DARK, YELLOW, YELLOW_DARK = '#e0703a', '#b9552a', '#eec14f', '#cf9f33'
OLIVE, OLIVE_DARK, AQUA, AQUA_DARK, CHARCOAL = '#7d8c55', '#5f6c40', '#8fc0c4', '#6a9ea3', '#3f3c37'
METAL = '#b0b6a0'


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

    def poly(self, points, c, **kw):
        return path('M' + 'L'.join(self.p(x, y) for x, y in points) + 'Z', c, **kw)

    def circ(self, x, y, r, c, **kw):
        px, py = self.p(x, y).split()
        return circle(px, py, round(r * self.k, 2), c, **kw)

    def ln(self, points, colour, width, **kw):
        return line('M' + 'L'.join(self.p(x, y) for x, y in points), colour, width, **kw)


def ellipse(cx, cy, rx, ry, c, **kw):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    fill = c if c == 'none' or c.startswith('#') else f'url(#{c})'
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'


def arc(cx, cy, r, a0, a1, colour, width, **kw):
    """Round-capped circular arc, angles in degrees clockwise from 12 o'clock."""
    pt = lambda a: f'{cx + r * math.sin(math.radians(a)):.2f} {cy - r * math.cos(math.radians(a)):.2f}'
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return line(f'M{pt(a0)}A{r} {r} 0 {large} 1 {pt(a1)}', colour, width, **kw)


# --------------------------------------------------------------------------
def tablet():
    """Landscape tablet: home screen with a weather card, app tiles and a dock."""
    tiles = ''
    colours = ['orange', 'yellow', 'cream', 'olive', 'cream', 'orange', 'yellow', 'olive', 'cream']
    for i, c in enumerate(colours):
        tiles += rect(61 + 10.5 * (i % 3), 38 + 10.5 * (i // 3), 8.5, 8.5, 2.6, c)
    return (
        rect(16, 30, 94, 70, 13, 'cream-dark')
        + rect(16, 26, 94, 70, 13, 'cream')
        + rect(22, 32, 74, 58, 8, 'charcoal')
        + rect(24.5, 34.5, 69, 53, 6, 'aqua')
        # weather card
        + rect(30, 38, 26, 30, 5, 'white')
        + circle(47, 47, 5, 'yellow')
        + path('M30 60Q38 52 46 58Q51 61 56 57V63Q56 68 51 68H35Q30 68 30 63Z', 'olive')
        + tiles
        # dock
        + rect(40, 74, 38, 9, 4.5, 'white', opacity='.85')
        + circle(49, 78.5, 2.4, 'orange') + circle(59, 78.5, 2.4, 'olive') + circle(69, 78.5, 2.4, 'yellow')
        # home button and camera
        + circle(103, 61, 4.2, 'cream-dark')
        + circle(103, 40, 1.8, 'olive')
    )


# --------------------------------------------------------------------------
def scanner():
    """Flatbed scanner, lid open, light bar sweeping under the glass."""
    return (
        # open lid: olive shell, pale pressure pad
        path('M27 16H99Q106 16 106.5 23L110 66H16L19.5 23Q20 16 27 16Z', 'olive-dark')
        + path('M29 20H97Q102 20 102.5 25L105.5 62H20.5L23.5 25Q24 20 29 20Z', 'olive')
        + path('M33 26H93Q96 26 96.3 29L98.5 58H27.5L29.7 29Q30 26 33 26Z', 'cream')
        # bed, seen from slightly above
        + path('M21 60H105L110 86H16Z', 'paper')
        + path('M28 65H98L101.5 81H24.5Z', 'aqua')
        + path('M52 65H68L69 81H51Z', 'yellow', opacity='.45')
        + line('M60 66.5V79.5', WHITE, 4.5)
        # front face
        + path('M16 87H110V97Q110 106 101 106H25Q16 106 16 97Z', 'cream-dark')
        + path('M16 84H110V93Q110 102 101 102H25Q16 102 16 93Z', 'cream')
        + rect(24, 89, 24, 8, 4, 'olive')
        + circle(85, 93, 3, 'yellow')
        + circle(97, 93, 4.2, 'orange')
    )


# --------------------------------------------------------------------------
def webcam():
    """Round webcam head on a little olive stand."""
    return (
        rect(36, 97, 54, 9, 4.5, 'olive-dark')
        + rect(36, 93, 54, 9, 4.5, 'olive')
        + rect(56, 78, 14, 18, 4, 'olive-dark')
        + circle(63, 53.5, 35, 'cream-dark')
        + circle(63, 51, 35, 'cream')
        + circle(63, 51, 24.5, 'charcoal')
        + circle(63, 51, 18, 'aqua')
        + circle(63, 51, 10, 'lens')
        + circle(58.5, 46.5, 3.4, 'white', opacity='.9')
        # indicator light and microphones
        + circle(63, 21.5, 2.8, 'orange')
        + circle(36, 64, 2.2, 'cream-dark') + circle(90, 64, 2.2, 'cream-dark')
    )


# --------------------------------------------------------------------------
def television():
    """Retro television: orange cabinet, rabbit-ear antenna, two knobs."""
    return (
        line('M56 36L39 20', OLIVE_DARK, 4.6) + line('M70 36L88 20', OLIVE_DARK, 4.6)
        + circle(38, 20, 4, 'yellow') + circle(89, 20, 4, 'yellow')
        + path('M49 39Q63 25 77 39Z', 'olive')
        + rect(28, 97, 14, 9, 3.5, 'olive-dark') + rect(84, 97, 14, 9, 3.5, 'olive-dark')
        + rect(16, 41, 94, 61, 13, 'orange-dark')
        + rect(16, 37, 94, 61, 13, 'orange')
        # picture tube
        + rect(22, 43, 62, 49, 11, 'cream')
        + rect(26, 47, 54, 41, 9, 'charcoal')
        + rect(28.5, 49.5, 49, 36, 7, 'aqua')
        + circle(64, 60, 5.5, 'yellow')
        + path('M28.5 76Q39 64 50 72Q58 78 66 73Q72 69 77.5 73V78.5Q77.5 85.5 70.5 85.5H35.5Q28.5 85.5 28.5 78.5Z', 'olive')
        # control panel
        + circle(97, 52, 6.5, 'cream') + circle(97, 52, 2.4, 'orange-dark')
        + circle(97, 68, 6.5, 'cream') + circle(97, 68, 2.4, 'olive')
        + line('M92 80H102M92 87H102', ORANGE_DARK, 3.4)
    )


# --------------------------------------------------------------------------
def media_player():
    """Pocket music player with a click wheel, plug and one earbud."""
    bars = ''
    for i, (h, c) in enumerate(((9, 'yellow'), (15, 'orange'), (11, 'yellow'), (18, 'cream'), (8, 'orange'), (13, 'yellow'))):
        bars += rect(30.5 + 7.3 * i, 51 - h, 4.6, h, 2, c)
    return (
        # plug, cord and earbud
        rect(58, 17, 22, 9, 4, 'orange')
        + line('M78 21.5H92Q101 21.5 101 31V54', ORANGE, 4.6)
        + rect(96.5, 52, 9, 14, 4, 'cream-dark')
        + circle(101, 70, 9, 'cream') + circle(101, 70, 3.6, 'olive')
        # body
        + rect(20, 28, 64, 78, 13, 'aqua-dark')
        + rect(20, 24, 64, 78, 13, 'aqua')
        + rect(26, 30, 52, 26, 6, 'charcoal')
        + bars
        # click wheel
        + circle(52, 80, 18.5, 'cream-dark')
        + circle(52, 78.5, 18.5, 'cream')
        + circle(52, 78.5, 7, 'orange')
        + circle(52, 65.5, 1.9, 'olive') + circle(52, 91.5, 1.9, 'olive')
        + circle(39, 78.5, 1.9, 'olive') + circle(65, 78.5, 1.9, 'olive')
    )


# --------------------------------------------------------------------------
def router():
    """Wireless router: two antennas, signal arcs and a row of status lights."""
    left, right = Tilt(-9, 30, 66), Tilt(9, 98, 66)
    return (
        left.rr(25.5, 17, 9, 52, 4.5, 'olive') + right.rr(93.5, 17, 9, 52, 4.5, 'olive')
        + rect(23, 58, 15, 10, 3, 'olive-dark') + rect(90, 58, 15, 10, 3, 'olive-dark')
        # signal
        + arc(64, 58, 25, -42, 42, AQUA_DARK, 5)
        + arc(64, 58, 14, -42, 42, AQUA_DARK, 5)
        + circle(64, 55, 4, 'orange')
        # feet and body
        + rect(27, 98, 14, 8, 3.5, 'olive-dark') + rect(87, 98, 14, 8, 3.5, 'olive-dark')
        + rect(16, 67, 94, 35, 11, 'cream-dark')
        + rect(16, 63, 94, 35, 11, 'cream')
        + rect(23, 73, 80, 14, 7, 'charcoal')
        + circle(33, 80, 3, 'yellow') + circle(44, 80, 3, 'mint') + circle(55, 80, 3, 'orange')
        + rect(66, 77.5, 29, 5, 2.5, 'aqua')
    )


# --------------------------------------------------------------------------
def chip():
    """Processor: dark package, gold pins on four sides, cream lid with a core."""
    pins = ''
    for i in range(5):
        o = 40.2 + 11.6 * i - 2.8
        pins += rect(o, 16, 5.6, 16, 2.4, 'yellow') + rect(o, 90, 5.6, 16, 2.4, 'yellow')
        pins += rect(19, o - 3, 16, 5.6, 2.4, 'yellow') + rect(93, o - 3, 16, 5.6, 2.4, 'yellow')
    return (
        pins
        + rect(30, 30, 68, 68, 10, 'lens')
        + rect(30, 27, 68, 68, 10, 'charcoal')
        + rect(40, 37, 48, 48, 7, 'cream-dark')
        + rect(40, 35, 48, 48, 7, 'cream')
        + rect(52, 47, 24, 24, 5, 'orange')
        + rect(58.5, 53.5, 11, 11, 3, 'yellow')
        + circle(36.5, 33.5, 2.4, 'yellow')
    )


# --------------------------------------------------------------------------
def memory():
    """RAM module: green board, memory chips, label and gold edge contacts."""
    t = Tilt(-17, 64, 62)
    contacts = ''
    for i in range(11):
        if i != 6:
            contacts += t.rr(26 + 7.1 * i, 73, 4.6, 9, 1.4, 'yellow')
    return (
        t.rr(22, 41, 84, 42, 4, 'olive-dark', transform='translate(1 4)')
        + t.rr(22, 41, 84, 42, 4, 'olive')
        + t.rr(22, 71.5, 84, 11.5, 2, 'olive-dark')
        + contacts
        + ''.join(t.rr(x, 46.5, 14, 19, 2.6, 'charcoal') for x in (27, 45, 63))
        + ''.join(t.circ(x + 7, 51.5, 1.8, 'stone') for x in (27, 45, 63))
        + t.rr(82, 46, 19, 20, 3, 'cream')
        + t.rr(82, 46, 19, 7, 3, 'orange')
        + t.ln([(86.5, 59.5), (96.5, 59.5)], OLIVE, 3.2)
    )


# --------------------------------------------------------------------------
def sdcard():
    """Memory card: clipped corner, gold contacts, label and lock switch."""
    body = 'M40 16H82L98 32V92Q98 102 88 102H40Q30 102 30 92V26Q30 16 40 16Z'
    contacts = ''.join(rect(37 + 8.6 * i, 22, 5.4, 16, 2, 'yellow') for i in range(5))
    return (
        rect(24.5, 50, 9, 15, 3.5, 'yellow')
        + path(body, 'orange-dark', transform='translate(0 4)')
        + path(body, 'orange')
        + contacts
        + path('M80 29L80 38H85.4V34.4Z', 'yellow')
        + rect(37, 48, 54, 46, 7, 'cream')
        + rect(43, 54, 28, 8, 4, 'aqua')
        + circle(81, 58, 4, 'olive')
        + line('M45 72H83M45 82H70', CREAM_DARK, 4.2)
    )


# --------------------------------------------------------------------------
def floppy():
    """3.5 inch floppy disk: metal shutter, clipped corner, paper label."""
    body = 'M28 17H92L107 32V91Q107 101 97 101H28Q19 101 19 92V26Q19 17 28 17Z'
    return (
        path(body, 'aqua-dark', transform='translate(0 4.5)')
        + path(body, 'aqua')
        # shutter
        + rect(37, 17, 46, 30, 3.5, 'stone', transform='translate(0 1.6)')
        + rect(37, 17, 46, 29, 3.5, 'metal')
        + rect(65, 22, 11, 19, 2.5, 'charcoal')
        # label
        + path('M34 56H92Q96 56 96 60V101H30V60Q30 56 34 56Z', 'cream')
        + rect(30, 56, 66, 9, 3.5, 'orange')
        + line('M38 75H88M38 84H88M38 93H72', CREAM_DARK, 3.6)
        # write-protect tab
        + rect(22, 87, 5.5, 8, 1.6, 'charcoal')
    )


# --------------------------------------------------------------------------
def camcorder():
    """Hand-held video camera: lens hood, carry handle, flip-out screen."""
    return (
        # carry handle and microphone
        line('M56 42V33Q56 27 62 27H84Q90 27 90 33V42', OLIVE, 6.5)
        + rect(40, 30, 14, 10, 4.5, 'yellow')
        # viewfinder
        + rect(98, 45, 12, 18, 4.5, 'charcoal')
        # lens barrel and hood
        + rect(28, 51, 20, 30, 4, 'olive')
        + rect(16, 44, 17, 44, 7, 'charcoal')
        + ellipse(23.5, 66, 4.6, 15, 'aqua')
        # body
        + rect(42, 44, 62, 50, 12, 'cream-dark')
        + rect(42, 40, 62, 50, 12, 'cream')
        # flip screen
        + rect(50, 46, 38, 27, 6, 'charcoal')
        + rect(53, 49, 32, 21, 3.5, 'aqua')
        + path('M53 66Q61 57 69 63Q76 68 85 60V66.5Q85 70 81.5 70H56.5Q53 70 53 66.5Z', 'olive')
        + circle(59, 54.5, 2.6, 'orange')
        # controls and strap
        + circle(95.5, 51, 3.6, 'orange')
        + rect(50, 78, 30, 7, 3.5, 'olive')
        + circle(90, 81.5, 3, 'yellow')
    )


# --------------------------------------------------------------------------
def speaker():
    """Loudspeaker cabinet with tweeter and woofer."""
    return (
        rect(26, 20, 74, 86, 12, 'olive-dark')
        + rect(26, 16, 74, 86, 12, 'olive')
        + rect(32, 22, 62, 74, 8, 'cream')
        # tweeter
        + circle(63, 38, 11.5, 'charcoal')
        + circle(63, 38, 7, 'lens')
        + circle(63, 38, 3.4, 'yellow')
        # woofer
        + circle(63, 71, 21.5, 'charcoal')
        + circle(63, 71, 16.5, 'lens')
        + circle(63, 71, 11, 'none', stroke=CHARCOAL, stroke_width=3)
        + circle(63, 71, 6.5, 'orange')
        # screws
        + circle(38, 28, 2, 'cream-dark') + circle(88, 28, 2, 'cream-dark')
        + circle(38, 90, 2, 'cream-dark') + circle(88, 90, 2, 'cream-dark')
    )


# --------------------------------------------------------------------------
def ups():
    """Battery backup tower with charge gauge, bolt badge and mains plug."""
    return (
        # cord and plug
        line('M82 92H93Q102 92 102 83V60', OLIVE_DARK, 5)
        + rect(96.3, 29, 4, 13, 1.6, 'metal') + rect(103.7, 29, 4, 13, 1.6, 'metal')
        + rect(94, 38, 16, 24, 5.5, 'orange')
        # tower
        + rect(19, 21, 68, 85, 11, 'cream-dark')
        + rect(19, 17, 68, 85, 11, 'cream')
        # charge gauge
        + rect(26, 24, 54, 21, 6, 'charcoal')
        + rect(31, 29, 7.5, 11, 2, 'yellow') + rect(41, 29, 7.5, 11, 2, 'yellow')
        + rect(51, 29, 7.5, 11, 2, 'yellow') + rect(61, 29, 7.5, 11, 2, 'lens')
        + rect(70.5, 32, 4, 5, 1.5, 'cream-dark')
        # bolt badge
        + circle(53, 66, 15.5, 'olive')
        + path('M57 53.5L45 68H52L49 78.5L61.5 63.5H54.5Z', 'yellow')
        # vents and power light
        + line('M30 91H62', CREAM_DARK, 3.6)
        + circle(73, 91, 3.2, 'orange')
    )


# --------------------------------------------------------------------------
def joystick():
    """Arcade joystick: orange ball, rubber boot, base with two buttons."""
    return (
        rect(17, 81, 92, 25, 11, 'cream-dark')
        + rect(17, 76, 92, 25, 11, 'cream')
        + circle(33, 88.5, 6.5, 'yellow-dark') + circle(33, 87, 6.5, 'yellow')
        + circle(93, 88.5, 6.5, 'aqua-dark') + circle(93, 87, 6.5, 'aqua')
        # boot and shaft
        + line('M63 68L69 42', METAL, 9)
        + path('M43 81Q43 62 63 62Q83 62 83 81Q63 87 43 81Z', 'olive-dark')
        + path('M45 78Q45 62 63 62Q81 62 81 78Q63 83 45 78Z', 'olive')
        + ellipse(63, 65, 9, 3.6, 'olive-dark')
        # ball
        + circle(71, 35.5, 18, 'orange-dark')
        + circle(70, 34, 18, 'orange')
        + circle(63.5, 27, 4.2, 'peach', opacity='.8')
    )


# --------------------------------------------------------------------------
def projector():
    """Video projector throwing a beam of light."""
    return (
        # beam
        path('M40 59L16 34V98L40 73Z', 'yellow', opacity='.42')
        + path('M40 62L16 48V84L40 70Z', 'yellow', opacity='.75')
        # feet
        + rect(56, 92, 11, 8, 3.5, 'olive-dark') + rect(93, 92, 11, 8, 3.5, 'olive-dark')
        # focus ring on top
        + rect(60, 30, 22, 10, 4.5, 'olive')
        # lens barrel
        + rect(36, 49, 20, 34, 6.5, 'charcoal')
        + ellipse(40.5, 66, 4, 12.5, 'aqua')
        # body
        + rect(49, 40, 61, 55, 11, 'cream-dark')
        + rect(49, 36, 61, 55, 11, 'cream')
        + rect(49, 36, 61, 11, 5.5, 'olive')
        + line('M84 56H101M84 64H101M84 72H101', CREAM_DARK, 3.8)
        + circle(66, 62, 8.5, 'orange-dark') + circle(66, 61, 8.5, 'orange')
        + circle(66, 61, 3.4, 'yellow')
        + circle(60, 81, 2.8, 'yellow') + circle(69, 81, 2.8, 'olive')
    )


# --------------------------------------------------------------------------
def smartwatch():
    """Smart watch: orange strap, cream case, activity rings, golden crown."""
    return (
        path('M48 16H80Q83 16 83.3 19L86 46H42L44.7 19Q45 16 48 16Z', 'orange')
        + path('M42 78H86L83.3 103Q83 106 80 106H48Q45 106 44.7 103Z', 'orange')
        + circle(64, 99, 2.4, 'orange-dark')
        + rect(54, 20, 20, 5, 2.5, 'orange-dark')
        # crown and button
        + rect(94, 48, 10, 15, 4, 'yellow')
        + rect(94, 68, 7.5, 9, 3, 'cream-dark')
        # case
        + rect(29, 33, 68, 62, 18, 'cream-dark')
        + rect(29, 29.5, 68, 62, 18, 'cream')
        + rect(35, 35.5, 56, 50, 13, 'charcoal')
        # activity rings
        + arc(63, 60.5, 17.5, 0, 265, ORANGE, 5)
        + arc(63, 60.5, 10.8, 0, 200, YELLOW, 5)
        + circle(63, 60.5, 3.6, 'aqua')
    )


# --------------------------------------------------------------------------
def drawing_tablet():
    """Graphics tablet with express keys, a drawn stroke and a stylus."""
    pen = Tilt(35, 64, 58, 1, 30, -18)
    return (
        rect(16, 44, 94, 62, 11, 'olive-dark')
        + rect(16, 40, 94, 62, 11, 'olive')
        + rect(22, 48, 10, 10, 3.2, 'cream') + rect(22, 62, 10, 10, 3.2, 'cream')
        + rect(22, 76, 10, 10, 3.2, 'yellow')
        + rect(38, 47, 66, 48, 7, 'cream')
        + line('M46 84C50 62 58 88 64 72C67 64 73 70 77 65', AQUA_DARK, 4.6)
        # stylus
        + pen.rr(59.5, 36, 9, 40, 3, 'orange-dark', transform='translate(1.5 2.5)')
        + pen.poly([(59.5, 74), (68.5, 74), (65.2, 85), (62.8, 85)], 'charcoal')
        + pen.rr(59.5, 36, 9, 40, 3, 'orange')
        + pen.rr(59.5, 36, 9, 8, 3, 'cream')
        + pen.rr(59.5, 62, 9, 6, 1.5, 'yellow')
    )


# --------------------------------------------------------------------------
def network_card():
    """Expansion network card: metal bracket, socket, controller, gold fingers."""
    fingers = ''.join(rect(x, 84, 4.6, 13, 1.6, 'yellow') for x in (48, 55.2, 62.4, 75, 82.2, 89.4, 96.6))
    return (
        # bracket
        rect(18, 18, 20, 9, 3.5, 'stone')
        + rect(16, 16, 11.5, 90, 4, 'stone', transform='translate(1.6 0)')
        + rect(16, 16, 11.5, 90, 4, 'metal')
        + circle(21.7, 23, 2.2, 'stone') + circle(21.7, 99, 2.2, 'stone')
        # edge connector
        + rect(44, 82, 28, 17, 2.5, 'olive-dark') + rect(72.5, 82, 31, 17, 2.5, 'olive-dark')
        + fingers
        # board
        + path('M27 33H104Q110 33 110 39V87H27Z', 'aqua-dark')
        + path('M27 30H104Q110 30 110 36V84H27Z', 'aqua')
        # socket
        + rect(25, 38, 27, 27, 4.5, 'cream-dark', transform='translate(0 2.5)')
        + rect(25, 38, 27, 27, 4.5, 'cream')
        + rect(31, 46, 15, 13, 2.5, 'charcoal')
        + circle(32.5, 41.8, 1.9, 'yellow') + circle(44.5, 41.8, 1.9, 'olive')
        # controller chip, capacitors, trace
        + line('M52 72H66L74 64', WHITE, 3.4, opacity='.8')
        + rect(64, 40, 25, 25, 4, 'charcoal')
        + rect(71, 47, 11, 11, 2.5, 'orange')
        + circle(100, 43, 4.4, 'yellow') + circle(100, 56, 4.4, 'orange')
        + rect(92, 68, 12, 7, 2.5, 'cream')
    )


ART = {
    'tablet': tablet,
    'scanner': scanner,
    'webcam': webcam,
    'television': television,
    'media-player': media_player,
    'router': router,
    'chip': chip,
    'memory': memory,
    'sdcard': sdcard,
    'floppy': floppy,
    'camcorder': camcorder,
    'speaker': speaker,
    'ups': ups,
    'joystick': joystick,
    'projector': projector,
    'smartwatch': smartwatch,
    'drawing-tablet': drawing_tablet,
    'network-card': network_card,
}
