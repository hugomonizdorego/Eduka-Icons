"""State families: every state of a tray or status icon gets its own glyph.

A battery that is charging at 20 % must not look like one charging at 90 %, and
"offline" must not look like "available". Merged after glyph_extra.

GLYPHS:  kind -> items (glyph_items)
DERIVED: kind -> (existing kind, extra items)
SYMBOLS: icon name -> (kind, 'alias alias ...', context)
"""
from glyph_items import S, F, C, ring, SLASH  # noqa: F401

_BODY = S('M1.5 7H14.5V17H1.5ZM16.6 10.5V13.5')          # compact battery, room for the bolt
_BOLT = F('M22 5.5L18.2 12.7H20.6L19.5 18.5L23.6 11.2H21.2Z')
_HEAD, _SHOULDERS = ring(10, 7.5, 3.6), S('M3 20Q3 13.6 10 13.6Q12.6 13.6 14.2 14.5')
_CLOUD = S('M7.5 15H17Q20.5 15 20.5 11.8Q20.5 8.9 17.4 8.6Q16.6 5 12.7 5Q9.3 5 8.3 8.2Q4 8.4 4 11.7Q4 15 7.5 15Z')
_SMALL_CLOUD = S('M9.5 19.5H17.8Q21.5 19.5 21.5 16.2Q21.5 13.3 18.4 13Q17.6 9.8 14.1 9.8Q11 9.8 10 12.7Q6.8 12.9 6.8 16.2Q6.8 19.5 9.5 19.5Z')
_MAIL = S('M3 5H21V19H3Z')
_SPEAKER = S('M3 9H7L12 5V19L7 15H3Z')
_LENS = [ring(10.5, 10.5, 6.5), S('M15.5 15.5L21 21')]


def _charge(width):
    return [_BODY, _BOLT] + ([F(f'M4 9.5H{4 + width}V14.5H4Z')] if width else [])


