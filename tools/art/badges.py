"""Eduka 1.0 clay artwork: folder emblem badges. GPL-3.0.

A badge is a small symbol drawn around (64, 82) within about +-15 units;
tools/clay.py folder_svg() scales it by 0.6 and sets it on the olive disc at
the lower right of the folder. Only light clay reads on olive, so every badge
is one bold cream/white silhouette with yellow parts and a small orange accent;
inner details are "cut" in olive-dark. Each shape carries its own clay filter
so the symbol is sculpted on the disc instead of printed on it.
"""
import math
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_DARK = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, YELLOW, OLIVE_DARK = '#e0703a', '#eec14f', '#5f6c40'
CUT = '#56623a'          # engraved detail inside a light shape
CLAY, CLAY_STROKE = 'url(#clay)', 'url(#clay-stroke)'


def P(d, c, **kw):
    return path(d, c, filter=CLAY, **kw)


def R(x, y, w, h, r, c, **kw):
    return rect(x, y, w, h, r, c, filter=CLAY, **kw)


def C(x, y, r, c, **kw):
    return circle(x, y, r, c, filter=CLAY, **kw)


def L(d, colour, width, **kw):
    """Raised round clay cord."""
    return line(d, colour, width, filter=CLAY_STROKE, **kw)


def cut(d, width=3.4, colour=CUT, **kw):
    """Flat engraved line (no bevel: it is a groove, not a part)."""
    return line(d, colour, width, **kw)


def hole(x, y, r, colour=CUT):
    return circle(x, y, r, colour)


def polar(cx, cy, r, degrees):
    a = math.radians(degrees)
    return f'{cx + r * math.sin(a):.2f} {cy - r * math.cos(a):.2f}'


def home():
    return (
        R(69, 67, 6, 10, 2, 'orange')                                              # chimney
        + P('M53 82L64 72L75 82V94Q75 97 72 97H56Q53 97 53 94Z', 'white')           # walls
        + R(60, 86, 8, 11, 2.5, 'orange')                                          # door
        + P('M46.5 81L62 67.2Q64 65.6 66 67.2L81.5 81Q83 82.6 81.4 84.2L79.8 85.8'
            'Q78.4 87 76.9 85.7L64 74.4L51.1 85.7Q49.6 87 48.2 85.8L46.6 84.2Q45 82.6 46.5 81Z', 'yellow')
    )


def download():
    return (
        P('M50 87Q50 85.5 51.5 85.5H54.5Q56 85.5 56 87V91.5H72V87Q72 85.5 73.5 85.5H76.5'
          'Q78 85.5 78 87V95Q78 97.5 75.5 97.5H52.5Q50 97.5 50 95Z', 'yellow')      # tray
        + P('M60.5 66H67.5Q69.5 66 69.5 68V76H74.5Q77.5 76 75.5 78.3L65.6 88.6Q64 90.2 62.4 88.6'
            'L52.5 78.3Q50.5 76 53.5 76H58.5V68Q58.5 66 60.5 66Z', 'white')       # arrow
    )


def music():
    return (
        '<ellipse cx="55.5" cy="91" rx="6.6" ry="5.4" fill="url(#white)" filter="url(#clay)" transform="rotate(-18 55.5 91)"/>'
        + '<ellipse cx="72.5" cy="87" rx="6.6" ry="5.4" fill="url(#white)" filter="url(#clay)" transform="rotate(-18 72.5 87)"/>'
        + R(57.2, 71, 4.8, 20, 2, 'white') + R(74.2, 67, 4.8, 20, 2, 'white')
        + P('M57.2 70.4Q57.2 68.8 58.8 68.4L77 64.2Q79 63.8 79 65.8V70.6Q79 72.2 77.4 72.6'
            'L59.2 76.8Q57.2 77.2 57.2 75.2Z', 'yellow')                          # beam
    )


