"""Pixel-reviewed glyph replacements and additional glyphs for 1.0.

GLYPHS:  kind -> list of items built with glyph_items.S / F / C / ring
SYMBOLS: icon name -> (kind, 'alias alias ...', context)

Rules of the family (checked at 16, 22 and 24 px with tools/glyph_preview.py):
24 x 24 grid, centre lines inside 2..22, 2 px round strokes on integer
coordinates, details at least 2 units apart, absolute path commands only.
"""
from glyph_items import S, F, C, ring, SLASH  # noqa: F401

# Parts shared by several glyphs (copies of the BASE drawings they extend).
_WIFI_DOT = C(12, 19.5, 1.6)
_WIFI_ARCS = ('M8.5 15.5Q12 12.5 15.5 15.5', 'M5.5 12Q12 6.5 18.5 12', 'M2.5 8.5Q12 0 21.5 8.5')
_MIC = [S('M12 3A3 3 0 0 1 15 6V11A3 3 0 0 1 9 11V6A3 3 0 0 1 12 3Z'),
        S('M5 11V12A7 7 0 0 0 19 12V11M12 19V22M8 22H16')]
_KEYBOARD = [S('M2 6H22V18H2Z'), S('M6 10H6.1M10 10H10.1M14 10H14.1M18 10H18.1M7 14H17')]
_PIN = S('M9 3H15L14 9L18 13H6L10 9ZM12 13V21')
_MAP_PIN = [S('M12 22Q5 15 5 9A7 7 0 0 1 19 9Q19 15 12 22Z'), ring(12, 9, 3)]
_RUNE = 'M7 7L17 16L12 21V3L17 8L7 17'
_DISPLAY = S('M2 3H22V17H2ZM12 17V21M7 21H17')
_TURN = S('M20 12A8 8 0 1 1 14.5 4.4M20 3V8H15')            # the "rotate" arrow
_STEAM = 'M7 2.5V6M13 2.5V6'
_MUG = [S('M4 10H16V16.5A4.5 4.5 0 0 1 11.5 21H8.5A4.5 4.5 0 0 1 4 16.5Z'), S('M16 12H18A2.5 2.5 0 0 1 18 17H16')]
_BOX = S('M11 5H4V20H19V13')                                # open box of export / import
_BARS = ((3, 16), (8, 12), (13, 8), (18, 4))                # signal bars: (left edge, top)


def _wifi(level):
    """Full arcs up to ``level``; the missing ones stay as hairlines so the fan keeps its shape."""
    return [_WIFI_DOT] + [S(d) if i < level else S(d, 0.9) for i, d in enumerate(_WIFI_ARCS)]


def _bars(level, count=4):
    """Mobile signal: ``level`` solid bars, the rest as outlines."""
    return [F(f'M{x} {top}H{x + 3}V20H{x}Z') if i < level else S(f'M{x + .5} {top + .5}H{x + 2.5}V19.5H{x + .5}Z', 1)
            for i, (x, top) in enumerate(_BARS[:count])]


