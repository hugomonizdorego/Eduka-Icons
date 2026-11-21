"""Building blocks of the Eduka line glyphs (24 x 24 grid, 2 px round strokes)."""


def S(d, width=2.0): return ('s', d, width)
def F(d): return ('f', d)
def C(x, y, r): return ('c', x, y, r)
def ring(x, y, r): return S(f'M{x + r} {y}A{r} {r} 0 1 0 {x - r} {y}A{r} {r} 0 1 0 {x + r} {y}')
SLASH = S('M3 3L21 21')
