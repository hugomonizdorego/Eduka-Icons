"""Headless GTK 3 icon lookups without a Python GI dependency.

Checks exact-size and HiDPI lookups, and that GTK's symbolic recolouring
(which forces ``fill`` on every path) keeps the Eduka line art intact.
"""
import ctypes as C
import ctypes.util
from pathlib import Path

NAMES = ('folder', 'user-home', 'system-file-manager', 'internet-web-browser', 'eduka-konekta', 'libreoffice-writer',
         'preferences-desktop-locale', 'utilities-system-monitor', 'help-about', 'face-smile',
         'network-wireless-signal-excellent', 'battery-full-symbolic')
SYMBOLIC = ('network-wireless-signal-excellent-symbolic', 'emblem-ok-symbolic', 'window-close-symbolic',
            'pan-down-symbolic', 'system-shutdown-symbolic', 'go-next-symbolic', 'edit-copy-symbolic')


class RGBA(C.Structure):
    _fields_ = [('red', C.c_double), ('green', C.c_double), ('blue', C.c_double), ('alpha', C.c_double)]


def _libraries():
    gtk_name = C.util.find_library('gtk-3')
    pix_name = C.util.find_library('gdk_pixbuf-2.0')
    if not gtk_name or not pix_name:
        return None
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
    gtk.gtk_icon_info_load_symbolic.argtypes = [C.c_void_p, C.POINTER(RGBA), C.c_void_p, C.c_void_p,
                                                 C.c_void_p, C.POINTER(C.c_int), C.c_void_p]
    gtk.gtk_icon_info_load_symbolic.restype = C.c_void_p
    for name in ('width', 'height', 'rowstride', 'n_channels'):
        getattr(pixels, f'gdk_pixbuf_get_{name}').argtypes = [C.c_void_p]
    pixels.gdk_pixbuf_get_pixels.argtypes = [C.c_void_p]
    pixels.gdk_pixbuf_get_pixels.restype = C.POINTER(C.c_ubyte)
    objects.g_object_unref.argtypes = [C.c_void_p]
    return gtk, pixels, objects


def _alpha(pixels, pixbuf):
    """Return (opaque pixel count, sum of red where opaque)."""
    width, height = pixels.gdk_pixbuf_get_width(pixbuf), pixels.gdk_pixbuf_get_height(pixbuf)
    stride, channels = pixels.gdk_pixbuf_get_rowstride(pixbuf), pixels.gdk_pixbuf_get_n_channels(pixbuf)
    data = pixels.gdk_pixbuf_get_pixels(pixbuf)
    covered = 0
    for y in range(height):
        for x in range(width):
            if channels == 4 and data[y * stride + x * 4 + 3] > 127:
                covered += 1
    return covered, width * height


APPS = ('gimp', 'inkscape', 'krita', 'google-chrome', 'brave-browser', 'telegram-desktop', 'whatsapp',
        'pcmanfm-qt', 'org.kde.kalzium', 'org.gnome.Nautilus', 'steam')


def check(base, variants=('Light', 'Dark', 'Bright', 'Comfort')):
    libraries = _libraries()
    if not libraries:
        return {'status': 'unavailable', 'reason': 'GTK 3 runtime libraries not installed'}
    gtk, pixels, objects = libraries
    root = Path(base).resolve()
    rows = []
    for variant in variants:
        theme = gtk.gtk_icon_theme_new()
        paths = (C.c_char_p * 1)(str(root).encode())
        gtk.gtk_icon_theme_set_search_path(theme, paths, 1)
        gtk.gtk_icon_theme_set_custom_theme(theme, f'Eduka-Icons-{variant}'.encode())
        try:
            for name in NAMES:
                for size, scale in ((16, 1), (48, 1), (22, 2), (48, 2), (128, 2), (256, 2)):
                    # FORCE_SIZE requests exact physical pixels for this check.
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
                                     'file': str(Path(filename).relative_to(root))})
                    finally: objects.g_object_unref(info)
            apps_theme = root / ('Eduka-Icons-Apps-Comfort' if variant == 'Comfort' else 'Eduka-Icons-Apps')
            seen = {}
            for name in APPS:
                for size, scale in ((16, 1), (48, 1), (64, 2)):
                    info = gtk.gtk_icon_theme_lookup_icon_for_scale(theme, name.encode(), size, scale, 0)
                    assert info, f'GTK app lookup missing: {variant} {name}'
                    try:
                        filename = Path(gtk.gtk_icon_info_get_filename(info).decode())
                        assert filename.resolve().is_relative_to(apps_theme), (variant, name, filename)
                        if size == 48: seen.setdefault(filename.resolve(), []).append(name)
                    finally: objects.g_object_unref(info)
                rows.append({'variant': variant, 'name': name, 'app_theme': 'ok'})
            shared = {str(k): v for k, v in seen.items() if len(v) > 1}
            assert not shared, f'Different applications share one icon: {shared}'
            red = RGBA(1.0, 0.0, 0.0, 1.0)
            for name in SYMBOLIC:
                info = gtk.gtk_icon_theme_lookup_icon_for_scale(theme, name.encode(), 32, 1, 1 << 4)
                assert info, f'GTK symbolic lookup missing: {variant} {name}'
                try:
                    plain = gtk.gtk_icon_info_load_icon(info, None)
                    was_symbolic = C.c_int(0)
                    tinted = gtk.gtk_icon_info_load_symbolic(info, C.byref(red), None, None, None, C.byref(was_symbolic), None)
                    assert plain and tinted and was_symbolic.value, f'GTK could not recolour {name}'
                    try:
                        before, total = _alpha(pixels, plain)
                        after, _ = _alpha(pixels, tinted)
                        # A stroked path filled by GTK would cover far more pixels.
                        assert 0 < after <= before * 1.15 + 4 and after < total * 0.7, (variant, name, before, after)
                    finally:
                        objects.g_object_unref(plain); objects.g_object_unref(tinted)
                    rows.append({'variant': variant, 'name': name, 'symbolic_recolour': 'ok'})
                finally: objects.g_object_unref(info)
        finally: objects.g_object_unref(theme)
    return {'status': 'passed', 'checked': len(rows), 'lookups': rows}