GLYPHS = {
    # ---- Replacements of BASE drawings ------------------------------------------------------
    # The outlined plane left a 1-unit grey core at 16 px; a solid silhouette stays readable.
    'airplane': [S('M12 3.5V19.5', 3), F('M12 8L21.5 14.5V16.5L12 13.5L2.5 16.5V14.5Z'),
                 F('M12 16.5L16 20V21.5L12 20.5L8 21.5V20Z')],
    # A microphone capsule is round; the square one read as a lamp or a pedestal.
    'microphone': _MIC,
    'microphone-off': [*_MIC, SLASH],
    # 3-unit bars had a 1-unit core that turned into grey mush; 4-unit bars keep a clean 2-unit core.
    'pause': [S('M6 4H10V20H6ZM14 4H18V20H14Z')],
    # Six keys 3.5 units apart merged at 16 px: solid display, four keys 6 units apart.
    'calculator': [S('M5 2H19V22H5Z'), S('M8.5 6.5H15.5', 3), C(9, 13, 1.4), C(15, 13, 1.4), C(9, 18, 1.4), C(15, 18, 1.4)],
    # The knob reached x = 24 (clipped) and the piece sat 1.5 units right of centre.
    'puzzle': [S('M3 7H8Q8 3 10.5 3Q13 3 13 7H18V12Q21 12 21 14.5Q21 17 18 17V21H3Z')],
    # The triangle ran from 0.5 to 23.5 and touched the canvas edge at 16 px.
    'warning': [S('M12 3L21.5 20H2.5Z'), S('M12 9.5V14'), C(12, 17, 1.2)],
    # The "?" was a smudge inside the 7 px high battery at 16 px.
    'battery-missing': [S('M3 6H19V18H3ZM21 10V14'), S('M8.5 9.5L13.5 14.5M13.5 9.5L8.5 14.5')],
    # The pin ran from 0.5 to 23 and touched the top and bottom edge.
    'map-pin': _MAP_PIN,
    # The triangle sat 2 units right of centre (box 6..22); now 5..21, still optically centred.
    'play': [S('M6 3L20 12L6 21Z')],
    'run': [S('M6 3L20 12L6 21Z')],
    # The arrow touched y = 1 and the glyph sat above centre: moved 1 unit down.
    'reboot': [S('M19.5 14A7.5 7.5 0 1 1 16.8 7.2'), S('M18 3V8H13')],
    # The outer wave reached x = 23.5.
    'volume-high': [S('M3 9H7L12 5V19L7 15H3Z'), S('M16 9Q19 12 16 15'), S('M19 5.5Q25 12 19 18.5')],
    # These four sat 1 unit above or below the centre of the canvas.
    'gamepad': [S('M7 6H17Q22 6 22 12Q22 18 18 18Q16 18 15 15H9Q8 18 6 18Q2 18 2 12Q2 6 7 6Z'), S('M6 12H10M8 10V14'),
                C(16, 11, 1.2), C(18.5, 13, 1.2)],
    'tab-new': [S('M3 5H21V19H3ZM3 9H11V5M15 11.5V16.5M12.5 14H17.5')],
    'education': [S('M2 10L12 5L22 10L12 15Z'), S('M6 12V17Q12 21 18 17V12M22 10V16')],
    'performance': [S('M3.5 19A9.5 9.5 0 1 1 20.5 19'), S('M12 15L16.5 9.5'), C(12, 15, 1.6)],
    # Weak / no signal was a lone dot at the bottom of the canvas: keep the fan as hairlines.
    'wifi-medium': _wifi(2),
    'wifi-low': _wifi(1),
    'wifi-none': _wifi(0),

    # ---- Mobile network ---------------------------------------------------------------------
    'cellular-high': _bars(4),
    'cellular-good': _bars(3),
    'cellular-ok': _bars(2),
    'cellular-weak': _bars(1),
    'cellular-none': _bars(0),
    'cellular-off': [*_bars(0), SLASH],
    'cellular-connecting': [*_bars(0), C(4, 5, 1.4), C(8.5, 5, 1.4), C(13, 5, 1.4)],
    'cellular-error': [*_bars(3, 3), S('M20 4.5V13.5'), C(20, 18.5, 1.3)],
    'wifi-secure': [S(_WIFI_ARCS[1]), S(_WIFI_ARCS[2]), F('M8.5 16.5H15.5V22H8.5Z'),
                    S('M10 16.5V15A2 2 0 0 1 14 15V16.5', 1.6)],
    'bluetooth-connected': [S(_RUNE), C(3.5, 12, 1.4), C(20.5, 12, 1.4)],
    'bluetooth-searching': [S('M3 7L13 16L8 21V3L13 8L3 17'), S('M16.5 9Q19 12 16.5 15'), S('M19 6Q23 12 19 18')],

    # ---- Tray and panel states --------------------------------------------------------------
    'keyboard-layout': [S('M6 3H18Q21 3 21 6V18Q21 21 18 21H6Q3 21 3 18V6Q3 3 6 3Z'), S('M8 17L12 7L16 17M9.5 13.5H14.5')],
    'keyboard-off': [*_KEYBOARD, SLASH],
    'do-not-disturb': [ring(12, 12, 10), S('M7 12H17')],
    'cup-on': [*_MUG, S(_STEAM)],
    'cup-off': [*_MUG, S(_STEAM, 0.9)],
    'rotation-allowed': [_TURN, F('M9.5 8H14.5V16H9.5Z')],
    'rotation-locked': [_TURN, F('M9.5 8H14.5V16H9.5Z'), SLASH],
    'screenshot': [S('M3 9V3H9M15 3H21V9M21 15V21H15M9 21H3V15'), C(12, 12, 3)],
    'screen-shared': [_DISPLAY, S('M12 14V7M9 10L12 7L15 10')],
    'map-pin-off': [*_MAP_PIN, SLASH],
    'plug': [S('M9 2V7M15 2V7'), S('M6 7H18V11A6 6 0 0 1 6 11Z'), S('M12 17V22')],
    'bolt': [F('M13.5 2L5 13.5H10.5L9.5 22L19 10H13Z')],
    'update': [ring(12, 12, 10), S('M12 17V8M8 12L12 8L16 12')],
    'check-circle': [ring(12, 12, 10), S('M7.5 12.5L10.5 15.5L16.5 9')],
    'important': [ring(12, 12, 10), S('M12 7V13'), C(12, 16.7, 1.3)],
    'printer-alert': [S('M5 9V4H14V9M5 16H2V9H17V16H14M5 13H14V20H5Z'), S('M21 6V14'), C(21, 18.5, 1.3)],
    'timer': [ring(12, 13, 8), S('M10 2H14M12 2V5'), S('M12 9V13')],
    'dark-mode': [ring(12, 12, 9), F('M12 3A9 9 0 0 1 12 21Z')],

    # ---- Sensors and devices ----------------------------------------------------------------
    'cpu': [S('M6 6H18V18H6Z'), S('M9 3V6M15 3V6M9 18V21M15 18V21M3 9H6M3 15H6M18 9H21M18 15H21'), F('M10 10H14V14H10Z')],
    'memory': [S('M2 6H22V15H2Z'), S('M6 15V19M10 15V19M14 15V19M18 15V19'), F('M6 9H10V12H6Z'), F('M14 9H18V12H14Z')],
    'temperature': [S('M8 13.5V4.5A2 2 0 0 1 12 4.5V13.5A4 4 0 1 1 8 13.5Z'), S('M10 8.5V15'), C(10, 17, 2),
                    S('M16 5H19M16 9H19M16 13H18')],
    'usb-port': [S('M12 19V5.5'), F('M12 2L15 6.5H9Z'), C(12, 20.2, 2), S('M12 16.5L6 13V11.5', 1.6), C(6, 10, 1.9),
                 S('M12 13.5L18 10.5V9.5', 1.6), F('M16.2 5.8H19.8V9.4H16.2Z')],
    'sd-card': [S('M9 2H19V22H5V6Z'), S('M10 6V9M13 6V9M16 6V9', 1.6)],
    'webcam': [ring(12, 10, 8), C(12, 10, 3), S('M12 18V21M8 21H16')],
    'video-camera': [S('M2 6H15V18H2Z'), S('M15 10L22 6.5V17.5L15 14')],

    # ---- Toolbar actions --------------------------------------------------------------------
    'folder-new': [S('M3 5H9L12 8H21V20H3Z'), S('M12 11V17M9 14H15')],
    'calendar-new': [S('M3 5H21V21H3ZM3 10H21M8 2V7M16 2V7'), S('M12 13V19M9 16H15')],
    'export': [_BOX, S('M14 3H21V10M21 3L11 13')],
    'import': [_BOX, S('M21 3L12 12M12 6V12H18')],
    'share': [C(17.5, 5.5, 2.8), C(6.5, 12, 2.8), C(17.5, 18.5, 2.8), S('M8.9 10.6L15.1 6.9M8.9 13.4L15.1 17.1')],
    'clipboard': [S('M8 4H5V21H19V4H16M8 2H16V6H8Z'), S('M9 11H15M9 16H15')],
    'drag-handle': [C(x, y, 1.8) for y in (5, 12, 19) for x in (9, 15)],
    'playlist': [S('M3 6H21M3 12H12M3 18H12'), F('M15 11L22 15.5L15 20Z')],
    'repeat-one': [S('M17 2L21 6L17 10M3 12V10Q3 6 7 6H21M7 22L3 18L7 14M21 12V14Q21 18 17 18H3'),
                   S('M11 10.5L12.5 9.5V14.5', 1.6)],
    'pin-off': [_PIN, SLASH],
    'thumbs-up': [S('M3 11H7V21H3ZM7 11L11 3Q13.5 3 13.5 6V9H18.5Q21.5 9 21 12L20 19Q19.6 21 17.5 21H7')],
    'thumbs-down': [S('M3 3H7V13H3ZM7 13L11 21Q13.5 21 13.5 18V15H18.5Q21.5 15 21 12L20 5Q19.6 3 17.5 3H7')],
    'qr-code': [S('M3 3H10V10H3ZM14 3H21V10H14ZM3 14H10V21H3Z'), F('M13 13H17.5V17.5H13Z'), F('M17.5 17.5H22V22H17.5Z')],
    'table': [S('M3 4H21V20H3ZM3 10H21M3 15H21M10 4V20')],
    'presentation': [S('M2 4H22M4 4V15H20V4M12 15V18M8 21L12 18L16 21'), S('M8 11L11 8L13.5 10.5L16 8')],
}

