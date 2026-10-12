# Build dan instalasi Eduka-Icons 0.3.0 standalone

Arsip GitHub berisi source, 17 master lossless, dan generator. Folder tema
hasil build dibuat pada `build/themes/`. Paket DEB dibuat terpisah di `dist/`.

## Mulai dari source

```sh
unzip Eduka-Icons-0.3.0-GitHub-source.zip
cd Eduka-Icons
sudo apt install python3 python3-pil librsvg2-2 libcairo2 make gtk-update-icon-cache dpkg
make build
make test
python3 tools/install.py --apply Light
```

Gunakan `--apply Dark` untuk tampilan gelap. Jalankan pemilihan tema sebagai
pengguna desktop tanpa sudo. Kedua tema dipasang di direktori ikon XDG
pengguna. Direktori Eduka sebelumnya dan pengaturan desktop dicadangkan.
Keluar dan masuk sesi untuk memuat ikon baru.

## Buat DEB

```sh
make deb
sudo apt install ./dist/eduka-icons_0.3.0_all.deb
eduka-icons-select --use-system-theme --apply Light
```

Versi tetap 0.3.0. Jika paket 0.3.0 lama sudah terpasang dan apt melewati
pemasangan paket baru, jalankan `sudo apt install --reinstall
./dist/eduka-icons_0.3.0_all.deb` dalam satu baris.

Selector versi standalone memeriksa metadata `X-Eduka-Edition=Standalone`
sebelum memilih paket sistem. Instalasi lokal Eduka yang menutupi tema sistem
dipindahkan ke cadangan di direktori data pengguna. Jangan memakai sudo untuk
`--use-system-theme`.

## Cubic

Setelah DEB disalin ke image, dalam terminal root Cubic:

```sh
apt install ./eduka-icons_0.3.0_all.deb
eduka-icons-select --apply Light --system-defaults
```

Default ditulis ke `/etc/xdg/lxqt/lxqt.conf` dan pengaturan GTK 3/4. Pastikan
paket serta konfigurasi tersebut masuk ke image yang diteruskan installer.
Uji image live dan hasil instalasi di mesin virtual sebelum distribusi.

## Ukuran dan HiDPI

File master source memakai WebP lossless. Build mendekodekannya ke PNG,
membuat komposisi tambahan, lalu mengekspor ukuran fisik 16 sampai 1024 px.
Direktori 2× tercatat pada `ScaledDirectories` dengan `Scale=2`; ukuran
logis 48 px pada skala 2× menggunakan PNG 96 px. Glyph panel memakai SVG.

## Ikon aplikasi

Alias seperti `pcmanfm-qt`, `qterminal`, `firefox`, `libreoffice-writer`, dan
nama aplikasi Eduka tersedia. Pakai `Icon=eduka-konekta` dalam launcher atau
`QIcon.fromTheme()` dalam Qt. Aplikasi dengan path ikon absolut perlu mengubah
lookup sendiri. Aplikasi yang tidak ada pada katalog memakai fallback hicolor.

## Source untuk GitHub

Ekstrak arsip dan unggah isi folder `Eduka-Icons`. Tidak perlu mengunggah hasil
`build/`, `dist/`, paket DEB atau arsip ke tree source. Buat repository kosong
baru agar riwayat berkas besar dari repository lama tidak terbawa.

```sh
make source
python3 tools/check_source.py
```

Arsip yang dihasilkan hanya memakai allowlist source. Preview, laporan,
cache, tema hasil build dan biner tetap di luar arsip source.
