"""Small offline SVG renderer using the installed librsvg and Cairo libraries."""
import ctypes as C
import ctypes.util
from pathlib import Path
import xml.etree.ElementTree as ET

def render(source, size, destination):
    names = [C.util.find_library(n) for n in ('rsvg-2', 'cairo', 'gobject-2.0')]
    if not all(names):
        raise RuntimeError('Install librsvg2-2 and libcairo2 before building artwork.')
    rsvg, cairo, objects = [C.CDLL(n) for n in names]
    rsvg.rsvg_handle_new_from_file.argtypes = [C.c_char_p, C.c_void_p]
    rsvg.rsvg_handle_new_from_file.restype = C.c_void_p
    rsvg.rsvg_handle_render_cairo.argtypes = [C.c_void_p, C.c_void_p]
    rsvg.rsvg_handle_render_cairo.restype = C.c_int
    cairo.cairo_image_surface_create.argtypes = [C.c_int, C.c_int, C.c_int]
    cairo.cairo_image_surface_create.restype = C.c_void_p
    cairo.cairo_create.argtypes = [C.c_void_p]
    cairo.cairo_create.restype = C.c_void_p
    cairo.cairo_scale.argtypes = [C.c_void_p, C.c_double, C.c_double]
    cairo.cairo_surface_write_to_png.argtypes = [C.c_void_p, C.c_char_p]
    cairo.cairo_surface_write_to_png.restype = C.c_int
    cairo.cairo_destroy.argtypes = [C.c_void_p]
    cairo.cairo_surface_destroy.argtypes = [C.c_void_p]
    objects.g_object_unref.argtypes = [C.c_void_p]
    source, destination = Path(source), Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    svg = ET.fromstring(source.read_text())
    width, height = float(svg.get('width', '128')), float(svg.get('height', '128'))
    handle = rsvg.rsvg_handle_new_from_file(str(source).encode(), None)
    if not handle:
        raise ValueError(f'Cannot load SVG: {source}')
    surface = cairo.cairo_image_surface_create(0, size, size)
    context = cairo.cairo_create(surface)
    try:
        cairo.cairo_scale(context, size / width, size / height)
        if not rsvg.rsvg_handle_render_cairo(handle, context):
            raise ValueError(f'Cannot render SVG: {source}')
        if cairo.cairo_surface_write_to_png(surface, str(destination).encode()):
            raise ValueError(f'Cannot save PNG: {destination}')
    finally:
        objects.g_object_unref(handle)
        cairo.cairo_destroy(context)
        cairo.cairo_surface_destroy(surface)
    return destination
