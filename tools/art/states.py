"""State variants built on a hero master: OVERLAYS = {asset: (base asset, fragment function)}.

The fragment is sculpted in clay and composited over the base image, so a
"full" trash can or an "open" folder is a different picture from the idle one.
"""
from artwork import path, rect, circle, line


def trash_full():
    # Crumpled paper balls piled in front of the bin and a sheet squeezed under the lid.
    return (path('M78 40L104 30Q108 30 108 34L104 52L84 50Z', 'white') +
            line('M86 42L100 37M88 47L100 44', '#d9c7a3', 2.4) +
            path('M22 96Q20 84 31 82Q36 74 46 80Q56 80 54 92Q58 104 46 106Q36 112 28 106Q18 104 22 96Z', 'cream') +
            line('M30 90L38 96L46 88M34 102L44 98', '#d9c7a3', 2.4) +
            path('M80 100Q78 90 88 88Q94 82 102 88Q110 90 108 100Q110 110 100 110Q90 114 84 108Q78 106 80 100Z', 'white') +
            line('M88 96L96 102L102 94', '#d9c7a3', 2.4) +
            path('M40 34L22 26Q18 26 19 30L24 46L38 46Z', 'cream') + line('M26 33L34 38', '#d9c7a3', 2.4))


def folder_open():
    # A sheet pulled up out of the folder with an orange tab, plus a second sheet behind it.
    return ('<g transform="rotate(-9 70 40)">' +
            rect(46, 14, 44, 46, 5, 'cream-dark') + rect(42, 10, 44, 48, 5, 'white') +
            line('M50 22H78M50 31H78M50 40H68', '#8fc0c4', 3.2) + rect(74, 6, 16, 9, 3, 'orange') + '</g>')


def folder_accept():
    # Drop target: a round plus badge at the lower right.
    return circle(94, 92, 18, 'olive') + line('M94 82V102M84 92H104', '#fbf5e6', 6)


def folder_new():
    return circle(94, 92, 18, 'yellow') + line('M94 82V102M84 92H104', '#fbf5e6', 6)


OVERLAYS = {
    'trash-full': ('trash', trash_full),
    'folder-open': ('folder', folder_open),
    'folder-accept': ('folder', folder_accept),
    'folder-new': ('folder', folder_new),
}
