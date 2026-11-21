# Eduka-Icons

## 1.0.0

### Design

- **System-tray, panel and toolbar icons are normal flat icons again.** Wi-Fi,
  Bluetooth, volume, battery, notifications, brightness, power and every
  toolbar action are one-colour line glyphs in the Eduka-Panel text colour
  (no 3D clay below 32 px). Clay artwork starts at 32 px, where its detail
  can be seen. `style = "colour"` in `eduka-icons.toml` brings two-tone
  glyphs back.
- **Every Eduka artwork was redrawn with more detail**: about 150 clay
  compositions (Eduka-Desktop suite, folders and their 29 badges, devices,
  file types, settings, dialogs, media, office, network, system and learning
  subjects) with side faces, highlights and small story details, each
  reviewed at 16, 24, 32, 48 and 64 px on light and dark backgrounds.
- **Every state has its own drawing**: battery charging per level, battery
  caution, four Wi-Fi levels plus connecting/error/off, wired states, volume
  levels, airplane mode and night light on/off, presence, a full weather
  set, mail states, sort/rotate/zoom/split directions, full and empty trash,
  open and drag-accept folders. The build fails when two states of one
  family share a picture.
- New clay shader (specular highlight, two-layer shadow) and a rewritten clay
  conversion for application icons: correct light direction on rotated
  shapes, translucent details kept, no more random grain, crisp small sizes.

### Completeness

- **File types and devices**: 660+ file-type names and all device names are
  clay now (previously only applications were).
- **The complete flat set** for actions, status, panel, emblems, emotes,
  animations and symbolic names (about 14,000 names from Papirus, recoloured
  to the variant's glyph colour) backs the Eduka glyphs, so toolbars and
  trays of GTK, Qt, KDE and Xfce applications are complete.
- New folders (favourites, games, recent, backup, code, books, camera, mail,
  print, important, network, root, apps, cloud drives, phone) and learning
  subjects (atom, microscope, abacus, compass, blocks, paint box, trophy ...).
- **Eight folder colours**: `eduka-icons-select --folder-colour olive`
  (aqua, olive, orange, yellow, rose, blue, plum, grey; `--system` for all
  users). Named colours (`folder-blue`, `folder-rose-documents` ...) exist too.

### Sizes and configuration

- Standard freedesktop sizes 16, 22, 24, 32, 48, 64, 96, 128, 256 and 512
  with HiDPI (@2x) directories; in-between sizes (18, 20, 36, 40, 72 ...) are
  scaled down from the next larger artwork instead of scaled up.
- `eduka-icons.toml`: variants, sizes, HiDPI sizes, glyph style, weight and
  colours, folder colours, sharpening, Bright and Comfort tuning.

### Fixes

- Application icons were hidden behind the applications' own hicolor icons
  whenever the generated `Eduka-Icons-Local` theme existed (GTK and Qt). The
  generated icons are now an overlay of `Eduka-Icons-Apps` in
  `/usr/local/share/icons` (or `~/.local/share/icons`); the old themes are
  removed on upgrade.
- Names were filed in the wrong context (emblems, emotes, devices and file
  types in `apps`), which broke icon pickers that browse by context.
- Dark shapes of application icons were deleted, the light came from the
  wrong side on rotated shapes, and transparent shapes turned into solid
  blobs in the clay conversion.
- SVG icons with units, without `width`/`height` or with a non-square view
  box were rendered cropped.
- `eduka-icons-select --reset-system-defaults` now restores the defaults
  that were in place before (they are recorded in
  `/var/lib/eduka-icons/backup`); backup files no longer leak into new home
  directories through `/etc/skel`.
- Settings files are replaced atomically and keep bytes that are not valid
  UTF-8; one read-only file no longer stops the other desktops from being
  configured.
- The Eduka-Desktop theme follower no longer switches itself off on its
  first run, survives a broken state file, and explains why it does nothing.
- `eduka-icons-clayify` converts each icon in a time- and memory-limited
  child process, tries the next original when one is broken, rejects blank
  results, regenerates after an upgrade, cleans up icons of removed
  applications and stays silent while its dependencies are being upgraded.
- Package scripts: removing the package no longer resets defaults on
  `deconfigure`, the systemd path unit is started on running systems, and
  generated files are removed with the package.
- Unit tests for the installed tools (`tools/test_tools.py`); the source
  check covers every tracked file.

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
