"""Headless GTK icon lookup checks without a Python GI dependency."""
import ctypes as C
import ctypes.util
from pathlib import Path

def check(base):
    gtk_name = C.util.find_library('gtk-3')
    pix_name = C.util.find_library('gdk_pixbuf-2.0')
    if not gtk_name or not pix_name:
        return {'status': 'unavailable', 'reason': 'GTK 3 runtime libraries not installed'}
    gtk, pixels = C.CDLL(gtk_name), C.CDLL(pix_name)
    objects = C.CDLL(C.util.find_library('gobject-2.0'))
    gtk.gtk_icon_theme_new.restype = C.c_void_p
    gtk.gtk_icon_theme_set_search_path.argtypes = [C.c_void_p, C.POINTER(C.c_char_p), C.c_int]
    gtk.gtk_icon_theme_set_custom_theme.argtypes = [C.c_void_p, C.c_char_p]
    gtk.gtk_icon_theme_lookup_icon_for_scale.argtypes = [C.c_void_p, C.c_char_p, C.c_int, C.c_int, C.c_int]
    gtk.gtk_icon_theme_lookup_icon_for_scale.restype = C.c_void_p
    gtk.gtk_icon_info_get_filename.argtypes = [C.c_void_p]
    gtk.gtk_icon_info_get_filename.restype = C.c_char_p
    gtk.gtk_icon_info_load_icon.argtypes = [C.c_void_p, C.c_void_p]
    gtk.gtk_icon_info_load_icon.restype = C.c_void_p
    pixels.gdk_pixbuf_get_width.argtypes = [C.c_void_p]
    pixels.gdk_pixbuf_get_height.argtypes = [C.c_void_p]
    objects.g_object_unref.argtypes = [C.c_void_p]
    root = Path(base).resolve()
    rows = []
    names = ('folder', 'user-home', 'pcmanfm-qt', 'firefox', 'eduka-konekta',
             'libreoffice-writer', 'network-wireless-signal-excellent', 'battery-full-symbolic')
    for variant in ('Light', 'Dark'):
        theme = gtk.gtk_icon_theme_new()
        paths = (C.c_char_p * 1)(str(root).encode())
        gtk.gtk_icon_theme_set_search_path(theme, paths, 1)
        gtk.gtk_icon_theme_set_custom_theme(theme, f'Eduka-Icons-{variant}'.encode())
        try:
            for name in names:
                for size, scale in ((16, 1), (48, 1), (18, 2), (22, 2), (48, 2), (128, 2), (512, 2)):
                    # GTK can preserve a nearby natural size by default; FORCE_SIZE
                    # requests exact physical pixels for this rendering check.
                    info = gtk.gtk_icon_theme_lookup_icon_for_scale(theme, name.encode(), size, scale, 1 << 4)
                    assert info, f'GTK lookup missing: {variant} {name} {size}@{scale}'
                    try:
                        filename = gtk.gtk_icon_info_get_filename(info).decode()
                        assert Path(filename).resolve().is_relative_to(root / f'Eduka-Icons-{variant}'), filename
                        if scale == 2 and filename.endswith('.png'): assert '@2x' in filename, filename
                        pixbuf = gtk.gtk_icon_info_load_icon(info, None)
                        assert pixbuf, filename
                        try:
                            width, height = pixels.gdk_pixbuf_get_width(pixbuf), pixels.gdk_pixbuf_get_height(pixbuf)
                            assert width == height == size * scale, (name, size, scale, width, height)
                        finally: objects.g_object_unref(pixbuf)
                        rows.append({'variant': variant, 'name': name, 'size': size, 'scale': scale,
                                     'physical_pixels': width, 'file': str(Path(filename).relative_to(root))})
                    finally: objects.g_object_unref(info)
        finally: objects.g_object_unref(theme)
    return {'status': 'passed', 'checked': len(rows), 'lookups': rows}