def pictures():
    return ('<g transform="rotate(-7 64 82)">'
            + R(48, 69, 32, 26, 4.5, 'white')
            + R(51.5, 72.5, 25, 19, 2.5, 'aqua')
            + path('M51.5 89L58.6 80.2Q60.2 78.6 61.8 80.2L66.4 85L69.3 82.4Q70.8 81.2 72.2 82.6L76.5 87V89'
                   'Q76.5 91.5 74 91.5H54Q51.5 91.5 51.5 89Z', 'olive')
            + C(70.5, 77.4, 3.4, 'yellow')
            + '</g>')


def video():
    return (
        R(49, 77, 30, 20, 4, 'white')                                              # slate
        + P('M60 81.2Q60 79.4 61.7 80.3L71 85.6Q72.6 86.6 71 87.6L61.7 92.9Q60 93.8 60 92Z', 'orange')
        + P('M48.5 72.4Q48.1 70.7 49.8 70.3L75.5 64.5Q77.2 64.1 77.6 65.8L78.4 69.2'
            'Q78.8 70.9 77.1 71.3L51.4 77.1Q49.7 77.5 49.3 75.8Z', 'yellow')  # clapper arm
        + cut('M57.3 69.3L59.2 74.6M65.2 67.5L67.1 72.8M73 65.8L74.9 71.1', 3.3)
    )


def share():
    return (
        L('M54 82L73 71.5M54 82L73 92.5', WHITE, 4.8)
        + C(54, 82, 6.6, 'orange') + C(73.5, 71.5, 6, 'white') + C(73.5, 92.5, 6, 'white')
    )


def lock():
    return (
        L('M56.5 81V75.5Q56.5 68.5 64 68.5Q71.5 68.5 71.5 75.5V81', WHITE, 5)
        + R(50.5, 78.5, 27, 19, 5.5, 'yellow')
        + hole(64, 85.6, 3.4) + cut('M64 86V91.4', 3.4)
    )


def templates():
    return (
        R(56, 66, 23, 27, 4, 'yellow')                                             # sheet behind
        + R(49, 71, 24, 27, 4, 'white')
        + rect(53, 75, 16, 5.5, 2, CUT)                                            # layout blocks
        + rect(53, 83.5, 6.5, 10.5, 2, ORANGE) + rect(62.5, 83.5, 6.5, 10.5, 2, CUT)
    )


def git():
    return (
        P('M61.6 65.8Q64 63.4 66.4 65.8L80.2 79.6Q82.6 82 80.2 84.4L66.4 98.2Q64 100.6 61.6 98.2'
          'L47.8 84.4Q45.4 82 47.8 79.6Z', 'white')
        + cut('M61 74V90M61 79Q61 82 67 82H69', 3.6)
        + hole(61, 74.2, 3.3) + hole(61, 90, 3.3) + circle(69.5, 82, 3.5, ORANGE)
    )


def cloud():
    shape = ('M55 95Q47.5 95 47.5 88.2Q47.5 82.4 53.2 81.5Q53.4 73.5 60.5 71Q68 68.8 72.2 76'
             'Q80.5 75.4 80.5 85.5Q80.5 95 73 95Z')
    return P(shape, 'cream-dark', transform='translate(0 2.2)') + P(shape, 'white')


def text():
    return (
        P('M55 67H68.5L77 75.5V94Q77 97 74 97H55Q52 97 52 94V70Q52 67 55 67Z', 'white')
        + P('M68.5 67L77 75.5H71.5Q68.5 75.5 68.5 72.5Z', 'yellow')
        + cut('M57.2 80H71.8M57.2 86H71.8M57.2 92H66', 3.6)
    )


def desktop():
    return (
        R(60, 88, 8, 7, 1.5, 'cream-dark') + R(53, 92.6, 22, 5, 2.5, 'white')    # stand
        + R(48, 67.5, 32, 23, 4.5, 'white')
        + R(51.5, 71, 25, 16, 2.5, 'aqua')
        + circle(57, 76.5, 2.6, YELLOW)
    )