GLYPHS = {
    # Battery: charging at each level, and the warning state.
    'battery-charge-full': _charge(8), 'battery-charge-good': _charge(6), 'battery-charge-medium': _charge(4),
    'battery-charge-low': _charge(2), 'battery-charge-empty': _charge(0),
    'battery-caution': [S('M3 6H19V18H3ZM21 10V14'), S('M11 8.8V12.6'), C(11, 15.4, 1.2)],
    # Wi-Fi "good": between ok and excellent (short outer arc).
    'wifi-good': [C(12, 19.5, 1.6), S('M8.5 15.5Q12 12.5 15.5 15.5'), S('M5.5 12Q12 6.5 18.5 12'),
                  S('M8 5.6Q12 3.9 16 5.6')],
    'wifi-connecting': [C(12, 19.5, 1.6), S('M8.5 15.5Q12 12.5 15.5 15.5'), C(5, 9.5, 1.1), C(12, 6.2, 1.1), C(19, 9.5, 1.1)],
    'wifi-error': [C(9.5, 19.5, 1.6), S('M6 15.5Q9.5 12.5 13 15.5'), S('M3 12Q9.5 6.5 16 12'), S('M20 8V15'), C(20, 18.6, 1.2)],
    'wired-connecting': [S('M4 4H20V15H4ZM12 15V20M7 20H17'), C(8, 9.5, 1.1), C(12, 9.5, 1.1), C(16, 9.5, 1.1)],
    'wired-error': [S('M4 4H20V15H4ZM12 15V20M7 20H17'), S('M12 6.8V9.8'), C(12, 12.3, 1.1)],
    # Volume: medium sits between low and high.
    'volume-medium': [_SPEAKER, S('M15.5 9.5Q18 12 15.5 14.5'), S('M18.2 7.2Q22.6 12 18.2 16.8', 1.4)],
    # Presence.
    'user-available': [_HEAD, _SHOULDERS, C(18.5, 18.5, 3.4)],
    'user-away': [_HEAD, _SHOULDERS, ring(18.5, 18.5, 2.9)],
    'user-busy': [_HEAD, _SHOULDERS, S('M15.2 18.5H21.8', 2.6)],
    'user-offline': [_HEAD, _SHOULDERS, S('M16.2 16.2L20.8 20.8M20.8 16.2L16.2 20.8', 1.8)],
    'user-invisible': [_HEAD, S('M3 20Q3 13.6 10 13.6Q12.6 13.6 14.2 14.5', 1.2), S('M15.5 18.5H16.2M18.2 18.5H18.9M20.9 18.5H21.6', 1.8)],
    # Weather.
    'weather-few-clouds': [_SMALL_CLOUD, S('M5.2 9.6A3.12 3.12 0 1 1 10.5 6.6'),
                           S('M7.5 1.2V2.4M2.6 3L3.5 3.9M1 8H2.2M12.4 3L11.5 3.9', 1.6)],
    'weather-clear-night': [S('M19.5 14.2A8 8 0 1 1 9.8 4.5A6.2 6.2 0 0 0 19.5 14.2Z'), S('M17 3.2V6.2M15.5 4.7H18.5', 1.4)],
    'weather-few-clouds-night': [_SMALL_CLOUD, S('M9.4 2.2A4.3 4.3 0 0 0 5.3 9.9A5.4 5.4 0 0 1 9.4 2.2Z')],
    'weather-overcast': [_CLOUD, S('M6 19H18', 1.8)],
    'weather-showers': [_CLOUD, S('M8.5 17.5L7.3 21M12.6 17.5L11.4 21M16.7 17.5L15.5 21', 1.8)],
    'weather-showers-scattered': [_CLOUD, S('M10 17.5L8.8 21M15.2 17.5L14 21', 1.8)],
    'weather-storm': [_CLOUD, F('M13.2 15.6L9 20H11.6L10.4 23.4L15 18.6H12.2Z')],
    'weather-snow': [_CLOUD, C(8, 18.6, 1.15), C(12.2, 20.6, 1.15), C(16.4, 18.6, 1.15)],
    'weather-fog': [_CLOUD, S('M5 18H19M7.5 21H16.5', 1.8)],
    'weather-windy': [S('M2.5 9H13.5Q16.5 9 16.5 6.6Q16.5 4.6 14.4 4.6Q12.8 4.6 12.5 6'),
                      S('M2.5 13H18Q21.5 13 21.5 15.8Q21.5 18.4 19 18.4Q17.2 18.4 16.8 16.8'), S('M2.5 17H11')],
    # Actions that used to share one glyph.
    'sort-descending': [S('M7 20V4M3 8L7 4L11 8M17 4V20M13 16L17 20L21 16')],
    'sort-plain': [S('M4 7H20M4 12H15M4 17H10')],
    'rotate-left': [S('M4 12A8 8 0 1 0 9.5 4.4M4 3V8H9')],
    'zoom-fit-width': [S('M3 5V19M21 5V19M7 12H17M9.5 9.5L7 12L9.5 14.5M14.5 9.5L17 12L14.5 14.5')],
    'zoom-fit-height': [S('M5 3H19M5 21H19M12 7V17M9.5 9.5L12 7L14.5 9.5M9.5 14.5L12 17L14.5 14.5')],
    'split-vertical': [S('M3 4H21V20H3ZM3 12H21')],
    'mail-read': [S('M3 10L12 3.5L21 10V20H3ZM3 10.5L12 16L21 10.5')],
    'mail-forward': [_MAIL, S('M7.5 12H16M13 9L16 12L13 15')],
    'mail-reply': [_MAIL, S('M16.5 12H8M11 9L8 12L11 15')],
    'mail-reply-all': [_MAIL, S('M17.5 12H10.5M13.2 9.3L10.5 12L13.2 14.7M8.6 9.3L5.9 12L8.6 14.7')],
    'mail-junk': [_MAIL, S('M8.5 8.5L15.5 15.5M15.5 8.5L8.5 15.5')],
    'mail-important': [_MAIL, S('M12 8V12.6'), C(12, 15.6, 1.2)],
    'mail-signed': [_MAIL, S('M8 12.2L11 15L16.2 9.4')],
    'seek-backward': [S('M12 6L4 12L12 18ZM21 6L13 12L21 18Z')],
    'seek-forward': [S('M12 6L20 12L12 18ZM3 6L11 12L3 18Z')],
    'save-as': [S('M4 3H15L19 7V11M4 3V21H10M7.5 3V8H13.5V3'), S('M20.3 13.4L22.6 15.7L16 22.3H13.7V20Z', 1.6)],
    'star-half': [S('M12 2.5L14.9 8.6L21.5 9.4L16.6 13.9L17.9 20.5L12 17.2L6.1 20.5L7.4 13.9L2.5 9.4L9.1 8.6Z', 1.6),
                  F('M12 2.5V17.2L6.1 20.5L7.4 13.9L2.5 9.4L9.1 8.6Z')],
    'brightness-low': [ring(12, 12, 3.6), C(12, 4.4, 1.1), C(12, 19.6, 1.1), C(4.4, 12, 1.1), C(19.6, 12, 1.1)],
    'keyboard-brightness': [S('M3 13H21V20H3ZM7 16.5H17', 1.8), S('M12 3.5V6.5M6.5 5.5L8.3 8M17.5 5.5L15.7 8', 1.8)],
    'trash-full': [S('M4 7H20M9 7V4H15V7M6 7L7 21H17L18 7'), F('M8.8 10.5H15.2L14.6 18.5H9.4Z')],
}

