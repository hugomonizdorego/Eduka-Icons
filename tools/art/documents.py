"""Eduka-Icons 1.0 clay artwork: document types and paper goods.

doc-sheet, doc-slides, doc-pdf and doc-zip continue the "document page" family
of art/office.py (same sheet, folded corner and title tab, one accent colour
and one inner object each); notes, book, package, download and code are
freestanding objects. Every function returns an SVG fragment on the 128 x 128
grid; tools/clay.py sculpts each shape element separately. GPL-3.0.
"""
from artwork import path, rect, circle, line

CREAM, WHITE, CREAM_D = '#f4e8cf', '#fbf5e6', '#d9c7a3'
ORANGE, ORANGE_D, YELLOW, YELLOW_D = '#e0703a', '#b9552a', '#eec14f', '#cf9f33'
OLIVE, OLIVE_D = '#7d8c55', '#5f6c40'
AQUA, AQUA_D, CHARCOAL = '#8fc0c4', '#6a9ea3', '#3f3c37'
BRICK, CARDBOARD_D = '#8f3f1f', '#a87f2b'


# --------------------------------------------------------------------------
# The shared sheet (identical to art/office.py): 70 x 85 with a 20 unit dog-ear.
SHEET = 'M36 16L77 16L97 36L97 92Q97 101 88 101L36 101Q27 101 27 92L27 25Q27 16 36 16Z'
EAR = 'M77 16L77 30Q77 36 83 36L97 36Z'


def sheet(accent, tab=True, depth=4.5):
    s = path(SHEET, 'cream-dark', transform=f'translate(0 {depth})') + path(SHEET, 'cream')
    s += path(EAR, accent)
    if tab:
        s += rect(35, 25, 30, 8, 4, accent)
    return s


# --------------------------------------------------------------------------
def doc_sheet():
    """Spreadsheet: olive tab and an olive table slab with clay cells."""
    s = sheet('olive')
    s += rect(34, 46.5, 56, 47, 6, 'olive-dark') + rect(34, 44, 56, 47, 6, 'olive')
    xs, ys = (38, 55.5, 73), (48, 59, 70, 81)
    for r, y in enumerate(ys):
        for c, x in enumerate(xs):
            colour = 'yellow' if r == 0 else 'orange' if (r, c) == (2, 1) else 'white'
            s += rect(x, y, 14.5, 7.5, 2.5, colour)
    return s


# --------------------------------------------------------------------------
def doc_slides():
    """Presentation: orange tab, a framed slide on a stand with pie and bars."""
    s = sheet('orange')
    # stand
    s += rect(58.5, 80, 7, 13, 2, 'orange-dark') + rect(46, 90, 32, 6, 3, 'orange-dark')
    # screen
    s += rect(34, 45.5, 56, 39, 6, 'orange-dark') + rect(34, 43, 56, 39, 6, 'orange')
    s += rect(38, 47, 48, 31, 3.5, 'white')
    # pie chart with a pulled slice
    s += circle(52, 62.5, 10.5, 'yellow')
    s += path('M53.5 61L53.5 49.5Q64 50.5 65 61Z', 'orange')
    # rising bars
    s += rect(68.5, 63, 5, 11, 2, 'olive') + rect(76, 55, 5, 19, 2, 'olive')
    return s


# --------------------------------------------------------------------------
def doc_pdf():
    """PDF: brick-red tab and a ribbon label wrapped around the page."""
    s = path('M20 84L27 84L27 91Z', BRICK)
    s += sheet('orange-dark')
    s += line('M37 47H87', CREAM_D, 5.5)
    s += line('M37 93H70', CREAM_D, 5.5)
    s += rect(20, 62.5, 71, 24, 5, BRICK) + rect(20, 60, 71, 24, 5, 'orange-dark')
    letters = ('M33 78.5V65.5H38.5Q43.5 65.5 43.5 69.75Q43.5 74 38.5 74H33'
               'M51 65.5V78.5H55Q62.5 78.5 62.5 72Q62.5 65.5 55 65.5Z'
               'M70 78.5V65.5H79.5M70 72.5H77.5')
    s += line(letters, WHITE, 4.6)
    return s


