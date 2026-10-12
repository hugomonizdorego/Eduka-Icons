# Artwork source

`masters/` contains the 17 original hero images encoded as lossless WebP.
Each decoded RGBA image was compared byte-for-byte with its 0.3.0 PNG master.
Checksums and dimensions are recorded in `generated.json`.

Other icons and semantic folder badges are generated from `tools/artwork.py`,
`tools/clay.py`, and `tools/symbolic.py`. `tools/prepare_clay.py` writes the
temporary composition SVGs and PNG masters under `build/`, then
`tools/build_theme.py` exports the installed theme files.

The source tree carries no installed theme copies or third-party icon catalog.
All included artwork is distributed with this project's GPL-3.0 license.