# New names only: nothing here is a name or alias that symbolic.py or glyph_states.py already defines.
SYMBOLS = {
    # status: mobile network, Wi-Fi security, Bluetooth
    'network-cellular-signal-excellent': ('cellular-high', 'network-cellular-connected network-cellular network-mobile-100 gsm-3g-full', 'status'),
    'network-cellular-signal-good': ('cellular-good', 'network-mobile-80 network-mobile-60 gsm-3g-high', 'status'),
    'network-cellular-signal-ok': ('cellular-ok', 'network-mobile-40 gsm-3g-medium', 'status'),
    'network-cellular-signal-weak': ('cellular-weak', 'network-mobile-20 gsm-3g-low', 'status'),
    'network-cellular-signal-none': ('cellular-none', 'network-mobile-0 network-mobile-available gsm-3g-none', 'status'),
    'network-cellular-acquiring': ('cellular-connecting', 'network-mobile-acquiring', 'status'),
    'network-cellular-no-route': ('cellular-error', 'network-cellular-error network-cellular-limited gsm-3g-no-service', 'status'),
    'network-cellular-offline': ('cellular-off', 'network-cellular-disabled network-cellular-hardware-disabled '
                                 'network-cellular-disconnected network-mobile-off gsm-3g-disabled', 'status'),
    'network-wireless-encrypted': ('wifi-secure', 'network-wireless-secure network-wireless-locked', 'status'),
    'bluetooth-connected': ('bluetooth-connected', 'network-bluetooth-activated bluetooth-active-connected', 'status'),
    'bluetooth-acquiring': ('bluetooth-searching', 'bluetooth-searching bluetooth-discovering', 'status'),
    'network-bluetooth': ('bluetooth', '', 'status'),
    'network-bluetooth-inactive': ('bluetooth-off', 'bluetooth-hardware-disabled', 'status'),
    # status: panel indicators
    'keyboard-layout': ('keyboard-layout', 'indicator-keyboard input-keyboard-layout preferences-desktop-keyboard-layout '
                        'input-method ibus-keyboard fcitx-kbd', 'status'),
    'input-keyboard-virtual': ('keyboard', 'input-keyboard-virtual-on', 'status'),
    'input-keyboard-virtual-off': ('keyboard-off', '', 'status'),
    'do-not-disturb': ('do-not-disturb', 'dnd notifications-dnd notification-dnd notifications-paused', 'status'),
    'caffeine-cup-full': ('cup-on', 'caffeine-on idle-inhibit idle-inhibited system-suspend-inhibited inhibit-on', 'status'),
    'caffeine-cup-empty': ('cup-off', 'caffeine-off idle-uninhibited system-suspend-uninhibited inhibit-off', 'status'),
    'rotation-allowed': ('rotation-allowed', 'screen-rotation-allowed screen-rotate-auto-on orientation-auto', 'status'),
    'rotation-locked': ('rotation-locked', 'screen-rotation-locked screen-rotate-auto-off orientation-locked', 'status'),
    'screen-shared': ('screen-shared', 'screen-sharing', 'status'),
    'location-services-active': ('map-pin', 'location-services location-active gps', 'status'),
    'location-services-disabled': ('map-pin-off', 'location-inactive location-disabled gps-off', 'status'),
    'thunderbolt': ('bolt', 'thunderbolt-acquiring bolt', 'status'),
    'dark-mode': ('dark-mode', 'night-mode contrast', 'status'),
    'mic-on': ('microphone', 'mic-ready', 'status'),
    'mic-off': ('microphone-off', 'microphone-hardware-disabled', 'status'),
    'camera-hardware-disabled': ('camera-off', '', 'status'),
    'update-low': ('update', 'update-medium update-high mintupdate-updates-available', 'status'),
    'update-none': ('check-circle', 'mintupdate-up-to-date', 'status'),
    'printer-warning': ('printer-alert', 'printer-attention', 'status'),
    'clipboard': ('clipboard', 'edit-clipboard clipboard-manager', 'status'),
    'channel-insecure': ('unlock', '', 'status'),
    'content-loading': ('more', '', 'status'),
    'chat-message-new': ('chat', 'chat im-message-new', 'status'),
    'folder-drag-accept': ('folder-open', 'folder-visiting', 'status'),
    # actions
    'screenshot': ('screenshot', 'take-screenshot', 'actions'),
    'folder-new': ('folder-new', 'folder-add', 'actions'),
    'appointment-new': ('calendar-new', 'event-new', 'actions'),
    'document-export': ('export', 'export external-link', 'actions'),
    'document-import': ('import', 'import', 'actions'),
    'document-share': ('share', 'share emblem-share', 'actions'),
    'upload': ('upload', 'document-upload folder-upload', 'actions'),
    'insert-table': ('table', 'table', 'actions'),
    'insert-comment': ('chat', 'comment', 'actions'),
    'object-locked': ('lock', 'lock', 'actions'),
    'object-unlocked': ('unlock', 'unlock', 'actions'),
    'list-drag-handle': ('drag-handle', 'drag-handle grip', 'actions'),
    'media-playlist': ('playlist', 'playlist view-media-playlist', 'actions'),
    'media-playlist-repeat-song': ('repeat-one', 'media-playlist-repeat-one media-repeat-single media-repeat-track', 'actions'),
    'window-pin': ('pin', 'pin pinned view-pinned', 'actions'),
    'window-unpin': ('pin-off', 'unpin view-unpin', 'actions'),
    'thumbs-up': ('thumbs-up', 'like approve', 'actions'),
    'thumbs-down': ('thumbs-down', 'dislike disapprove', 'actions'),
    'qr-code': ('qr-code', 'qrcode view-barcode-qr', 'actions'),
    'translate': ('language', 'translation tools-translate config-language set-language', 'actions'),
    'timer': ('timer', 'stopwatch chronometer', 'actions'),
    # emblems
    'emblem-important': ('important', 'emblem-urgent important', 'emblems'),
    'emblem-readonly': ('lock', 'emblem-locked emblem-nowrite', 'emblems'),
    'emblem-unlocked': ('unlock', '', 'emblems'),
    'emblem-unreadable': ('error', 'emblem-error emblem-noread', 'emblems'),
    'emblem-synchronizing': ('refresh', 'emblem-sync emblem-syncing', 'emblems'),
    'emblem-success': ('check-circle', 'emblem-checked emblem-verified data-success dialog-positive', 'emblems'),
    # devices and sensors
    'cpu': ('cpu', 'processor cpu-usage device-cpu', 'devices'),
    'memory': ('memory', 'ram memory-usage device-mem', 'devices'),
    'temperature': ('temperature', 'sensors-temperature temperature-normal temperature-warm temperature-cold thermometer sensors', 'devices'),
    'usb': ('usb-port', 'device-usb device-notifier', 'devices'),
    'drive-removable-media-usb-pendrive': ('usb', 'usb-stick usb-drive', 'devices'),
    'media-flash-sd-mmc': ('sd-card', 'media-flash-sd sd-card media-flash-memory-stick media-flash-cf media-flash-smart-media', 'devices'),
    'webcam': ('webcam', 'camera-webcam video-webcam', 'devices'),
    'video-camera': ('video-camera', 'camera-recorder call-video video-call', 'devices'),
    'ac-adapter': ('plug', 'battery-ac-adapter gpm-ac-adapter power-plug', 'devices'),
    'multimedia-player': ('music', '', 'devices'),
    # places, file types, categories, applications (freedesktop names that had no glyph)
    'folder-publicshare': ('share', 'folder-public', 'places'),
    'folder-templates': ('document', '', 'places'),
    'folder-recent': ('history', '', 'places'),
    'folder-saved-search': ('search', '', 'places'),
    'x-office-spreadsheet': ('table', 'x-office-spreadsheet-template', 'mimetypes'),
    'x-office-presentation': ('presentation', 'x-office-presentation-template', 'mimetypes'),
    'x-office-address-book': ('book', '', 'mimetypes'),
    'text-html': ('code', 'text-xml', 'mimetypes'),
    'preferences-system-sharing': ('share', '', 'categories'),
    'preferences-desktop': ('gear', '', 'categories'),
    'preferences-desktop-screensaver': ('display', '', 'categories'),
    'applications-other': ('app-grid', '', 'categories'),
    'applets-screenshooter': ('screenshot', 'accessories-screenshot', 'apps'),
    'caffeine': ('cup-on', 'caffeine-indicator', 'apps'),
    'accessories-character-map': ('font', '', 'apps'),
}
