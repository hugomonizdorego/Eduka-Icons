"""Build configuration: eduka-icons.toml merged over the defaults below."""
import copy
import functools
import os
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
# All generated files; EDUKA_ICONS_BUILD moves them (e.g. a RAM disk or a second tree).
BUILD = Path(os.environ.get('EDUKA_ICONS_BUILD', ROOT / 'build')).resolve()
DEFAULTS = {
    'build': {'variants': ['Light', 'Dark', 'Bright', 'Comfort'],
              'sizes': [16, 22, 24, 32, 48, 64, 96, 128, 256, 512],
              'hidpi': [16, 22, 24, 32, 48, 64, 128, 256],
              'app_sizes': [16, 22, 24, 32, 48, 64, 128], 'app_hidpi': [16, 24, 32, 64],
              'sharpen_up_to': 48, 'sharpen_percent': 100},
    'glyphs': {'style': 'mono', 'weight': 1.0, 'comfort_weight': 1.3,
               'colour': {'Light': '#183c35', 'Dark': '#e0e0e0', 'Bright': '#1d3a36', 'Comfort': '#16130f'}},
    'folders': {'default': 'aqua', 'max_size': 256,
                'colours': ['aqua', 'olive', 'orange', 'yellow', 'rose', 'blue', 'plum', 'grey']},
    'bright': {'saturation': 1.38, 'brightness': 1.0, 'contrast': 1.06},
    'comfort': {'outline': '#221d16', 'contrast': 1.14, 'saturation': 0.9, 'blue': 0.88},
}
KNOWN_VARIANTS = ('Light', 'Dark', 'Bright', 'Comfort')


def _merge(base, extra, path=''):
    for key, value in extra.items():
        if key not in base:
            raise SystemExit(f'eduka-icons.toml: unknown setting {path}{key}')
        if isinstance(base[key], dict):
            if not isinstance(value, dict):
                raise SystemExit(f'eduka-icons.toml: {path}{key} must be a table')
            _merge(base[key], value, f'{path}{key}.')
        else:
            if type(value) is not type(base[key]) and not (isinstance(base[key], float) and isinstance(value, int)):
                raise SystemExit(f'eduka-icons.toml: {path}{key} must be {type(base[key]).__name__}')
            base[key] = value


@functools.lru_cache(maxsize=1)
def load():
    config = copy.deepcopy(DEFAULTS)
    path = Path(os.environ.get('EDUKA_ICONS_CONFIG', ROOT / 'eduka-icons.toml'))
    if path.is_file():
        if tomllib is None:
            raise SystemExit('Reading eduka-icons.toml needs Python 3.11 or newer.')
        with path.open('rb') as stream:
            _merge(config, tomllib.load(stream))
    build = config['build']
    for key in ('sizes', 'hidpi', 'app_sizes', 'app_hidpi'):
        values = build[key]
        if not values or any(not isinstance(v, int) or not 8 <= v <= 1024 for v in values):
            raise SystemExit(f'eduka-icons.toml: build.{key} needs sizes between 8 and 1024')
        build[key] = sorted(set(values))
    unknown = [v for v in build['variants'] if v not in KNOWN_VARIANTS]
    if unknown or not build['variants']:
        raise SystemExit(f'eduka-icons.toml: build.variants may contain {", ".join(KNOWN_VARIANTS)}')
    if config['glyphs']['style'] not in ('mono', 'colour'):
        raise SystemExit('eduka-icons.toml: glyphs.style must be "mono" or "colour"')
    folders = config['folders']
    if folders['default'] not in folders['colours']:
        folders['colours'] = [folders['default'], *folders['colours']]
    return config


def physical(sizes, hidpi):
    """Pixel sizes needed for the logical sizes plus their @2x directories."""
    return tuple(sorted(set(sizes) | {size * 2 for size in hidpi}))