DERIVED = {
    'airplane-off': ('airplane', [SLASH]),
    'night-light-off': ('suspend', [SLASH]),
    'vpn-off': ('vpn', [SLASH]),
    'touchpad-off': ('touchpad', [SLASH]),
    'camera-off': ('camera', [SLASH]),
    'call-off': ('call', [S('M21 3L3 21')]),
}

_CHARGING = {'full': '100 090 90', 'good': '080 80 070 70 060 60', 'medium': '050 50 040 40 030 30',
             'low': '020 20 010 10', 'empty': '000 0'}
_LEVELS = {'full': '100 090', 'good': '080 070 060', 'medium': '050 040 030', 'low': '020 010', 'empty': '000'}


def _battery():
    out = {}
    for level, numbers in _CHARGING.items():
        aliases = [f'battery-level-{n}-charging' for n in numbers.split() if not n.startswith('0') or n == '0']
        aliases += [f'battery-{n}-charging' for n in numbers.split() if len(n) == 3]
        aliases += [f'battery-{level}-charged'] if level == 'full' else []
        aliases += ['battery-level-100-charged', 'battery-charged', 'gpm-battery-charged', 'battery-100-charged'] if level == 'full' else []
        aliases += ['battery-caution-charging'] if level == 'low' else []
        out[f'battery-{level}-charging'] = (f'battery-charge-{level}', ' '.join(aliases), 'status')
    return out


