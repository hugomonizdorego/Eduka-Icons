# Artwork source

All Eduka clay icons and the folder badges are composed as vector drawings in
`tools/art/` (one module per group) and `tools/artwork.py`, and rendered with
the clay lighting filter in `tools/clay.py`. `tools/prepare_clay.py` writes
the composition SVGs and PNG masters under `build/`. Flat glyphs come from
`tools/symbolic.py`, `tools/glyph_extra.py` and `tools/glyph_states.py`.

`masters/` keeps the 17 original hero images of the first releases as
lossless WebP for reference. They are no longer used by the build; their
checksums in `generated.json` are still verified by `make test`.

`upstream/` holds the pinned Papirus sources (GPL-3.0): application icons,
file-type and device icons, and the flat action/status/panel set, each as a
`tar.xz` named after the upstream commit, plus the upstream licence.

The Bright theme is derived from the same masters with stronger colour, the
Comfort theme with a dark contour and warmer, higher-contrast colours.

All artwork is distributed under this project's GPL-3.0 licence.
