# Installing Eduka-Icons

## 1. Debian packages (recommended)

Eduka-Icons comes as three packages; install them together:

```sh
sudo apt install ./eduka-icons_1.0.0_all.deb ./eduka-icons-apps_1.0.0_all.deb \
                 ./eduka-icons-apps-comfort_1.0.0_all.deb
```

| Package | Content |
| --- | --- |
| `eduka-icons` | the four themes, `eduka-icons-select`, `eduka-icons-clayify` |
| `eduka-icons-apps` | clay icons for thousands of applications (required) |
| `eduka-icons-apps-comfort` | the same in the eye-comfort edition (recommended) |

The `eduka-icons` package installs:

| Path | Content |
| --- | --- |
| `/usr/share/icons/Eduka-Icons-Light` | default theme |
| `/usr/share/icons/Eduka-Icons-Dark` | for dark desktop themes |
| `/usr/share/icons/Eduka-Icons-Bright` | vivid colours |
| `/usr/share/icons/Eduka-Icons-Comfort` | eye comfort and low vision |
| `/usr/bin/eduka-icons-clayify` | clay icons for applications installed later |
| `/etc/apt/apt.conf.d/80eduka-icons-clayify` | runs `eduka-icons-clayify` after every apt/dpkg run |
| `eduka-icons-clayify.path` (systemd) | runs it when Flatpak or Snap applications change |
| `/usr/bin/eduka-icons-select` | theme selector |
| `/etc/xdg/autostart/eduka-icons-follow.desktop` | follows the Eduka-Desktop theme in LXQt/Eduka sessions |

On the **first** installation the post-install script makes Eduka-Icons-Light
the default for new accounts and the live session. Environment variables:

| Variable | Effect |
| --- | --- |
| `EDUKA_ICONS_DEFAULT=Dark`, `Bright` or `Comfort` | use that variant as the default |
| `EDUKA_ICONS_NO_DEFAULT=1` | install the themes without changing defaults |

Upgrades keep whatever default is in place. Removing the package
(`sudo apt remove eduka-icons`) removes the defaults it wrote again.

## 2. Cubic (building the Edukasaun OS ISO)

1. In Cubic, open the **Terminal** step (chroot).
2. Drag the three `.deb` files (`eduka-icons`, `eduka-icons-apps`,
   `eduka-icons-apps-comfort`) into the terminal window (or use Cubic's copy
   button). They land in the current folder.
3. Install it with apt so the dependencies come from the Debian archive:

   ```sh
   apt update
   apt install -y ./eduka-icons_1.0.0_all.deb ./eduka-icons-apps_1.0.0_all.deb \
                  ./eduka-icons-apps-comfort_1.0.0_all.deb
   ```

   For another default variant:

   ```sh
   EDUKA_ICONS_DEFAULT=Bright apt install -y ./eduka-icons*_1.0.0_all.deb
   ```

4. Check and clean up:

   ```sh
   dpkg -s eduka-icons | grep -E 'Status|Version'
   grep icon_theme /etc/xdg/lxqt/lxqt.conf     # icon_theme=Eduka-Icons-Light
   rm ./eduka-icons*_1.0.0_all.deb
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
eduka-icons-select --apply Light    # or Dark, Bright, Comfort
```

This updates, for the current account only: LXQt/Eduka-Desktop, GTK 2/3/4,
GNOME/Budgie (gsettings), Cinnamon, MATE, Xfce (xfconf), KDE (`kdeglobals`),
LXDE, qt5ct/qt6ct and xsettingsd (i3, Openbox, Fluxbox, bspwm, sway users).
Eduka-Settings → Appearance → Icon theme also lists all four variants.

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
A system default other than Light (for example an ISO built with
`EDUKA_ICONS_DEFAULT=Dark`) is kept as well, and nothing is changed while the
Eduka-Desktop theme is unknown to this version.

## 4. Eye comfort and low vision

`Eduka-Icons-Comfort` is made for people with low vision, light sensitivity
or long screen sessions:

- a dark contour around every icon, so it stands out on any wallpaper or
  panel colour;
- warmer colours with less blue light and less glaring saturation;
- higher contrast inside the artwork;
- thicker, high-contrast symbolic glyphs.

Select it with `eduka-icons-select --apply Comfort` (or in Eduka-Settings →
Appearance). The Eduka-Desktop theme follower never switches away from it.

## 5. Applications installed later

