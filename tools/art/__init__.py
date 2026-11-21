"""Detailed 1.0 clay compositions.

Every module in this package may define ``ART`` (kind -> function returning an
SVG fragment on the 128 x 128 grid) and ``BADGES`` (folder badge kind ->
fragment); they replace the simpler 0.x drawings of the same kind. ``OVERLAYS``
(asset -> (base asset, fragment)) adds state variants drawn over a hero master.
"""
import importlib
import os
import pkgutil
import sys

OVERRIDES, BADGES, OVERLAYS = {}, {}, {}
for _module in sorted(m.name for m in pkgutil.iter_modules(__path__)):
    try:
        _loaded = importlib.import_module(f'{__name__}.{_module}')
    except Exception as _error:  # a draft that does not import must not break the build tools
        if os.environ.get('EDUKA_ART_STRICT'):
            raise
        print(f'art: skipped {_module}: {_error}', file=sys.stderr)
        continue
    OVERRIDES.update(getattr(_loaded, 'ART', {}))
    BADGES.update(getattr(_loaded, 'BADGES', {}))
    OVERLAYS.update(getattr(_loaded, 'OVERLAYS', {}))