# --------------------------------------------------------------------------
def doc_zip():
    """Archive: yellow corner and a zip fastener running down the whole page."""
    s = sheet('yellow', tab=False)
    s += rect(52, 16, 20, 85, 2.5, 'gold')
    for i in range(13):
        y = 19.5 + i * 6.2
        s += rect(54.5, y, 8.5, 3.5, 1.6, 'white') + rect(61, y + 3.1, 8.5, 3.5, 1.6, 'white')
    # slider and pull tab
    slider = 'M53 55H71Q76 55 75 60L72.5 71Q72 74 68 74H56Q52 74 51.5 71L49 60Q48 55 53 55Z'
    s += path(slider, 'orange-dark', transform='translate(0 2.5)') + path(slider, 'orange')
    s += rect(57, 68.5, 10, 25, 5, 'orange-dark') + rect(57, 66, 10, 25, 5, 'orange')
    s += circle(62, 84.5, 2.6, 'cream')
    return s


# --------------------------------------------------------------------------
def notes():
    """Notepad: yellow legal pad, orange binding with cream rings, a bullet list."""
    s = rect(96, 44, 11, 14, 3.5, 'olive')                      # index tab
    s += rect(22, 24, 80, 82, 10, 'orange-dark')             # back board
    s += rect(26, 22, 72, 80, 7, 'cream-dark')               # the pages below
    s += path('M33 20H91Q98 20 98 27V80L80 98H33Q26 98 26 91V27Q26 20 33 20Z', 'yellow')
    s += path('M98 80L80 98L80 87Q80 80 87 80Z', 'white')     # curled corner
    s += path('M33 20H91Q98 20 98 27V37H26V27Q26 20 33 20Z', 'orange')
    for x in (36, 49, 62, 75, 88):
        s += circle(x, 31, 3, 'charcoal') + rect(x - 2.5, 16, 5, 15, 2.5, 'cream')
    s += line('M45 50H88M45 62H88M45 74H80M45 86H68', OLIVE_D, 4.6)
    for y in (50, 62, 74, 86):
        s += circle(35.5, y, 3, 'orange')
    return s


# --------------------------------------------------------------------------
def book():
    """Open book: orange cover, two arched page blocks, a picture and a ribbon."""
    cover = ('M21 30H105Q109 30 109 34V94Q109 99 104 99H70Q65 99 63 102Q61 99 56 99H22'
             'Q17 99 17 94V34Q17 30 21 30Z')
    left = 'M21 {0}C35 {1} 53 {2} 63 {3}V{4}C53 {5} 35 {6} 21 {7}Z'
    right = 'M105 {0}C91 {1} 73 {2} 63 {3}V{4}C73 {5} 91 {6} 105 {7}Z'

    def pages(top, c):
        ys = [top + v for v in (4, -2, -4, 6, 70, 60, 62, 68)]
        return path(left.format(*ys), c) + path(right.format(*ys), c)
    s = path(cover, 'orange-dark', transform='translate(0 3.5)') + path(cover, 'orange')
    s += path('M69 88H79V105L74 100.5L69 105Z', 'yellow')     # bookmark ribbon
    s += pages(28, 'cream-dark') + pages(23, 'white')
    # left page: a little landscape and a caption
    s += rect(28, 37, 27, 21, 4, 'aqua')
    s += circle(47.5, 44, 3.4, 'yellow')
    s += path('M28 54L36 46Q39 43.5 42 46.5L52 58H32Q28 58 28 54Z', 'olive')
    s += line('M29 68Q42 64.5 55 69M29 78Q39 75 48 77.5', OLIVE, 4.2)
    # right page: heading and text
    s += line('M71 43Q82 38 91 40', ORANGE, 5)
    s += line('M71 54Q84 49.5 97 53M71 65Q84 60.5 97 64M71 76Q80 72.5 88 74', OLIVE, 4.2)
    return s


