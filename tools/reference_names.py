"""Icon names Eduka-Icons is checked against (see tools/coverage.py)."""

# Every icon name requested by Eduka-Desktop 0.9.24 (Eduka-Menu, Eduka-Panel,
# Eduka-Settings, Eduka-About and its launchers). All of them must use Eduka art.
EDUKA_DESKTOP = '''
accessories-dictionary airplane-mode application-default-icon application-menu application-x-executable
applications-accessories applications-all applications-development applications-education
applications-graphics applications-internet applications-multimedia applications-office
applications-science applications-system applications-utilities appointment-soon audio-card
audio-speakers audio-volume-high audio-volume-low audio-volume-medium audio-volume-muted
audio-x-generic battery battery-good battery-good-charging blueman-adapters blueman-manager
blueman-sendto blueman-services bluetooth display-brightness display-brightness-symbolic document-open
document-preview document-send drive-harddisk drive-harddisk-solidstate drive-harddisk-usb
drive-removable-media drive-removable-media-usb edit-clear edit-clear-all edit-find emblem-default
emblem-favorite face-plain face-smile folder-open gcompris-qt go-down go-next go-previous go-up
google-chrome help-about image-x-generic input-keyboard input-mouse input-touchpad
internet-web-browser libreoffice-startcenter list-add list-remove media-eject media-flash
multimedia-player multimedia-volume-control network-disconnect network-wired network-wireless
network-wireless-signal-excellent network-wireless-signal-good network-wireless-signal-ok
network-wireless-signal-weak network-workgroup nm-connection-editor notifications-disabled
office-calendar pavucontrol-qt pcmanfm-qt power-saver preferences-desktop
preferences-desktop-accessibility preferences-desktop-display preferences-desktop-locale
preferences-desktop-peripherals preferences-desktop-sound preferences-desktop-theme
preferences-desktop-wallpaper preferences-system preferences-system-bluetooth
preferences-system-network preferences-system-notifications preferences-system-parental-controls
preferences-system-power-management preferences-system-time printer process-stop qterminal
start-here system-config-printer system-file-manager system-lock-screen system-log-out system-reboot
system-run system-search system-shutdown system-software-update system-users telegram-desktop
text-x-script transform-move transform-scale user-desktop user-home user-trash utilities-terminal
video-display view-app-grid view-fullscreen view-grid view-list-details view-list-icons view-preview
view-refresh view-split-left-right whatsapp-linux-app window-close window-new x-office-calendar
zoom-in zoom-out lxqt-about lxqt-config lxqt-config-input lxqt-config-locale lxqt-config-monitor
lxqt-config-notificationd lxqt-config-powermanagement lxqt-leave lxqt-notificationd lxqt-panel
eduka-update-system eduka-settings eduka-menu-settings eduka-about eduka-panel eduka-menu
edukasaun-desktop eduka-konekta eduka-block eduka-lafa edukasaun-welcome x-office-document starred
'''.split()

