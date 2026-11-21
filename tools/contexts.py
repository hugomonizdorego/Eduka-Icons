"""Freedesktop context of an icon name.

Icon choosers filter by context (Applications, Actions, Status, ...), so every
name is filed where the Icon Naming Specification or the upstream theme puts
it, independent of the artwork it uses.
"""
import functools

import flat
import reference_names

# Icon Naming Specification 0.8.90: first and last name of every context block
# inside reference_names.FREEDESKTOP (which lists the names in specification order).
SPEC_BLOCKS = (('actions', 'address-book-new', 'zoom-out'), ('animations', 'process-working', 'process-working'),
               ('apps', 'accessories-calculator', 'utilities-terminal'),
               ('categories', 'applications-accessories', 'system-help'), ('devices', 'audio-card', 'video-display'),
               ('emblems', 'emblem-default', 'emblem-unreadable'), ('emotes', 'face-angel', 'face-worried'),
               ('mimetypes', 'application-x-executable', 'x-office-spreadsheet'), ('places', 'folder', 'user-trash'),
               ('status', 'appointment-missed', 'weather-storm'))
# Upstream only relocates into these contexts (its actions/status sets also hold app-like names).
UPSTREAM_ORDER = ('emblems', 'emotes', 'animations', 'devices', 'mimetypes')


@functools.lru_cache(maxsize=1)
def spec():
    names = reference_names.FREEDESKTOP
    table = {}
    for context, first, last in SPEC_BLOCKS:
        start = names.index(first)
        end = len(names) - 1 - names[::-1].index(last)
        for name in names[start:end + 1]:
            table.setdefault(name, context)
    return table


@functools.lru_cache(maxsize=1)
def upstream():
    table = {}
    tree = flat.tree()
    for directory, names in tree.items():
        if directory in flat.LAYOUT:
            context = flat.LAYOUT[directory][1]
            for name in names:
                table.setdefault(name, set()).add(context)
    import catalog
    for context, names in catalog.upstream_types().items():
        for name in names:
            table.setdefault(name, set()).add(context)
    return table


def context_of(name, default):
    """Context directory for ``name``; ``default`` is the context of its artwork entry."""
    if name in spec():
        return spec()[name]
    found = upstream().get(name)
    if not found or default in found or default in ('apps', 'categories', 'places'):
        return default
    for context in UPSTREAM_ORDER:
        if context in found:
            return context
    return default