`eduka-icons-clayify` finds every installed application (Debian packages,
Flatpak, Snap, `~/.local`) whose icon is not drawn by Eduka-Icons yet and
turns its own icon into clay. The results are an overlay of the catalog
themes: they are stored under the same theme names in another icon
directory, `/usr/local/share/icons/Eduka-Icons-Apps` and
`.../Eduka-Icons-Apps-Comfort` (or `~/.local/share/icons/...` with `--user`).
Nothing in the packaged themes is changed. It runs automatically after every
apt/dpkg operation and when Flatpak/Snap applications change.

```sh
sudo eduka-icons-clayify            # all users
eduka-icons-clayify --user          # applications installed in your account
sudo eduka-icons-clayify --rebuild  # regenerate everything
sudo eduka-icons-clayify --remove   # delete the generated icons
```

Applications that point to an icon file by absolute path cannot be themed by
any icon theme.

## 6. Folder colours

```sh
eduka-icons-select --list-folder-colours
eduka-icons-select --folder-colour olive            # this account
sudo eduka-icons-select --folder-colour blue --system   # all users (e.g. in Cubic)
eduka-icons-select --folder-colour default          # back to aqua
```

All standard folders (Documents, Downloads, Music ...) change together and
keep their badges. Single folders can use a named colour in any file manager
that lets you pick a folder icon: `folder-rose`, `folder-blue-documents` ...

## 7. Sizes and customising the build

The themes ship the freedesktop standard sizes 16, 22, 24, 32, 48, 64, 96,
128 and 256 px plus HiDPI (@2x) directories. Panels and menus may ask
for any size: sizes in between are scaled down from the next larger artwork.
Up to 24 px the tray, panel and toolbar names are flat one-colour glyphs;
from 32 px they are clay.

Everything else is set in `eduka-icons.toml` before `make build`:

| Section | What it controls |
| --- | --- |
| `[build]` | variants to build, icon sizes, HiDPI sizes, catalog sizes, sharpening |
| `[glyphs]` | `style = "mono"` (flat, default) or `"colour"`; stroke weight; colour per variant |
| `[folders]` | default folder colour and the selectable colours |
| `[bright]`, `[comfort]` | saturation, contrast, contour colour, blue reduction |

## 8. From source without a package

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
- **Tray, panel and symbolic icons** are flat filled outlines in the
  Eduka-Panel text colour of the matching theme (Light `#183c35`, Dark
  `#e0e0e0`). GTK and KDE recolour the `-symbolic` names themselves; Qt 5
  panels show the colour of the selected variant, so pick the variant that
  matches the panel (the theme follower does this in Eduka-Desktop).
- **Qt outside LXQt/KDE** (e.g. under Openbox or i3) follows qt5ct/qt6ct or
  the GTK platform theme; the selector updates qt5ct/qt6ct when installed.

### Suggestions for Eduka-Desktop

These need changes in the Eduka-Desktop repository; Eduka-Icons works
without them.

- Add `eduka-icons` to `Recommends:` of `edukasaun-desktop-menu`, before
  `papirus-icon-theme`, and try `Eduka-Icons-Light` (or the variant matching
  the current Eduka theme) first in `eduka_common._theme_candidates()`.
- Ask for the `-symbolic` name first in Eduka-Panel's tray and tint it with
  the panel text colour, so tray icons follow custom panel colours exactly.
- Set `Qt.AA_UseHighDpiPixmaps` so the @2x artwork is used on HiDPI screens.
- Call `eduka-icons-select --apply <variant>` from Eduka-Settings when the
  icon theme is changed there, so GTK and other desktops follow.
- Credit Eduka-Icons in `eduka-about`.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Old icons after switching | Log out and in; or `gtk-update-icon-cache -f /usr/share/icons/Eduka-Icons-Light` |
| A local copy hides the system theme | Remove `~/.local/share/icons/Eduka-Icons-*` and `~/.icons/Eduka-Icons-*` |
| GNOME/Cinnamon/MATE default not used | `sudo glib-compile-schemas /usr/share/glib-2.0/schemas`; existing users keep their own gsettings value |
| Tray icons too dark or too light on a custom panel | Select the other variant (`--apply Dark` for dark panels), or set `[glyphs.colour]` in `eduka-icons.toml` and rebuild |
| Undo the system defaults | `sudo eduka-icons-select --reset-system-defaults` |
