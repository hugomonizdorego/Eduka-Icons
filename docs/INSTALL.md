# Installing Eduka-Icons

## 1. Debian package (recommended)

```sh
sudo apt install ./eduka-icons_0.4.0_all.deb
```

The package installs:

| Path | Content |
| --- | --- |
| `/usr/share/icons/Eduka-Icons-Light` | default theme |
| `/usr/share/icons/Eduka-Icons-Dark` | for dark desktop themes |
| `/usr/share/icons/Eduka-Icons-Bright` | vivid colours |
| `/usr/bin/eduka-icons-select` | theme selector |
| `/etc/xdg/autostart/eduka-icons-follow.desktop` | follows the Eduka-Desktop theme in LXQt/Eduka sessions |

On the **first** installation the post-install script makes Eduka-Icons-Light
the default for new accounts and the live session. Environment variables:

| Variable | Effect |
| --- | --- |
| `EDUKA_ICONS_DEFAULT=Dark` or `Bright` | use that variant as the default |
| `EDUKA_ICONS_NO_DEFAULT=1` | install the themes without changing defaults |

Upgrades keep whatever default is in place. Removing the package
(`sudo apt remove eduka-icons`) removes the defaults it wrote again.

## 2. Cubic (building the Edukasaun OS ISO)

1. In Cubic, open the **Terminal** step (chroot).
2. Drag `eduka-icons_0.4.0_all.deb` into the terminal window (or use Cubic's
   copy button). It lands in the current folder.
3. Install it with apt so the dependencies come from the Debian archive:

   ```sh
   apt update
   apt install -y ./eduka-icons_0.4.0_all.deb
   ```

   For another default variant:

   ```sh
   EDUKA_ICONS_DEFAULT=Bright apt install -y ./eduka-icons_0.4.0_all.deb
   ```

4. Check and clean up:

   ```sh
   dpkg -s eduka-icons | grep -E 'Status|Version'
   grep icon_theme /etc/xdg/lxqt/lxqt.conf     # icon_theme=Eduka-Icons-Light
   rm ./eduka-icons_0.4.0_all.deb
   ```

Installation order with `edukasaun-desktop-menu` does not matter. To change
the ISO default later inside the chroot:

```sh
eduka-icons-select --apply Dark --system-defaults
```

Nothing graphical is started in the chroot; the live user and every new
account start with the selected theme.

### What `--system-defaults` writes

| Desktop | File |
| --- | --- |
| LXQt and Eduka-Desktop | `/etc/xdg/lxqt/lxqt.conf` (`[General] icon_theme`) |
| GTK 3 / GTK 4 apps | `/etc/xdg/gtk-3.0/settings.ini`, `/etc/xdg/gtk-4.0/settings.ini` |
| GTK 2 apps | `/etc/skel/.gtkrc-2.0` |
| GNOME, Budgie, Cinnamon, MATE | `/usr/share/glib-2.0/schemas/90_eduka-icons.gschema.override` |
| KDE Plasma | `/etc/xdg/kdeglobals` (`[Icons] Theme`) |
| Xfce | `/etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml` (when present) |
| LXDE | `/etc/xdg/lxsession/LXDE/desktop.conf` (when present) |
| qt5ct / qt6ct | `/etc/xdg/qt5ct/qt5ct.conf`, `/etc/xdg/qt6ct/qt6ct.conf` (when installed) |

Existing files are edited line by line (comments and other keys stay), and a
copy of the original is kept once as `<file>.eduka-icons-backup`.

## 3. Choosing a theme as a user

```sh
eduka-icons-select --apply Light    # or Dark, Bright
```

This updates, for the current account only: LXQt/Eduka-Desktop, GTK 2/3/4,
GNOME/Budgie (gsettings), Cinnamon, MATE, Xfce (xfconf), KDE (`kdeglobals`),
LXDE, qt5ct/qt6ct and xsettingsd (i3, Openbox, Fluxbox, bspwm, sway users).
Eduka-Settings → Appearance → Icon theme also lists all three variants.

### Following the Eduka-Desktop theme

In Eduka-Desktop sessions the autostart entry runs
`eduka-icons-select --follow-desktop --watch`:

| Eduka-Desktop theme | Icons |
| --- | --- |
| Eduka-Default-Theme, Liquid Glass, Eduka-Low-Theme | Eduka-Icons-Light |
| Edukasaun-Dark, Eduka-Transparan | Eduka-Icons-Dark |
| Eduka-MultiColor | Eduka-Icons-Bright |

It only switches between Eduka-Icons variants. If a user picks an icon theme
by hand (Eduka-Settings, `--apply`, or a non-Eduka theme such as Papirus), the
follower stops. Turn it back on with `eduka-icons-select --follow-desktop`.

## 4. From source without a package

```sh
make build
make install                     # ~/.local/share/icons + select Light
sudo make install-system         # /usr/share/icons (then select as above)
```

## Compatibility notes

- **Eduka-Desktop** reads `~/.config/lxqt/lxqt.conf`, then
  `/etc/xdg/lxqt/lxqt.conf`; both are written by the selector. Every icon name
  Eduka-Desktop 0.9.24 asks for has Eduka artwork (`make test` fails otherwise).
- **Applications not drawn yet** fall back to Papirus (recommended by the
  package), Breeze, Adwaita and hicolor.
- **Symbolic icons** are filled outlines, so GTK's recolouring keeps the line
  art, and Qt/KDE show them in the variant's colour.
- **Qt outside LXQt/KDE** (e.g. under Openbox or i3) follows qt5ct/qt6ct or
  the GTK platform theme; the selector updates qt5ct/qt6ct when installed.

### Suggestions for Eduka-Desktop

- Add `eduka-icons` to `Recommends:` of `edukasaun-desktop-menu`, before
  `papirus-icon-theme`.
- In `eduka_common._theme_candidates()`, try `Eduka-Icons-Light` (or the
  variant matching the current Eduka theme) before `Papirus` as the default
  when no icon theme is configured.
- Credit Eduka-Icons in `eduka-about`.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Old icons after switching | Log out and in; or `gtk-update-icon-cache -f /usr/share/icons/Eduka-Icons-Light` |
| A local copy hides the system theme | Remove `~/.local/share/icons/Eduka-Icons-*` and `~/.icons/Eduka-Icons-*` |
| GNOME/Cinnamon/MATE default not used | `sudo glib-compile-schemas /usr/share/glib-2.0/schemas`; existing users keep their own gsettings value |
| Undo the system defaults | `sudo eduka-icons-select --reset-system-defaults` |
