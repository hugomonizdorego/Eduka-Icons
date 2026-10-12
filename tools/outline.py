"""Convert simple stroked SVG paths into filled outlines.

GTK 3 and GTK 4 recolour symbolic icons by injecting
``rect,circle,path { fill: <fg> !important }`` into the SVG. A path that is
drawn only with ``stroke`` would therefore be filled as a solid blob. Every
Eduka symbolic glyph is converted into filled geometry with round caps and
round joins, so the recolouring keeps the intended line art.

Supported path commands: absolute M, L, H, V, Q, C, A and Z.
"""
import math
import re

TOKEN = re.compile(r'[MLHVQCAZmlhvqcaz]|-?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?')


def _arc(p0, rx, ry, phi, large, sweep, p1, steps_per_turn=48):
    """Flatten an SVG endpoint arc (SVG 1.1 implementation notes, F.6.5)."""
    x1, y1 = p0
    x2, y2 = p1
    if rx == 0 or ry == 0 or (x1, y1) == (x2, y2):
        return [p1]
    rx, ry = abs(rx), abs(ry)
    cos, sin = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    xp, yp = cos * dx + sin * dy, -sin * dx + cos * dy
    scale = (xp * xp) / (rx * rx) + (yp * yp) / (ry * ry)
    if scale > 1:
        rx, ry = rx * math.sqrt(scale), ry * math.sqrt(scale)
    num = rx * rx * ry * ry - rx * rx * yp * yp - ry * ry * xp * xp
    den = rx * rx * yp * yp + ry * ry * xp * xp
    factor = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        factor = -factor
    cxp, cyp = factor * rx * yp / ry, -factor * ry * xp / rx
    cx = cos * cxp - sin * cyp + (x1 + x2) / 2
    cy = sin * cxp + cos * cyp + (y1 + y2) / 2

    def angle(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    t1 = angle(1, 0, (xp - cxp) / rx, (yp - cyp) / ry)
    dt = angle((xp - cxp) / rx, (yp - cyp) / ry, (-xp - cxp) / rx, (-yp - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    steps = max(4, int(abs(dt) / (2 * math.pi) * steps_per_turn) + 1)
    points = []
    for i in range(1, steps + 1):
        t = t1 + dt * i / steps
        x, y = rx * math.cos(t), ry * math.sin(t)
        points.append((cos * x - sin * y + cx, sin * x + cos * y + cy))
    points[-1] = p1
    return points


def flatten(d):
    """Return a list of (points, closed) polylines for a path string."""
    tokens = TOKEN.findall(d)
    polylines, current, closed = [], [], False
    pos = start = (0.0, 0.0)
    command = None
    i = 0

    def number():
        nonlocal i
        value = float(tokens[i])
        i += 1
        return value

    def finish(is_closed):
        nonlocal current
        if len(current) > 1 or (current and is_closed):
            polylines.append((current, is_closed))
        current = []

    while i < len(tokens):
        if re.fullmatch(r'[A-Za-z]', tokens[i]):
            command = tokens[i]
            i += 1
            if command.islower():
                raise ValueError(f'Relative path commands are not supported: {d}')
            if command == 'Z':
                finish(True)
                pos = start
                continue
        if command == 'M':
            finish(False)
            pos = start = (number(), number())
            current = [pos]
            command = 'L'
        elif command == 'L':
            pos = (number(), number())
            current.append(pos)
        elif command == 'H':
            pos = (number(), pos[1])
            current.append(pos)
        elif command == 'V':
            pos = (pos[0], number())
            current.append(pos)
        elif command == 'Q':
            c, end = (number(), number()), (number(), number())
            for s in range(1, 13):
                t = s / 12
                current.append(((1 - t) ** 2 * pos[0] + 2 * (1 - t) * t * c[0] + t * t * end[0],
                                (1 - t) ** 2 * pos[1] + 2 * (1 - t) * t * c[1] + t * t * end[1]))
            pos = end
        elif command == 'C':
            c1, c2, end = (number(), number()), (number(), number()), (number(), number())
            for s in range(1, 17):
                t = s / 16
                u = 1 - t
                current.append((u ** 3 * pos[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * end[0],
                                u ** 3 * pos[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * end[1]))
            pos = end
        elif command == 'A':
            rx, ry, phi = number(), number(), number()
            large, sweep = bool(number()), bool(number())
            end = (number(), number())
            current.extend(_arc(pos, rx, ry, phi, large, sweep, end))
            pos = end
        else:
            raise ValueError(f'Unsupported path command {command!r} in {d}')
    finish(closed)
    return polylines


def _orient(points):
    """Return the points with a positive signed area (consistent winding)."""
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))
    return points if area > 0 else list(reversed(points))


def _fmt(points):
    return 'M' + 'L'.join(f'{x:.2f} {y:.2f}'.replace('.00', '') for x, y in points) + 'Z'


def _disc(center, radius, steps=16):
    return _orient([(center[0] + radius * math.cos(2 * math.pi * k / steps),
                     center[1] + radius * math.sin(2 * math.pi * k / steps)) for k in range(steps)])


def stroke(d, width=2.0):
    """Outline a stroked path as filled sub-paths (non-zero union)."""
    radius = width / 2
    parts = []
    for points, closed in flatten(d):
        clean = [points[0]]
        for p in points[1:]:
            if math.dist(p, clean[-1]) > 1e-6:
                clean.append(p)
        if closed and len(clean) > 1 and math.dist(clean[0], clean[-1]) > 1e-6:
            clean.append(clean[0])
        if len(clean) == 1:
            parts.append(_fmt(_disc(clean[0], radius)))
            continue
        for a, b in zip(clean, clean[1:]):
            length = math.dist(a, b)
            nx, ny = -(b[1] - a[1]) / length * radius, (b[0] - a[0]) / length * radius
            quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                    (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
            parts.append(_fmt(_orient(quad)))
        # Round joins and caps.
        for p in clean:
            parts.append(_fmt(_disc(p, radius, 12)))
    return ''.join(parts)


def fill(d):
    """Normalise a filled path so it shares the outline winding."""
    return ''.join(_fmt(_orient(points)) for points, _ in flatten(d) if len(points) > 2)
