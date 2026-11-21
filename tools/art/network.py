"""Eduka-Icons 1.0 clay artwork: network and people group.

wifi, bluetooth, network, globe, cloud, phone, message, person, users, smile.
Every function returns an SVG fragment on the 128 x 128 grid; tools/clay.py
sculpts each shape element separately. GPL-3.0.
"""
import math
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_D = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_D, YELLOW, YELLOW_D = '#e0703a', '#b9552a', '#eec14f', '#cf9f33'
OLIVE, OLIVE_D = '#7d8c55', '#5f6c40'
AQUA, AQUA_D, CHARCOAL = '#8fc0c4', '#6a9ea3', '#3f3c37'
AQUA_DD = '#4f8287'          # shadow tone under cream strokes on aqua
SKIN, SKIN_D = '#d99261', '#b87548'


def ellipse(cx, cy, rx, ry, c, **kw):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    fill = c if c == 'none' or c.startswith('#') else f'url(#{c})'
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" {extra}/>'


def arc(cx, cy, r, a0, a1, colour, width, **kw):
    """Round-capped circular arc from angle a0 to a1 (degrees, clockwise, 0 = east)."""
    p = lambda a: f'{cx + r * math.cos(math.radians(a)):.2f} {cy + r * math.sin(math.radians(a)):.2f}'
    large = 1 if abs(a1 - a0) > 180 else 0
    return line(f'M{p(a0)}A{r} {r} 0 {large} 1 {p(a1)}', colour, width, **kw)


# --------------------------------------------------------------------------
def wifi():
    """Little router with two antennas, an orange beacon and three clay waves."""
    cx, cy = 63, 76
    s = ''
    for r in (52, 36, 20):
        s += arc(cx, cy + 3.2, r, -137, -43, AQUA_D, 9)
        s += arc(cx, cy, r, -137, -43, AQUA, 9)
    # antennas with soft tips
    for x in (25, 94):
        s += rect(x, 64, 7, 24, 3.5, 'olive') + circle(x + 3.5, 63.5, 4.6, 'yellow')
    # router body
    s += rect(20, 86, 86, 20, 9, 'cream-dark')
    s += rect(20, 82, 86, 20, 9, 'cream')
    s += circle(33, 92, 3.1, 'olive') + circle(43.5, 92, 3.1, 'yellow')
    s += rect(72, 89.2, 24, 5.6, 2.8, 'cream-dark')
    # beacon
    s += circle(cx, cy + 1.5, 7.5, 'orange-dark')
    s += circle(cx, cy, 7.5, 'orange')
    return s


# --------------------------------------------------------------------------
def bluetooth():
    """Thick aqua pill with an embossed cream rune and two pairing waves."""
    rune = 'M49 46L77 72L63 85V33L77 46L49 72'
    s = line('M26 47Q19 59 26 71', ORANGE, 5.5) + line('M100 47Q107 59 100 71', ORANGE, 5.5)
    s += rect(34, 21, 58, 85, 29, AQUA_DD)
    s += rect(34, 16, 58, 85, 29, 'aqua-dark')
    s += rect(39.5, 21.5, 47, 74, 23.5, 'none', stroke=AQUA, stroke_width=3.4, opacity='.75')
    s += line(rune, '#44747a', 8, transform='translate(1.2 2.6)')
    s += line(rune, WHITE, 8)
    return s


# --------------------------------------------------------------------------
def network():
    """Three small computers wired through an olive switch with orange cable."""
    cable = 'M63 50V64M32 78V72Q32 66 38 66H88Q94 66 94 72V78'
    def pc(x, y, w, h, screen):
        return (rect(x, y + 4, w, h, 6, 'cream-dark') + rect(x, y, w, h, 6, 'cream')
                + rect(x + 4, y + 4, w - 8, h - 9, 3.5, 'aqua') + screen)
    s = line(cable, ORANGE_D, 6, transform='translate(0 2.5)') + line(cable, ORANGE, 6)
    # top computer
    s += pc(39, 16, 48, 34,
            line('M49 27H62M49 34H57', WHITE, 3.4) + circle(74, 30, 4.5, 'yellow'))
    # switch
    s += rect(50, 61.5, 26, 13, 5, 'olive-dark') + rect(50, 58.5, 26, 13, 5, 'olive')
    s += circle(57, 65, 2.4, 'yellow') + circle(63, 65, 2.4, 'cream') + circle(69, 65, 2.4, 'yellow')
    # two clients
    s += pc(16, 76, 34, 25, rect(23, 83, 9, 9, 2.5, 'orange') + line('M37 85H42M37 90H40', WHITE, 3.2))
    s += pc(76, 76, 34, 25, circle(87, 87, 4, 'yellow') + line('M95 85H102M95 90H100', WHITE, 3.2))
    return s