# --------------------------------------------------------------------------
def package():
    """Cardboard box: two top flaps sealed with orange tape, label, 'this side up'."""
    front = 'M18 48H108V95Q108 103 100 103H26Q18 103 18 95Z'
    s = path(front, CARDBOARD_D, transform='translate(0 3)') + path(front, 'yellow-dark')
    # top flaps, seen from above
    s += path('M30 25H62.5V48H18L25 28.5Q26.5 25 30 25Z', 'yellow')
    s += path('M63.5 25H96Q99.5 25 101 28.5L108 48H63.5Z', 'yellow')
    # tape over the seam and down the front
    s += path('M55.5 25H70.5L72 48H54Z', 'orange')
    s += path('M54 48H72V66L67.5 62L63 66L58.5 62L54 66Z', 'orange-dark')
    # shipping label
    s += rect(26, 68, 30, 24, 4, 'cream')
    s += line('M32 76H50', OLIVE_D, 4.2)
    s += path('M32 85H50', 'none', stroke=CHARCOAL, stroke_width=5, stroke_dasharray='3 2.4')
    # this side up
    arrows = 'M80 90V75M74 80L80 73.5L86 80M96 90V75M90 80L96 73.5L102 80'
    s += line(arrows, BRICK, 4.4)
    return s


# --------------------------------------------------------------------------
def download():
    """Download: a thick orange arrow dropping into a cream in-tray."""
    arrow = ('M54 17.5H72Q76.5 17.5 76.5 22V44H89Q95 44 91 49L67 77.5Q63 82 59 77.5L35 49Q31 44 37 44H49.5V22'
             'Q49.5 17.5 54 17.5Z')
    lip = ('M16 70H40Q44 70 46 74Q50 84 58 84H68Q76 84 80 74Q82 70 86 70H110V94Q110 102 102 102'
           'H24Q16 102 16 94Z')
    s = path('M24 62H102Q106 62 106 66V92H20V66Q20 62 24 62Z', 'olive-dark')
    s += path(arrow, 'orange-dark', transform='translate(2 3)') + path(arrow, 'orange')
    s += path(lip, 'cream-dark', transform='translate(0 3.5)') + path(lip, 'cream')
    # progress bar and light
    s += rect(26, 90, 58, 6, 3, 'olive-dark') + rect(26, 90, 36, 6, 3, 'yellow')
    s += circle(97, 93, 3.6, 'orange')
    return s


# --------------------------------------------------------------------------
def code():
    """Code window: cream frame, three clay buttons, dark editor with </> and code pills."""
    s = rect(18, 24, 90, 80, 11, 'cream-dark') + rect(18, 20, 90, 80, 11, 'cream')
    s += circle(28.5, 29, 3.3, 'orange') + circle(38.5, 29, 3.3, 'yellow') + circle(48.5, 29, 3.3, 'olive')
    s += rect(62, 25.5, 38, 7, 3.5, 'cream-dark')
    s += rect(23, 38, 80, 57, 7, 'charcoal')
    s += line('M49 49L37 61L49 73M77 49L89 61L77 73', AQUA, 6.5)
    s += line('M68 46L58 76', ORANGE, 6.5)
    s += rect(30, 83, 18, 5.5, 2.75, 'yellow') + rect(52, 83, 26, 5.5, 2.75, 'olive')
    s += rect(82, 83, 14, 5.5, 2.75, 'cream')
    return s


ART = {
    'doc-sheet': doc_sheet,
    'doc-slides': doc_slides,
    'doc-pdf': doc_pdf,
    'doc-zip': doc_zip,
    'notes': notes,
    'book': book,
    'package': package,
    'download': download,
    'code': code,
}