# freedesktop.org Icon Naming Specification 0.8.90 (international flags omitted).
FREEDESKTOP = '''
address-book-new application-exit appointment-new call-start call-stop contact-new document-new
document-open document-open-recent document-page-setup document-print document-print-preview
document-properties document-revert document-save document-save-as document-send edit-clear edit-copy
edit-cut edit-delete edit-find edit-find-replace edit-paste edit-redo edit-select-all edit-undo
folder-new format-indent-less format-indent-more format-justify-center format-justify-fill
format-justify-left format-justify-right format-text-direction-ltr format-text-direction-rtl
format-text-bold format-text-italic format-text-underline format-text-strikethrough go-bottom go-down
go-first go-home go-jump go-last go-next go-previous go-top go-up help-about help-contents help-faq
insert-image insert-link insert-object insert-text list-add list-remove mail-forward
mail-mark-important mail-mark-junk mail-mark-notjunk mail-mark-read mail-mark-unread mail-message-new
mail-reply-all mail-reply-sender mail-send mail-send-receive media-eject media-playback-pause
media-playback-start media-playback-stop media-record media-seek-backward media-seek-forward
media-skip-backward media-skip-forward object-flip-horizontal object-flip-vertical object-rotate-left
object-rotate-right process-stop system-lock-screen system-log-out system-run system-search
system-reboot system-shutdown tools-check-spelling view-fullscreen view-refresh view-restore
view-sort-ascending view-sort-descending window-close window-new zoom-fit-best zoom-in
zoom-original zoom-out process-working accessories-calculator accessories-character-map
accessories-dictionary accessories-text-editor help-browser multimedia-volume-control
preferences-desktop-accessibility preferences-desktop-font preferences-desktop-keyboard
preferences-desktop-locale preferences-desktop-multimedia preferences-desktop-screensaver
preferences-desktop-theme preferences-desktop-wallpaper system-file-manager system-software-install
system-software-update utilities-system-monitor utilities-terminal applications-accessories
applications-development applications-engineering applications-games applications-graphics
applications-internet applications-multimedia applications-office applications-other
applications-science applications-system applications-utilities preferences-desktop
preferences-desktop-peripherals preferences-desktop-personal preferences-other preferences-system
preferences-system-network system-help audio-card audio-input-microphone battery camera-photo
camera-video camera-web computer drive-harddisk drive-optical drive-removable-media input-gaming
input-keyboard input-mouse input-tablet media-flash media-floppy media-optical media-tape modem
multimedia-player network-wired network-wireless pda phone printer scanner video-display
emblem-default emblem-documents emblem-downloads emblem-favorite emblem-important emblem-mail
emblem-photos emblem-readonly emblem-shared emblem-symbolic-link emblem-synchronized emblem-system
emblem-unreadable face-angel face-angry face-cool face-crying face-devilish face-embarrassed face-kiss
face-laugh face-monkey face-plain face-raspberry face-sad face-sick face-smile face-smile-big
face-smirk face-surprise face-tired face-uncertain face-wink face-worried application-x-executable
audio-x-generic font-x-generic image-x-generic package-x-generic text-html text-x-generic
text-x-generic-template text-x-script video-x-generic x-office-address-book x-office-calendar
x-office-document x-office-presentation x-office-spreadsheet folder folder-remote network-server
network-workgroup start-here user-bookmarks user-desktop user-home user-trash appointment-missed
appointment-soon audio-volume-high audio-volume-low audio-volume-medium audio-volume-muted
battery-caution battery-low dialog-error dialog-information dialog-password dialog-question
dialog-warning folder-drag-accept folder-open folder-visiting image-loading image-missing
mail-attachment mail-unread mail-read mail-replied mail-signed mail-signed-verified
media-playlist-repeat media-playlist-shuffle network-error network-idle network-offline
network-receive network-transmit network-transmit-receive printer-error printer-printing
security-high security-medium security-low software-update-available software-update-urgent
sync-error sync-synchronizing task-due task-past-due user-available user-away user-idle user-offline
user-trash-full weather-clear weather-clear-night weather-few-clouds weather-few-clouds-night
weather-fog weather-overcast weather-severe-alert weather-showers weather-showers-scattered
weather-snow weather-storm
'''.split()