# --------------------------------------------------------------------------
def globe():
    """Desk globe on a tilted brass meridian, clamped in an olive foot."""
    cx, cy, R = 57, 53, 33
    s = rect(30, 97, 54, 9, 4.5, 'olive-dark') + rect(30, 93.5, 54, 9, 4.5, 'olive')
    s += arc(cx + 1, cy + 2.5, 38.5, -62, 118, YELLOW_D, 5.5)
    s += arc(cx, cy, 38.5, -62, 118, YELLOW, 5.5)
    s += circle(cx + 1.2, cy + 2.6, R, 'aqua-dark')
    s += circle(cx, cy, R, 'aqua')
    # drawn for a 35-unit sphere centred on 57 55, then fitted
    grid = 'M40 26.7Q60.3 48.8 90 53.3M27.9 39.5Q51.4 65.6 86.1 70.5M24 56.7Q44.3 78.8 74 83.3'
    land = line(grid, AQUA_D, 3.6, opacity='.55')
    # continents: one wraps round the right edge
    land += path('M79.5 28.2A35 35 0 0 1 91.9 58Q86 66 80 60Q76 54 70 56Q62 58 62 50Q62 44 68 42Q72 38 70 32Q72 26 79.5 28.2Z', 'olive')
    land += path('M36 40Q44 34 50 40Q54 46 48 52Q44 56 46 62Q50 70 44 76Q38 80 36 72Q36 64 32 58Q28 48 36 40Z', 'olive')
    land += circle(70, 77, 4.8, 'olive')
    s += f'<g transform="translate({cx} {cy}) scale({R / 35:.4f}) translate(-57 -55)">{land}</g>'
    # neck that grips the ring, axis pins
    s += path('M47 96.5Q47 84.5 57 84.5Q67 84.5 67 96.5Z', 'olive')
    s += circle(75.1, 19, 3.8, 'orange') + circle(38.9, 87, 3.8, 'orange')
    return s


# --------------------------------------------------------------------------
def cloud():
    """Puffy aqua cloud in front of a cream one, with up/down sync arrows."""
    big = 'M38 96C13 96 12 64 37 62C38 34 76 30 85 54C110 52 116 96 90 96Z'
    back = 'M66 56C54 56 54 40 66 39C68 24 90 22 95 36C108 35 111 56 97 56Z'
    s = path(back, 'cream-dark', transform='translate(1 3)') + path(back, 'cream')
    s += path(big, 'aqua-dark', transform='translate(0 4.5)')
    s += path(big, 'aqua')
    s += line('M31 74Q33 66 41 65', WHITE, 4, opacity='.6')
    up = 'M54 67L65 79H58.5V90H49.5V79H43Z'
    down = 'M77 90L66 78H72.5V67H81.5V78H88Z'
    s += path(up, AQUA_DD, transform='translate(1 2.6)') + path(up, 'cream')
    s += path(down, AQUA_DD, transform='translate(4 2.6)') + path(down, 'orange', transform='translate(3 0)')
    return s


# --------------------------------------------------------------------------
def phone():
    """Olive call button with a cream handset and two ringing waves."""
    handset = ('M31 26Q25 26 23 34Q20 59 44 83Q66 105 89 102Q95 101 99 94L102 84Q103 80 98 77'
               'L83 69Q78 67 75 72L69 80Q54 77 46 64Q40 56 40 51L48 46Q52 43 49 38L41 27Q38 24 31 26Z')
    place = 'translate(14.6 10.4) scale(.79)'
    s = circle(63, 65, 41, 'olive-dark') + circle(63, 60.5, 41, 'olive')
    s += circle(63, 60.5, 34.5, 'none', stroke='#93a26b', stroke_width=3.4, opacity='.8')
    s += f'<g transform="translate(1.2 3)"><g transform="{place}">' + path(handset, 'olive-dark') + '</g></g>'
    s += f'<g transform="{place}">' + path(handset, 'cream') + '</g>'
    s += arc(59, 64, 14, -76, -14, YELLOW, 5)
    s += arc(59, 64, 24.5, -72, -18, YELLOW, 5)
    return s


# --------------------------------------------------------------------------
def message():
    """Aqua speech bubble with three written lines and an orange unread dot."""
    bubble = 'M31 23H93Q107 23 107 37V70Q107 84 93 84H60L37 101Q33 103 34 98L37 84H31Q17 84 17 70V37Q17 23 31 23Z'
    s = path(bubble, 'aqua-dark', transform='translate(0 4.5)')
    s += path(bubble, 'aqua')
    s += line('M32 41H76M32 54H92M32 67H68', AQUA_DD, 6.5, transform='translate(0 2)')
    s += line('M32 41H76M32 54H92M32 67H68', WHITE, 6.5)
    s += circle(97, 30, 12, 'orange-dark') + circle(96, 27.5, 12, 'orange')
    s += circle(96, 27.5, 4.2, 'white')
    return s


