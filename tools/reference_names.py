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
