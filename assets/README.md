# Artwork source

`masters/` contains the 17 original hero images encoded as lossless WebP.
Checksums and dimensions are recorded in `generated.json` and verified on every
build.

All other clay icons and the folder badges are composed in `tools/artwork.py`
and rendered with the clay lighting filter in `tools/clay.py`;
`tools/prepare_clay.py` writes the composition SVGs and PNG masters under
`build/`. Symbolic glyphs come from `tools/symbolic.py`. The Bright theme is
derived from the same masters with stronger colour (see `brighten()` in
`tools/build_theme.py`).

All artwork is distributed under this project's GPL-3.0 licence.