def favorites():
    def star(cx, cy, big, small):
        return 'M' + 'L'.join(polar(cx, cy, big if i % 2 == 0 else small, i * 36) for i in range(10)) + 'Z'
    return (path(star(64, 85, 17.5, 8.4), 'yellow-dark', stroke='#cf9f33', stroke_width=3, stroke_linejoin='round', filter=CLAY)
            + path(star(64, 82.8, 17.5, 8.4), 'yellow', stroke=YELLOW, stroke_width=3, stroke_linejoin='round', filter=CLAY))


def games():
    return (
        P('M53 72.5H75Q81 72.5 82.4 79L84 88.5Q84.9 95.5 79.8 95.5Q77 95.5 75.2 93.2L72 89.5H56'
          'L52.8 93.2Q51 95.5 48.2 95.5Q43.1 95.5 44 88.5L45.6 79Q47 72.5 53 72.5Z', 'white')
        + cut('M51.3 80.6H59.7M55.5 76.4V84.8', 3.6)
        + circle(70.2, 83, 2.9, YELLOW) + circle(75.8, 78.6, 2.9, ORANGE)
    )


def recent():
    return (
        C(64, 82, 16.5, 'yellow') + C(64, 82, 12.6, 'white')
        + cut('M64 74.6V82L69.4 85.6', 3.6)
        + circle(64, 82, 2.2, ORANGE)
    )


def backup():
    r = 12.5
    return (
        L(f'M{polar(64, 82, r, 82)}A{r} {r} 0 1 1 {polar(64, 82, r, -6)}', WHITE, 5.6)
        + P('M64.5 62.5L75.8 69.2Q77.6 70.3 75.8 71.4L64.5 77.5Q62.8 78.3 62.8 76.4V63.6Q62.8 61.7 64.5 62.5Z', 'yellow')
    )


def code():
    return (
        L('M56 72.5L47 82L56 91.5', WHITE, 5.8)
        + L('M72 72.5L81 82L72 91.5', WHITE, 5.8)
        + L('M66.8 71L61.2 93', YELLOW, 4.8)
    )


def books():
    return (
        R(48.5, 70, 9.5, 27, 2.2, 'white') + rect(48.5, 75, 9.5, 4, 0, ORANGE)
        + R(59, 67, 10, 30, 2.2, 'yellow') + rect(59, 87, 10, 4, 0, WHITE)
        + '<g transform="rotate(-14 75 84)">' + R(70.5, 70.5, 9, 27, 2.2, 'white') + rect(70.5, 75, 9, 4, 0, CUT) + '</g>'
    )


def camera():
    return (
        R(56, 68, 13, 8, 2.5, 'cream-dark')
        + R(47.5, 72.5, 33, 23, 5, 'white')
        + C(64, 84, 8.2, 'yellow') + hole(64, 84, 4.6)
        + circle(75, 77.2, 2.2, ORANGE)
    )


def mail():
    return (
        R(47.5, 70, 33, 24, 4.5, 'white')
        + cut('M51 74L64 84.5L77 74', 3.6)
        + C(64, 84.5, 3.8, 'orange')
    )


def print_():
    return (
        R(55, 66.5, 18, 12, 2.5, 'white')                                          # blank sheet in
        + R(47.5, 74.5, 33, 15.5, 4.5, 'yellow')
        + rect(52, 83.5, 24, 3.2, 1.6, CUT)                                        # slot
        + R(54, 85.5, 20, 12, 2.5, 'white')
        + cut('M58.4 91.6H69.6', 3.2)
        + circle(75.5, 79, 2, ORANGE)
    )


def important():
    return (
        P('M60 65H68Q71.2 65 71 68.2L69.6 83.4Q69.4 86 66.8 86H61.2Q58.6 86 58.4 83.4'
          'L57 68.2Q56.8 65 60 65Z', 'white')
        + C(64, 93.6, 5.4, 'orange')
    )


def network():
    return (
        L('M64 76V82M54.5 88V82H73.5V88', YELLOW, 3.8)
        + R(56.5, 66.5, 15, 11.5, 3, 'white')
        + R(47.5, 86, 14, 11, 3, 'white') + R(66.5, 86, 14, 11, 3, 'white')
    )


