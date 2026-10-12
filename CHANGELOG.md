# Eduka-Icons

## 0.5.0

- **Every application has its own icon.** The Papirus application catalog
  (3,700+ artworks, 8,300+ names, GPL-3.0) is converted to Eduka clay at
  build time: GIMP, Inkscape and Krita, Chrome, Brave, Firefox, Google Earth,
  WhatsApp, Telegram, Discord, VLC, Steam, KDE (apps.kde.org), GNOME
  (apps.gnome.org), LXQt, education, games, office, audio and video apps no
  longer share generic artwork.
- Applications that would still share one picture (e.g. several apps whose
  upstream icon is the generic terminal or settings icon) get a unique clay
  copy with their own coloured monogram chip.
- **New Eduka-Icons-Comfort** for eye comfort and low vision: dark contour
  around every icon, warm low-blue colours, raised contrast, thicker
  high-contrast symbolic glyphs. Never switched automatically.
- **Colourful clay panel icons**: Wi-Fi, Bluetooth, volume, battery,
  brightness, notifications, power and toolbar actions are sculpted 3D clay
  in colour. Symbolic (`-symbolic`) icons are two-tone colour; GTK and KDE
  still recolour them for their headerbars.
- **`eduka-icons-clayify`**: applications installed later (apt, Flatpak,
  Snap) that ship only their own flat icon get a clay icon automatically
  (APT hook and a systemd path unit).
- LXQt configuration modules, Bluetooth managers, input-method tools and the
  education apps from Edukasaun OS 0.9.24 now each have distinct icons.
- New hidden shared themes Eduka-Icons-Apps / -Apps-Comfort (inherited by all
  variants) and Eduka-Icons-Local / -Local-Comfort (generated on the system).
- Packages: `eduka-icons` (themes and tools), `eduka-icons-apps` and
  `eduka-icons-apps-comfort` (application icons).
- Coverage report extended with LXQt, KDE, GNOME and popular application lists.

## 0.4.0

- New **Eduka-Icons-Bright** theme: livelier, more saturated clay colours for
  Eduka-MultiColor and other colourful themes, next to Light and Dark.
- Every icon name used by Eduka-Desktop 0.9.24 now has Eduka artwork; so does
  the whole freedesktop.org Icon Naming Specification.
- 21 new clay artworks (bell, help, error, check, key, star, globe, package,
  system monitor, microphone, font, download, users, puzzle, disc, picture,
  moon, notes, smartphone, desktop folder, …) and redrawn power, Bluetooth,
  Wi-Fi, volume, info, phone, message and person icons with solid clay bodies.
- Catalog grows from 79 to 113 entries and about 1,100 names, including the
  default applications of LXQt, Xfce, GNOME, KDE, MATE, Cinnamon and LXDE.
- 246 symbolic glyphs (was 45) for panels, toolbars and dialogs, converted to
  filled outlines so GTK 3/4 recolouring keeps the line art (stroked paths were
  filled into blobs before). Symbolic icons now live in `symbolic/<context>`.
- `eduka-icons-select` replaces `tools/install.py`: one command configures
  LXQt/Eduka-Desktop, GTK 2/3/4, GNOME, Budgie, Cinnamon, MATE, Xfce, KDE,
  LXDE, qt5ct/qt6ct and xsettingsd; `--system-defaults` sets ISO defaults;
  `--follow-desktop` matches the Eduka-Desktop theme.
- The .deb sets the default icon theme on first installation (Cubic ready),
  honours `EDUKA_ICONS_DEFAULT` / `EDUKA_ICONS_NO_DEFAULT`, and removes its
  defaults again on removal.
- Fallbacks: Papirus → Breeze → Adwaita → hicolor.
- Sizes 16–512 px with `@2x` HiDPI; 1024 px and rarely used sizes dropped to
  keep the package small.
- Tests: GTK symbolic recolour check, coverage report (`tools/coverage.py`),
  duplicate-name detection. Screenshots in `docs/screenshots/`.
- Documentation and scripts in English.

## 0.3.0 — standalone source

- Removed the upstream catalog, folders, artwork and generators from the source.
- Kept 79 core Eduka artworks and 17 lossless clay masters.
- Added 45 own panel/action SVG glyphs and application aliases.
- Offline Light/Dark build from Eduka sources with hicolor fallback.