# --------------------------------------------------------------------------
def _bust(x, head_y, r, shirt, shirt_dark, top, bottom, half, hair, detail=''):
    """Head-and-shoulders figure centred on x."""
    body = (f'M{x - half} {bottom - 6}V{top + 26}Q{x - half} {top} {x} {top}Q{x + half} {top} {x + half} {top + 26}'
            f'V{bottom - 6}Q{x + half} {bottom} {x + half - 6} {bottom}H{x - half + 6}Q{x - half} {bottom} {x - half} {bottom - 6}Z')
    s = path(body, shirt_dark, transform='translate(0 3.5)') + path(body, shirt)
    s += rect(x - r * .42, head_y + r * .55, r * .84, r * .9, r * .3, SKIN_D)        # neck
    s += detail
    s += circle(x - r + 1.5, head_y + 2, r * .21, SKIN_D) + circle(x + r - 1.5, head_y + 2, r * .21, SKIN_D)   # ears
    s += circle(x, head_y, r, SKIN)
    s += hair
    return s


def _face(x, y, k=1):
    return (circle(x - 7 * k, y, 2.6 * k, 'charcoal') + circle(x + 7 * k, y, 2.6 * k, 'charcoal')
            + line(f'M{x - 6 * k} {y + 7.5 * k}Q{x} {y + 12.5 * k} {x + 6 * k} {y + 7.5 * k}', '#8c4a2c', max(3, 3.2 * k)))


def person():
    """Friendly bust: aqua shirt, cream collar, orange tie, dark hair."""
    x = 63
    collar = (path(f'M{x - 13} 61L{x} 76L{x - 10} 87Q{x - 19} 76 {x - 13} 61Z', 'cream')
              + path(f'M{x + 13} 61L{x} 76L{x + 10} 87Q{x + 19} 76 {x + 13} 61Z', 'cream'))
    tie = path(f'M{x} 74L{x + 5.5} 80L{x + 4} 100Q{x} 104 {x - 4} 100L{x - 5.5} 80Z', 'orange')
    hair = path('M43.5 40Q41 17 63 17Q85 17 82.5 40Q78 29 67 29Q54 31 43.5 40Z', 'charcoal')
    s = _bust(x, 40, 20, 'aqua', 'aqua-dark', 63, 103, 40, hair, collar + tie)
    s += _face(x, 44)
    return s


def users():
    """Two friends: orange shirt behind, aqua shirt in front."""
    hair_b = (circle(84, 36, 17, 'charcoal'))
    fringe_b = path('M70.5 34Q70 20 84 20Q98 20 97.5 34Q90 27 84 28Q76 28 70.5 34Z', 'charcoal')
    necklace = line('M76.5 57.5Q84 65 91.5 57.5', YELLOW, 4)
    back = (hair_b + _bust(84, 37, 14, 'orange', 'orange-dark', 55, 96, 26, fringe_b, necklace)
            + _face(84, 40, .72))
    collar = path('M35 71L47 85L59 71L53 67H41Z', 'cream')
    hair_f = path('M30.5 46Q28 27 47 27Q66 27 63.5 46Q60 37 50 37Q39 39 30.5 46Z', 'charcoal')
    front = _bust(47, 46, 17, 'aqua', 'aqua-dark', 68, 103, 31, hair_f, collar) + _face(47, 49.5, .86)
    return back + front


# --------------------------------------------------------------------------
def smile():
    """Sunny round face with a big open smile."""
    s = circle(63, 65, 41, 'yellow-dark') + circle(63, 60.5, 41, 'yellow')
    s += circle(35, 67, 6.5, 'orange', opacity='.6') + circle(91, 67, 6.5, 'orange', opacity='.6')
    s += ellipse(49, 50, 5.2, 7.2, 'charcoal') + ellipse(77, 50, 5.2, 7.2, 'charcoal')
    s += circle(51, 47, 2.1, 'white') + circle(79, 47, 2.1, 'white')
    s += path('M41 65Q63 70 85 65Q86 91 63 91Q40 91 41 65Z', 'charcoal')
    s += path('M45 67.6Q63 71.5 81 67.6Q81.5 73 79 74Q63 77.5 47 74Q44.5 73 45 67.6Z', 'white')
    s += path('M52 86.5Q52 79 63 79Q74 79 74 86.5Q70 89.8 63 89.8Q56 89.8 52 86.5Z', 'orange')
    return s


ART = {
    'wifi': wifi,
    'bluetooth': bluetooth,
    'network': network,
    'globe': globe,
    'cloud': cloud,
    'phone': phone,
    'message': message,
    'person': person,
    'users': users,
    'smile': smile,
}