# Default applications of Debian desktops (LXQt, Xfce, GNOME, KDE, MATE, Cinnamon, LXDE).
DESKTOP_APPS = '''
pcmanfm-qt qterminal featherpad lximage-qt qps screengrab lxqt-archiver lxqt-config lxqt-leave
pavucontrol-qt nm-connection-editor blueman-manager firefox-esr thunderbird libreoffice-writer
libreoffice-calc libreoffice-impress vlc synaptic org.xfce.thunar xfce4-terminal mousepad ristretto
org.xfce.ristretto xfce4-taskmanager xfce4-screenshooter xfce4-settings-manager parole
org.gnome.Nautilus org.gnome.Terminal org.gnome.TextEditor org.gnome.Calculator org.gnome.Calendar
org.gnome.Software org.gnome.Settings org.gnome.SystemMonitor org.gnome.eog org.gnome.Evince
org.gnome.FileRoller org.gnome.Totem org.gnome.Rhythmbox org.gnome.Cheese org.gnome.Weather
org.gnome.clocks org.gnome.Maps org.gnome.Contacts org.gnome.Characters org.gnome.DiskUtility
org.gnome.baobab org.gnome.Screenshot org.gnome.Yelp org.gnome.tweaks org.kde.dolphin org.kde.konsole
org.kde.kate org.kde.okular org.kde.gwenview org.kde.ark org.kde.spectacle org.kde.discover
systemsettings org.kde.elisa org.kde.kcalc caja mate-terminal pluma atril eom engrampa mate-calc
nemo gnome-terminal xed xreader xviewer pcmanfm lxterminal galculator gpicview leafpad
gnome-disks gparted timeshift transmission-gtk qbittorrent gimp inkscape krita audacity obs kdenlive
shotwell evince okular calibre keepassxc gufw htop gcompris-qt kalzium marble stellarium geogebra
scratch tuxmath klavaro anki goldendict code geany thonny virtualbox remmina steam
'''.split()

# LXQt applications and configuration modules (Icon= names of the Debian packages).
LXQT = '''
utilities-terminal system-file-manager user-desktop system-users system-suspend-hibernate system-suspend
system-reboot system-log-out system-lock-screen system-shutdown screengrab qps preferences-system-time
preferences-system-session-services preferences-system-power-management preferences-system
preferences-desktop-theme preferences-desktop-peripherals preferences-desktop-notification
preferences-desktop-locale preferences-desktop-keyboard preferences-desktop-filetype-association
preferences-desktop-display obconf-qt lxqt-archiver lxqt-about lximage-qt featherpad brightnesssettings
pcmanfm-qt qterminal lxqt-config lxqt-runner lxqt-sudo pavucontrol-qt nm-connection-editor
'''.split()

# KDE applications (apps.kde.org), application IDs.
KDE = '''
org.kde.dolphin org.kde.konsole org.kde.kate org.kde.kwrite org.kde.okular org.kde.gwenview org.kde.ark
org.kde.spectacle org.kde.discover org.kde.elisa org.kde.kcalc org.kde.kdenlive org.kde.krita org.kde.kolourpaint
org.kde.digikam org.kde.kmail2 org.kde.kontact org.kde.korganizer org.kde.kaddressbook org.kde.akregator
org.kde.konversation org.kde.neochat org.kde.kdeconnect.app org.kde.ktorrent org.kde.kget org.kde.falkon
org.kde.konqueror org.kde.kalzium org.kde.kstars org.kde.marble org.kde.kgeography org.kde.kbruch
org.kde.kig org.kde.kmplot org.kde.kturtle org.kde.ktouch org.kde.kwordquiz org.kde.parley org.kde.khangman
org.kde.kanagram org.kde.klettres org.kde.blinken org.kde.cantor org.kde.labplot2 org.kde.step
org.kde.artikulate org.kde.minuet org.kde.gcompris org.kde.kiten org.kde.rocs org.kde.kalgebra
org.kde.kpat org.kde.kmines org.kde.ksudoku org.kde.kblocks org.kde.bovo org.kde.knights org.kde.kmahjongg
org.kde.ktuberling org.kde.palapeli org.kde.kbounce org.kde.kgoldrunner org.kde.knetwalk org.kde.kubrick
org.kde.katomic org.kde.kollision org.kde.ksnakeduel org.kde.picmi org.kde.granatier org.kde.kapman
org.kde.filelight org.kde.partitionmanager org.kde.kfind org.kde.kcharselect org.kde.kruler org.kde.kmag
org.kde.kmousetool org.kde.kmouth org.kde.kdenlive org.kde.kamoso org.kde.haruna org.kde.dragonplayer
org.kde.kaffeine org.kde.juk org.kde.k3b org.kde.skanlite org.kde.skanpage org.kde.kolf org.kde.kgpg
org.kde.kleopatra org.kde.kwalletmanager5 org.kde.kinfocenter org.kde.ksystemlog org.kde.plasma-systemmonitor
org.kde.kdevelop org.kde.umbrello org.kde.kompare org.kde.lokalize org.kde.okteta org.kde.kile
org.kde.calligrawords org.kde.calligrasheets org.kde.calligrastage org.kde.karbon org.kde.krdc org.kde.krfb
org.kde.kteatime org.kde.kweather org.kde.kclock org.kde.ktimer org.kde.kalarm org.kde.kmplayer
systemsettings kdenlive krita kalzium marble kstars gcompris-qt
'''.split()