SYMBOLS = {
    **_battery(),
    'battery-full': ('battery-full', 'battery-level-100 battery-level-90 battery-100 battery-090 gpm-battery-100', 'status'),
    'battery-good': ('battery-good', 'battery-level-80 battery-level-70 battery-level-60 battery-080 battery-070 battery-060 gpm-battery-080 gpm-battery-060', 'status'),
    'battery-medium': ('battery-medium', 'battery-level-50 battery-level-40 battery-level-30 battery-050 battery-040 battery-030 gpm-battery-040', 'status'),
    'battery-low': ('battery-low', 'battery-level-20 battery-level-10 battery-020 battery-010 gpm-battery-020', 'status'),
    'battery-caution': ('battery-caution', 'battery-action', 'status'),
    'battery-empty': ('battery-empty', 'battery-level-0 battery-000 gpm-battery-000', 'status'),
    'battery-missing': ('battery-missing', 'gpm-battery-missing', 'status'),
    'network-wireless-signal-excellent': ('wifi-high', 'network-wireless-connected network-wireless network-wireless-hotspot '
                                          'network-wireless-connected-100 nm-signal-100 network-wireless-100', 'status'),
    'network-wireless-signal-good': ('wifi-good', 'network-wireless-connected-75 nm-signal-75 network-wireless-80 network-wireless-60', 'status'),
    'network-wireless-signal-ok': ('wifi-medium', 'network-wireless-connected-50 nm-signal-50 network-wireless-40', 'status'),
    'network-wireless-signal-weak': ('wifi-low', 'network-wireless-connected-25 nm-signal-25 network-wireless-20', 'status'),
    'network-wireless-signal-none': ('wifi-none', 'network-wireless-connected-00 nm-signal-00 network-wireless-0', 'status'),
    'network-wireless-acquiring': ('wifi-connecting', 'nm-stage01-connecting01 nm-stage02-connecting01 nm-stage03-connecting01', 'status'),
    'network-wireless-no-route': ('wifi-error', 'network-wireless-error network-wireless-limited', 'status'),
    'network-wireless-offline': ('wifi-off', 'network-wireless-disabled network-wireless-disconnected network-wireless-hardware-disabled '
                                 'network-wireless-disconnected-symbolic nm-no-connection', 'status'),
    'network-wired': ('wired', 'network-wired-activated network-transmit-receive network-idle network-transmit network-receive '
                      'nm-device-wired network-wired-connected', 'status'),
    'network-wired-acquiring': ('wired-connecting', '', 'status'),
    'network-wired-no-route': ('wired-error', 'network-error network-wired-error', 'status'),
    'network-wired-disconnected': ('wired-off', 'network-offline network-disconnect network-wired-offline network-wired-unavailable', 'status'),
    'network-vpn': ('vpn', 'network-vpn-acquiring nm-vpn-standalone-lock', 'status'),
    'network-vpn-disconnected': ('vpn-off', 'network-vpn-disabled network-vpn-no-route', 'status'),
    'airplane-mode': ('airplane', 'airplane-mode-on', 'status'),
    'airplane-mode-disabled': ('airplane-off', 'airplane-mode-off', 'status'),
    'night-light': ('suspend', 'redshift-status-on', 'status'),
    'night-light-disabled': ('night-light-off', 'redshift-status-off', 'status'),
    'audio-volume-high': ('volume-high', 'audio-volume-overamplified audio-volume-high-panel', 'status'),
    'audio-volume-medium': ('volume-medium', 'audio-volume-medium-panel', 'status'),
    'audio-volume-low': ('volume-low', 'audio-volume-low-panel', 'status'),
    'audio-volume-zero': ('volume-zero', 'audio-volume-zero-panel audio-volume-off', 'status'),
    'audio-volume-muted': ('volume-mute', 'audio-volume-muted-blocking audio-volume-muted-panel', 'status'),
    'bluetooth-active': ('bluetooth', 'bluetooth-paired bluetooth blueman-tray blueman blueman-active preferences-system-bluetooth-activated', 'status'),
    'bluetooth-disabled': ('bluetooth-off', 'bluetooth-disconnected blueman-disabled bluetooth-inactive preferences-system-bluetooth-inactive', 'status'),
    'notification-active': ('bell', 'notifications preferences-system-notifications notification-new notification notification-symbolic', 'status'),
    'display-brightness': ('brightness', 'display-brightness-high display-brightness-medium', 'status'),
    'display-brightness-low': ('brightness-low', 'display-brightness-off', 'status'),
    'keyboard-brightness': ('keyboard-brightness', 'input-keyboard-brightness', 'status'),
    'touchpad-disabled': ('touchpad-off', 'input-touchpad-off touchpad-indicator-off', 'status'),
    'camera-disabled': ('camera-off', 'camera-off', 'status'),
    'call-stop': ('call-off', 'call-end call-missed', 'actions'),
    'user-available': ('user-available', 'user-online', 'status'),
    'user-away': ('user-away', 'user-idle user-away-extended', 'status'),
    'user-busy': ('user-busy', 'user-dnd', 'status'),
    'user-offline': ('user-offline', '', 'status'),
    'user-invisible': ('user-invisible', '', 'status'),
    'avatar-default': ('user', 'user-info preferences-desktop-personal contact-new address-book-new user-identity', 'status'),
    'weather-clear': ('sun', '', 'status'),
    'weather-few-clouds': ('weather-few-clouds', 'weather-clouds', 'status'),
    'weather-clear-night': ('weather-clear-night', '', 'status'),
    'weather-few-clouds-night': ('weather-few-clouds-night', 'weather-clouds-night', 'status'),
    'weather-overcast': ('weather-overcast', 'weather-many-clouds', 'status'),
    'weather-showers': ('weather-showers', 'weather-showers-day weather-showers-night', 'status'),
    'weather-showers-scattered': ('weather-showers-scattered', 'weather-showers-scattered-day weather-showers-scattered-night', 'status'),
    'weather-storm': ('weather-storm', 'weather-storm-day weather-storm-night', 'status'),
    'weather-snow': ('weather-snow', 'weather-snow-scattered weather-freezing-rain weather-hail', 'status'),
    'weather-fog': ('weather-fog', 'weather-mist', 'status'),
    'weather-windy': ('weather-windy', 'weather-tornado', 'status'),
    'task-past-due': ('warning', 'weather-severe-alert', 'status'),
    'view-sort-ascending': ('sort', '', 'actions'),
    'view-sort-descending': ('sort-descending', '', 'actions'),
    'view-sort': ('sort-plain', '', 'actions'),
    'object-rotate-right': ('rotate', '', 'actions'),
    'object-rotate-left': ('rotate-left', '', 'actions'),
    'zoom-fit-best': ('zoom-fit', '', 'actions'),
    'zoom-fit-width': ('zoom-fit-width', '', 'actions'),
    'zoom-fit-height': ('zoom-fit-height', '', 'actions'),
    'view-split-left-right': ('split', 'view-dual', 'actions'),
    'view-split-top-bottom': ('split-vertical', '', 'actions'),
    'mail-unread': ('mail', 'mail-message-new mail-mark-unread emblem-mail', 'status'),
    'mail-read': ('mail-read', 'mail-mark-read mail-message mail-open', 'status'),
    'mail-forward': ('mail-forward', '', 'actions'),
    'mail-reply-sender': ('mail-reply', 'mail-replied', 'actions'),
    'mail-reply-all': ('mail-reply-all', '', 'actions'),
    'mail-mark-junk': ('mail-junk', '', 'actions'),
    'mail-mark-notjunk': ('mail-signed', 'mail-signed mail-signed-verified', 'actions'),
    'mail-mark-important': ('mail-important', '', 'actions'),
    'go-first': ('first', '', 'actions'),
    'go-last': ('last', '', 'actions'),
    'media-seek-backward': ('seek-backward', '', 'actions'),
    'media-seek-forward': ('seek-forward', '', 'actions'),
    'document-save': ('save', '', 'actions'),
    'document-save-as': ('save-as', '', 'actions'),
    'starred': ('star', 'rating', 'actions'),
    'semi-starred': ('star-half', 'rating-half', 'actions'),
    'non-starred': ('star-outline', 'rating-unrated', 'actions'),
    'user-trash': ('trash', 'edit-delete trash-empty', 'places'),
    'user-trash-full': ('trash-full', '', 'places'),
}