def root():
    points = []
    teeth, steps = 8, 6
    for i in range(teeth * steps):
        radius = 17 if i % steps in (0, 1, 2) else 12.6
        points.append(polar(64, 82, radius, (i - 1) * 360 / (teeth * steps)))
    return (
        path('M' + 'L'.join(points) + 'Z', 'white', stroke=WHITE, stroke_width=2, stroke_linejoin='round', filter=CLAY)
        + C(64, 82, 7, 'yellow') + circle(64, 82, 3, ORANGE)
    )


def trash():
    return (
        P('M51.5 78H76.5L74.6 94.5Q74.3 97.5 71.3 97.5H56.7Q53.7 97.5 53.4 94.5Z', 'white')
        + cut('M59.6 82.8L60 92.4M68.4 82.8L68 92.4', 3.6)
        + R(59.5, 65.8, 9, 6, 2.5, 'orange')
        + R(48.5, 70, 31, 7.5, 3.5, 'yellow')
    )


def public():
    return (
        C(72.5, 73.5, 5.6, 'yellow')
        + P('M63 95.5V91Q63 82 72.5 82Q82 82 82 91V93Q82 95.5 79.5 95.5Z', 'yellow')
        + C(57.5, 75.5, 6.4, 'white')
        + P('M46 97.5Q46 97.5 46 94Q46 84.5 57.5 84.5Q69 84.5 69 94V95Q69 97.5 66.5 97.5H48.5Q46 97.5 46 95Z', 'white')
    )


def box():
    return (
        P('M49.5 74L64 81.5V98.5L51 91.8Q49.5 91 49.5 89.3Z', 'cream')
        + P('M78.5 74V89.3Q78.5 91 77 91.8L64 98.5V81.5Z', 'sand')
        + P('M64 66L78.5 73.4L64 81L49.5 73.4Z', 'white')
        + path('M56 69.8L60.5 67.5L75 75L70.5 77.3Z', ORANGE)
        + path('M70.5 77.3L75 75V81.5L70.5 83.8Z', ORANGE)
    )


def phone():
    return (
        R(53.5, 65.5, 21, 33, 5.5, 'white')
        + R(56.8, 70, 14.4, 21, 2.5, 'aqua')
        + circle(64, 94.6, 1.9, CUT)
        + rect(59, 73, 4.4, 4.4, 1.2, YELLOW) + rect(64.6, 73, 4.4, 4.4, 1.2, ORANGE)
    )


def apps():
    return (
        R(49.5, 67.5, 13, 13, 4, 'white') + R(65.5, 67.5, 13, 13, 4, 'yellow')
        + R(49.5, 83.5, 13, 13, 4, 'yellow') + C(72, 90, 6.8, 'orange')
    )


def _fit(draw, k=1.22, dx=0, dy=0):
    """Enlarge a badge about its centre so it fills the disc (radius 30 in badge units).

    The disc centre sits at (63.3, 81.7) in badge units; the extra -0.5 lifts the
    symbol against its own drop shadow. dx/dy re-centre lopsided silhouettes.
    """
    def fitted():
        return f'<g transform="translate({63.3 + dx:g} {81.2 + dy:g}) scale({k}) translate(-64 -82)">{draw()}</g>'
    return fitted


NUDGE = {'games': (0, -2), 'cloud': (0, -1.6), 'backup': (0, 1.8), 'video': (0, 1.2), 'public': (0, -0.6)}
BADGES = {kind: _fit(draw, 1.22, *NUDGE.get(kind, (0, 0))) for kind, draw in {
    'home': home, 'download': download, 'music': music, 'pictures': pictures, 'video': video,
    'share': share, 'lock': lock, 'templates': templates, 'git': git, 'cloud': cloud,
    'text': text, 'desktop': desktop,
    'favorites': favorites, 'games': games, 'recent': recent, 'backup': backup, 'code': code,
    'books': books, 'camera': camera, 'mail': mail, 'print': print_, 'important': important,
    'network': network, 'root': root, 'trash': trash, 'public': public, 'box': box,
    'phone': phone, 'apps': apps,
}.items()}