# GNOME applications (apps.gnome.org), application IDs.
GNOME = '''
org.gnome.Nautilus org.gnome.Terminal org.gnome.Console org.gnome.TextEditor org.gnome.gedit
org.gnome.Calculator org.gnome.Calendar org.gnome.Contacts org.gnome.clocks org.gnome.Weather org.gnome.Maps
org.gnome.Music org.gnome.Totem org.gnome.Showtime org.gnome.Loupe org.gnome.eog org.gnome.Evince
org.gnome.Papers org.gnome.Snapshot org.gnome.Cheese org.gnome.SimpleScan org.gnome.DiskUtility
org.gnome.baobab org.gnome.SystemMonitor org.gnome.Logs org.gnome.Characters org.gnome.font-viewer
org.gnome.FileRoller org.gnome.Software org.gnome.Settings org.gnome.tweaks org.gnome.Extensions
org.gnome.Epiphany org.gnome.Geary org.gnome.Evolution org.gnome.Polari org.gnome.Fractal org.gnome.Boxes
org.gnome.Connections org.gnome.Todo org.gnome.Notes org.gnome.World.Secrets org.gnome.seahorse.Application
org.gnome.Rhythmbox3 org.gnome.Lollypop org.gnome.Podcasts org.gnome.Shotwell org.gnome.gitg
org.gnome.Builder org.gnome.Meld org.gnome.GHex org.gnome.Dictionary org.gnome.Yelp org.gnome.Tour
org.gnome.Chess org.gnome.Mines org.gnome.Sudoku org.gnome.Mahjongg org.gnome.TwentyFortyEight
org.gnome.Quadrapassel org.gnome.Robots org.gnome.Tetravex org.gnome.Reversi org.gnome.Nibbles
org.gnome.Aisleriot org.gnome.Fragments org.gnome.Shortwave org.gnome.Solanum org.gnome.design.Palette
org.gnome.Decibels org.gnome.Calls org.gnome.Photos org.gnome.Documents
'''.split()

# Popular applications on Linux (browsers, chat, media, office, education, games).
POPULAR = '''
google-chrome brave-browser firefox chromium microsoft-edge vivaldi opera librewolf tor-browser
google-earth google-earth-pro whatsapp whatsapp-desktop telegram telegram-desktop signal-desktop discord
element-desktop slack skype zoom teams-for-linux thunderbird gimp inkscape krita blender darktable
rawtherapee scribus audacity ardour lmms musescore vlc mpv obs kdenlive openshot shotcut handbrake
libreoffice-startcenter libreoffice-writer libreoffice-calc libreoffice-impress libreoffice-draw
libreoffice-math libreoffice-base onlyoffice-desktopeditors wps-office calibre foliate anki goldendict
geogebra stellarium celestia scratch-desktop gcompris tuxmath tuxpaint tuxtype klavaro kalzium marble
code codium geany thonny arduino android-studio steam lutris retroarch minetest supertuxkart 0ad
virtualbox gnome-boxes remmina anydesk teamviewer rustdesk transmission qbittorrent keepassxc bitwarden
gparted timeshift synaptic gdebi bleachbit stacer htop hardinfo cpu-x spotify duolingo kiwix-desktop
'''.split()