# Names that must never resolve to the same drawing (checked by the build).
FAMILIES = [
    ['battery-full', 'battery-good', 'battery-medium', 'battery-low', 'battery-caution', 'battery-empty', 'battery-missing',
     'battery-full-charging', 'battery-good-charging', 'battery-medium-charging', 'battery-low-charging', 'battery-empty-charging'],
    ['network-wireless-signal-excellent', 'network-wireless-signal-good', 'network-wireless-signal-ok',
     'network-wireless-signal-weak', 'network-wireless-signal-none', 'network-wireless-acquiring',
     'network-wireless-no-route', 'network-wireless-offline'],
    ['network-wired', 'network-wired-acquiring', 'network-wired-no-route', 'network-wired-disconnected'],
    ['audio-volume-high', 'audio-volume-medium', 'audio-volume-low', 'audio-volume-muted'],
    ['airplane-mode', 'airplane-mode-disabled'], ['night-light', 'night-light-disabled'],
    ['bluetooth-active', 'bluetooth-disabled'], ['notification-active', 'notifications-disabled'],
    ['user-available', 'user-away', 'user-busy', 'user-offline', 'user-invisible'],
    ['weather-clear', 'weather-few-clouds', 'weather-clear-night', 'weather-few-clouds-night', 'weather-overcast',
     'weather-showers', 'weather-showers-scattered', 'weather-storm', 'weather-snow', 'weather-fog', 'weather-severe-alert'],
    ['view-sort-ascending', 'view-sort-descending'], ['object-rotate-right', 'object-rotate-left'],
    ['zoom-fit-best', 'zoom-fit-width', 'zoom-fit-height'], ['view-split-left-right', 'view-split-top-bottom'],
    ['mail-unread', 'mail-read', 'mail-forward', 'mail-mark-junk', 'mail-mark-important', 'mail-reply-sender', 'mail-reply-all'],
    ['go-first', 'media-seek-backward'], ['go-last', 'media-seek-forward'],
    ['document-save', 'document-save-as'], ['starred', 'semi-starred', 'non-starred'],
    ['user-trash', 'user-trash-full'], ['microphone-sensitivity-high', 'microphone-sensitivity-muted'],
]
