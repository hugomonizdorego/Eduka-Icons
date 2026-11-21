#!/usr/bin/env python3
"""Unit tests of the installed tools (no themes or root needed): python3 tools/test_tools.py"""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import select_theme as st  # noqa: E402
import symbolic  # noqa: E402


class Ini(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / 'a.conf'

    def tearDown(self):
        self.dir.cleanup()

    def test_keeps_other_content_and_bytes(self):
        self.path.write_bytes(b'# note \xff\n[General]\nicon_theme=Old\nfoo=1\n\n[Other]\nicon_theme=keep\n')
        self.assertTrue(st.set_ini_value(self.path, 'General', 'icon_theme', 'New', backup=False))
        self.assertEqual(self.path.read_bytes(), b'# note \xff\n[General]\nicon_theme=New\nfoo=1\n\n[Other]\nicon_theme=keep\n')
        self.assertFalse(st.set_ini_value(self.path, 'General', 'icon_theme', 'New', backup=False))
        self.assertEqual(st.read_ini_value(self.path, 'Other', 'icon_theme'), 'keep')

    def test_adds_section_and_key(self):
        st.set_ini_value(self.path, 'Icons', 'Theme', 'A', backup=False)
        self.assertEqual(self.path.read_text(), '[Icons]\nTheme=A\n')
        self.path.write_text('[Icons]\nx=1\n[Z]\ny=2\n')
        st.set_ini_value(self.path, 'Icons', 'Theme', 'B', backup=False)
        self.assertEqual(st.read_ini_value(self.path, 'Icons', 'Theme'), 'B')
        self.assertEqual(st.read_ini_value(self.path, 'Z', 'y'), '2')

    def test_only_real_line_ends_split(self):
        self.path.write_text('[General]\nNote=x\x0cy\u2028z\n[Icons]\nTheme=breeze\n')
        st.set_ini_value(self.path, 'Icons', 'Theme', 'New', backup=False)
        self.assertEqual(self.path.read_text(), '[General]\nNote=x\x0cy\u2028z\n[Icons]\nTheme=New\n')

    def test_no_temporary_file_left(self):
        st.set_ini_value(self.path, 'A', 'b', 'c', backup=False)
        self.assertEqual([p.name for p in Path(self.dir.name).iterdir()], ['a.conf'])


class SystemDefaults(unittest.TestCase):
    def test_reset_restores_earlier_defaults(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            files = {'etc/xdg/lxqt/lxqt.conf': '[General]\nicon_theme=Papirus\nfoo=1\n',
                     'etc/skel/.gtkrc-2.0': 'gtk-theme-name="X"\ngtk-icon-theme-name="Adwaita"\n',
                     'etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml':
                         '<x>\n<property name="IconThemeName" type="string" value="elementary"/>\n</x>\n'}
            for relative, text in files.items():
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                (root / relative).write_text(text)
            st.apply_system('Dark', True, root)
            st.apply_system('Light', True, root)          # a second selection must not forget the originals
            self.assertEqual(st.read_ini_value(root / 'etc/xdg/lxqt/lxqt.conf', 'General', 'icon_theme'), 'Eduka-Icons-Light')
            self.assertEqual(st.read_ini_value(root / 'etc/xdg/kdeglobals', 'Icons', 'Theme'), 'Eduka-Icons-Light')
            self.assertFalse(list((root / 'etc/skel').glob('*backup*')))
            st.reset_system(True, root)
            left = {str(p.relative_to(root)): p.read_text() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(left, files)


    def test_reset_uses_backups_of_older_versions(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            # State left by 0.5.0: our value in place, the original next to it.
            files = {'etc/xdg/lxqt/lxqt.conf': '[General]\nicon_theme=Eduka-Icons-Light\n',
                     'etc/xdg/lxqt/lxqt.conf.eduka-icons-backup': '[General]\nicon_theme=Papirus\n',
                     'etc/skel/.gtkrc-2.0': 'gtk-icon-theme-name="Eduka-Icons-Light"\n',
                     'etc/skel/.gtkrc-2.0.eduka-icons-backup': 'gtk-icon-theme-name="Adwaita"\n',
                     'etc/xdg/kdeglobals': '[Icons]\nTheme=Eduka-Icons-Light\n',
                     'var/lib/eduka-icons/defaults-initialized': 'Light\n'}
            for relative, text in files.items():
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                (root / relative).write_text(text)
            st.migrate_system(True, root)                 # what the package does on upgrade
            self.assertFalse(list(root.rglob('*.eduka-icons-backup')))
            st.apply_system('Dark', True, root)
            st.reset_system(True, root)
            self.assertEqual(st.read_ini_value(root / 'etc/xdg/lxqt/lxqt.conf', 'General', 'icon_theme'), 'Papirus')
            self.assertEqual((root / 'etc/skel/.gtkrc-2.0').read_text(), 'gtk-icon-theme-name="Adwaita"\n')
            self.assertFalse((root / 'etc/xdg/kdeglobals').exists())     # created by Eduka-Icons


class Follow(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.home = Path(self.dir.name)
        self.saved = {k: os.environ.get(k) for k in ('HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS')}
        os.environ.update(HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / '.config'), XDG_DATA_HOME=str(self.home / '.local/share'))
        os.environ.pop('XDG_RUNTIME_DIR', None); os.environ.pop('DBUS_SESSION_BUS_ADDRESS', None)
        for variant in st.VARIANTS:
            theme = self.home / '.local/share/icons' / st.theme_name(variant)
            theme.mkdir(parents=True); (theme / 'index.theme').write_text('[Icon Theme]\n')
        self.settings = self.home / '.config/eduka-desktop/desktop/settings.json'
        self.settings.parent.mkdir(parents=True)
        self.geteuid, os.geteuid = os.geteuid, lambda: 1000

    def tearDown(self):
        os.geteuid = self.geteuid
        for key, value in self.saved.items():
            os.environ.pop(key, None) if value is None else os.environ.__setitem__(key, value)
        self.dir.cleanup()

    def desktop(self, style):
        self.settings.write_text(json.dumps({'theme_style': style}))

    def test_follows_then_respects_manual_choice(self):
        self.desktop('Edukasaun-Dark')
        self.assertEqual(st.follow_once(), 'applied')
        self.assertEqual(st.current_user_theme(), 'Eduka-Icons-Dark')
        self.assertEqual(st.follow_once(), 'unchanged')
        self.desktop('Eduka-MultiColor')
        self.assertEqual(st.follow_once(), 'applied')
        st.apply_user('Light', True)                       # by hand, e.g. in Eduka-Settings
        self.assertEqual(st.follow_once(), 'manual')
        self.assertEqual(st.follow_once(), 'disabled')
        self.assertEqual(st.current_user_theme(), 'Eduka-Icons-Light')

    def test_first_run_keeps_a_variant_picked_by_hand(self):
        st.set_ini_value(self.home / '.config/lxqt/lxqt.conf', 'General', 'icon_theme', 'Eduka-Icons-Dark')
        self.desktop('Eduka-Default-Theme')
        self.assertEqual(st.follow_once(), 'manual')
        self.assertEqual(st.current_user_theme(), 'Eduka-Icons-Dark')
        self.assertEqual(st.follow_once(), 'disabled')

    def test_unknown_or_half_written_desktop_theme_changes_nothing(self):
        self.desktop('Edukasaun-Dark')
        self.assertEqual(st.follow_once(), 'applied')
        for content in ('{"wallpaper": "/x.png", "theme_st', '', '{"theme_style": "Some-Custom-Dark"}', '{}', '[1]'):
            self.settings.write_text(content)
            self.assertEqual(st.follow_once(), 'unknown-desktop-theme', content)
            self.assertEqual(st.current_user_theme(), 'Eduka-Icons-Dark')

    def test_empty_xdg_variables_count_as_unset(self):
        os.environ['XDG_CONFIG_HOME'] = ''
        os.environ['XDG_DATA_HOME'] = 'relative/path'
        home, config, data = st.user_dirs()
        self.assertEqual((config, data), (self.home / '.config', self.home / '.local/share'))

    def test_comfort_and_foreign_themes_are_never_switched(self):
        self.desktop('Edukasaun-Dark')
        st.apply_user('Comfort', True)
        self.assertEqual(st.follow_once(), 'comfort')
        st.set_ini_value(self.home / '.config/lxqt/lxqt.conf', 'General', 'icon_theme', 'Papirus')
        self.assertEqual(st.follow_once(), 'other-theme')

    def test_broken_state_file(self):
        st.follow_state_path().parent.mkdir(parents=True)
        st.follow_state_path().write_text('[1, 2]')
        self.assertEqual(st.read_follow_state(), {'enabled': True, 'last_applied': ''})

    def test_one_unwritable_target_does_not_stop_the_rest(self):
        blocker = self.home / '.config/gtk-4.0'
        blocker.parent.mkdir(parents=True, exist_ok=True); blocker.write_text('a file where a directory is expected')
        st.apply_user('Dark', True)
        self.assertEqual(st.read_ini_value(self.home / '.config/kdeglobals', 'Icons', 'Theme'), 'Eduka-Icons-Dark')


class Glyphs(unittest.TestCase):
    def test_states_have_their_own_drawing(self):
        self.assertEqual(symbolic.check_families(), [])

    def test_every_kind_is_drawable(self):
        for kind in symbolic.BASE:
            self.assertTrue(symbolic.glyph_path(kind), kind)
        for name, (kind, _, _) in symbolic.SYMBOLS.items():
            self.assertIn(kind, symbolic.BASE, name)

    def test_hue_prefers_exact_names(self):
        self.assertEqual(symbolic.hue('bell-off'), 'rose')
        self.assertEqual(symbolic.hue('bell'), 'honey')


if __name__ == '__main__':
    unittest.main(verbosity=1)
