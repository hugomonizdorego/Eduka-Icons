"""Original 24px line glyphs for the Eduka panel and desktop actions."""
from html import escape

def line(d):
    return f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'

def glyph(kind):
    if kind.startswith('wifi'):
        n = {'wifi-low': 1, 'wifi-medium': 2, 'wifi-high': 3, 'wifi-off': 0}.get(kind, 3)
        paths = ['M9 17Q12 14 15 17', 'M6 13Q12 7 18 13', 'M3 9Q12 0 21 9']
        art = '<circle cx="12" cy="20" r="1.4" fill="currentColor"/>' + ''.join(line(p) for p in paths[:n])
        return art + (line('M3 3L21 21') if kind == 'wifi-off' else '')
    if kind.startswith('volume'):
        art = line('M3 9H7L12 5V19L7 15H3Z')
        if kind == 'volume-mute': return art + line('M16 9L21 15M21 9L16 15')
        art += line('M16 9Q19 12 16 15')
        if kind == 'volume-high': art += line('M19 5Q26 12 19 19')
        return art
    if kind.startswith('battery'):
        percent = {'battery-empty': 0, 'battery-low': .2, 'battery-medium': .5, 'battery-charge': 0}.get(kind, 1)
        art = line('M3 6H19V18H3ZM21 10V14')
        if percent: art += f'<rect x="5" y="8" width="{12 * percent}" height="8" rx="1" fill="currentColor"/>'
        if kind == 'battery-charge': art += '<path d="M13 4L8 12H12L10 20L17 10H13Z" fill="currentColor"/>'
        return art
    shapes = {
        'bluetooth': 'M8 7L17 16L12 21V3L17 8L8 17',
        'wired': 'M7 3H17V11H7ZM12 11V16M3 20V16H21V20M8 3V7M12 3V7M16 3V7',
        'power': 'M12 2V11M6 5A9 9 0 1 0 18 5',
        'refresh': 'M20 8A9 9 0 0 0 4 7M4 7V2M4 7H9M4 16A9 9 0 0 0 20 17M20 17V22M20 17H15',
        'download': 'M12 3V16M7 11L12 16L17 11M4 17V21H20V17',
        'home': 'M3 11L12 3L21 11M6 9V21H10V14H14V21H18V9',
        'folder': 'M3 5H9L12 8H21V20H3Z',
        'trash': 'M4 6H20M9 6V3H15V6M6 6L7 21H17L18 6M10 10V17M14 10V17',
        'mail': 'M3 5H21V19H3ZM3 6L12 13L21 6',
        'lock': 'M7 10V7A5 5 0 0 1 17 7V10M5 10H19V21H5ZM12 14V17',
        'search': 'M16 16L22 22M18 10A8 8 0 1 0 2 10A8 8 0 1 0 18 10',
        'close': 'M5 5L19 19M19 5L5 19',
        'menu': 'M4 6H20M4 12H20M4 18H20',
        'check': 'M4 12L9 17L20 6',
        'warning': 'M12 2L23 21H1ZM12 8V14M12 18H12.1',
        'info': 'M12 11V17M12 7H12.1M22 12A10 10 0 1 0 2 12A10 10 0 1 0 22 12',
        'display': 'M2 3H22V17H2ZM12 17V22M7 22H17',
        'brightness': 'M12 2V4M12 20V22M2 12H4M20 12H22M5 5L6 6M18 18L19 19M5 19L6 18M18 6L19 5M17 12A5 5 0 1 0 7 12A5 5 0 1 0 17 12',
        'logout': 'M10 3H3V21H10M8 12H22M17 7L22 12L17 17',
        'play': 'M7 3L21 12L7 21Z',
        'pause': 'M6 4H9V20H6ZM15 4H18V20H15Z',
        'stop': 'M5 5H19V19H5Z',
        'next': 'M4 5L15 12L4 19ZM20 4V20',
        'previous': 'M20 5L9 12L20 19ZM4 4V20',
        'up': 'M5 15L12 8L19 15',
        'down': 'M5 9L12 16L19 9',
        'left': 'M15 5L8 12L15 19',
        'right': 'M9 5L16 12L9 19',
        'plus': 'M12 4V20M4 12H20',
        'minus': 'M4 12H20',
        'bell': 'M5 17H19L17 14V9A5 5 0 0 0 7 9V14ZM9 20Q12 24 15 20',
        'microphone': 'M9 3H15V14H9ZM5 11V13A7 7 0 0 0 19 13V11M12 20V23M8 23H16',
    }
    return line(shapes[kind])

SYMBOLS = {
 'network-wireless-signal-excellent': ('wifi-high', 'network-wireless-signal-good'),
 'network-wireless-signal-ok': ('wifi-medium', ''),
 'network-wireless-signal-weak': ('wifi-low', ''),
 'network-wireless-offline': ('wifi-off', 'network-wireless-disabled'),
 'network-wired': ('wired', 'network-wired-activated'),
 'bluetooth-active': ('bluetooth', 'bluetooth-disabled bluetooth-paired'),
 'audio-volume-high': ('volume-high', ''),
 'audio-volume-medium': ('volume-low', ''),
 'audio-volume-low': ('volume-low', ''),
 'audio-volume-muted': ('volume-mute', ''),
 'audio-input-microphone': ('microphone', 'microphone-sensitivity-high'),
 'battery-full': ('battery-full', 'battery-good'),
 'battery-medium': ('battery-medium', ''),
 'battery-low': ('battery-low', 'battery-caution'),
 'battery-empty': ('battery-empty', 'battery-missing'),
 'battery-full-charging': ('battery-charge', 'battery-good-charging battery-low-charging'),
 'system-shutdown': ('power', ''),
 'system-log-out': ('logout', ''),
 'view-refresh': ('refresh', 'software-update-available'),
 'folder-download': ('download', 'document-save'),
 'user-home': ('home', ''),
 'folder': ('folder', ''),
 'user-trash': ('trash', 'edit-delete'),
 'mail-unread': ('mail', 'mail-message-new'),
 'system-lock-screen': ('lock', ''),
 'system-search': ('search', 'edit-find'),
 'window-close': ('close', 'dialog-cancel'),
 'open-menu': ('menu', ''),
 'emblem-ok': ('check', 'dialog-ok'),
 'dialog-warning': ('warning', 'dialog-error'),
 'dialog-information': ('info', 'dialog-question'),
 'video-display': ('display', ''),
 'display-brightness': ('brightness', ''),
 'media-playback-start': ('play', ''),
 'media-playback-pause': ('pause', ''),
 'media-playback-stop': ('stop', ''),
 'media-skip-forward': ('next', ''),
 'media-skip-backward': ('previous', ''),
 'go-up': ('up', ''), 'go-down': ('down', ''),
 'go-previous': ('left', ''), 'go-next': ('right', ''),
 'list-add': ('plus', ''), 'list-remove': ('minus', ''),
 'notification-active': ('bell', ''),
}

def svg(kind, variant, title):
    color = '#3d463b' if variant == 'Light' else '#f3ecdf'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" color="{color}"><title>{escape(title)}</title>{glyph(kind)}</svg>\n'
