"""Small offline SVG renderer using the installed librsvg and Cairo libraries."""
import ctypes as C
import ctypes.util
from pathlib import Path


class _Rectangle(C.Structure):
    _fields_ = [('x', C.c_double), ('y', C.c_double), ('width', C.c_double), ('height', C.c_double)]


def _libraries():
    names = [C.util.find_library(n) for n in ('rsvg-2', 'cairo', 'gobject-2.0')]
    if not all(names):
        raise RuntimeError('Install librsvg2-2 and libcairo2 before rendering artwork.')
    rsvg, cairo, objects = [C.CDLL(n) for n in names]
    rsvg.rsvg_handle_new_from_file.argtypes = [C.c_char_p, C.c_void_p]
    rsvg.rsvg_handle_new_from_file.restype = C.c_void_p
    rsvg.rsvg_handle_render_document.argtypes = [C.c_void_p, C.c_void_p, C.POINTER(_Rectangle), C.c_void_p]
    rsvg.rsvg_handle_render_document.restype = C.c_int
    cairo.cairo_image_surface_create.argtypes = [C.c_int, C.c_int, C.c_int]
    cairo.cairo_image_surface_create.restype = C.c_void_p
    cairo.cairo_create.argtypes = [C.c_void_p]
    cairo.cairo_create.restype = C.c_void_p
    cairo.cairo_surface_write_to_png.argtypes = [C.c_void_p, C.c_char_p]
    cairo.cairo_surface_write_to_png.restype = C.c_int
    cairo.cairo_destroy.argtypes = [C.c_void_p]
    cairo.cairo_surface_destroy.argtypes = [C.c_void_p]
    objects.g_object_unref.argtypes = [C.c_void_p]
    return rsvg, cairo, objects


def render(source, size, destination):
    """Render the whole SVG document into a size x size PNG.

    The document is fitted into the square with its aspect ratio kept, so
    files with units (mm, em, %), with only a viewBox, or with a non-square
    canvas come out complete and undistorted.
    """
    rsvg, cairo, objects = _libraries()
    source, destination = Path(source), Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle = rsvg.rsvg_handle_new_from_file(str(source).encode(), None)
    if not handle:
        raise ValueError(f'Cannot load SVG: {source}')
    surface = cairo.cairo_image_surface_create(0, size, size)
    context = cairo.cairo_create(surface)
    try:
        viewport = _Rectangle(0.0, 0.0, float(size), float(size))
        if not rsvg.rsvg_handle_render_document(handle, context, C.byref(viewport), None):
            raise ValueError(f'Cannot render SVG: {source}')
        if cairo.cairo_surface_write_to_png(surface, str(destination).encode()):
            raise ValueError(f'Cannot save PNG: {destination}')
    finally:
        objects.g_object_unref(handle)
        cairo.cairo_destroy(context)
        cairo.cairo_surface_destroy(surface)
    return destination
