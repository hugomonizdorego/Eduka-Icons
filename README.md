# Eduka-Icons 0.3.0

Source mandiri untuk **Eduka-Icons-Light** dan **Eduka-Icons-Dark**, dibuat untuk
Edukasaun OS. Pengelola: Hugo Moniz do Rego / proyek Edukasaun OS.

Desain memakai clay 3D matte, bentuk membulat, krem, oranye, kuning, olive, dan
aqua. Folder tetap aqua dan Home tetap berupa rumah krem. Versi artwork tetap
0.3.0. Semua 17 master utama disimpan sebagai WebP lossless dengan piksel RGBA
yang identik terhadap master PNG 0.3.0.

## Isi source

- 79 ikon inti Eduka, alias aplikasi dan mimetype, serta 45 glyph panel/action
  yang digambar dengan kode SVG sendiri.
- 17 master artwork utama, kode untuk membangun komposisi lainnya, dan varian
  folder dengan emblem.
- Builder tema, installer, validator, generator preview, pembuat DEB, dan
  pembungkus source.
- Metadata HiDPI `Scale=2`, ukuran fisik 16–1024 px, dan fallback `hicolor`.

Tidak ada katalog, folder, SVG, generator, tautan, atau dependensi Papirus.
Katalog puluhan ribu logo aplikasi dari rilis gabungan sebelumnya sudah
dikeluarkan. Nama alias aplikasi memakai artwork fungsi Eduka; logo aplikasi
lain mengikuti ikon yang dipasang aplikasi tersebut melalui tema `hicolor`.

Artwork berwarna diekspor sebagai PNG transparan agar Qt dan GTK menggunakan
berkas yang sama. Panel/action memakai SVG sendiri. Raster clay memiliki
batas detail master 1024 px.

## Build offline pada Debian / Edukasaun OS

Pasang dependensi build:

```sh
sudo apt install python3 python3-pil librsvg2-2 libcairo2 make gtk-update-icon-cache dpkg
```

Di dalam folder source:

```sh
make build
make test
make preview
```

Hasil tema tersedia di `build/themes/Eduka-Icons-Light/` dan
`build/themes/Eduka-Icons-Dark/`. Preview dan laporan validasi ada di `build/`.
Build tidak mengunduh artwork dan tidak memanggil layanan generatif.

## Pasang tema

Sebagai pengguna desktop:

```sh
python3 tools/install.py --apply Light
# atau: python3 tools/install.py --apply Dark
```

Installer mencadangkan instalasi Eduka sebelumnya, memasang kedua tema ke
direktori ikon pengguna, memperbarui cache jika tersedia, dan mencadangkan
konfigurasi LXQt/GTK sebelum memilih tema. Keluar dan masuk sesi kembali.

Untuk paket sistem:

```sh
make deb
sudo apt install ./dist/eduka-icons_0.3.0_all.deb
eduka-icons-select --use-system-theme --apply Light
```

Untuk Cubic, jalankan selector dengan `--apply Light --system-defaults` sebagai
root setelah paket terpasang. Panduan rinci: [docs/INSTALL-ID.md](docs/INSTALL-ID.md).

## Unggah source ke GitHub

Ekstrak ZIP atau tar.gz, lalu unggah isi folder **Eduka-Icons** ke repository
baru bernama **Eduka-Icons**. Simpan file source sebagai file biasa agar kode
bisa dibaca dan workflow bisa berjalan. Daftar berkas source kurang dari 100
file dan setiap file berada di bawah batas 25 MiB untuk unggahan browser.
Aturan ukuran: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

Folder `build/`, `dist/`, paket DEB, cache, dan arsip tidak ikut commit karena
diabaikan oleh `.gitignore`. Jangan menyalin riwayat repository lama yang
memuat berkas besar ke repository baru ini.

Contoh terminal; ganti `USERNAME` dengan akun GitHub Anda dan buat repository
kosong terlebih dahulu:

```sh
git init -b main
git add .
git commit -m "Eduka-Icons 0.3.0 standalone source"
git remote add origin https://github.com/USERNAME/Eduka-Icons.git
git push -u origin main
```

`make source` membuat ZIP dan tar.gz kecil di `dist/` hanya dari source yang
diizinkan. GitHub Actions menjalankan build, validasi, preview dan pembuatan
DEB; hasilnya disediakan sebagai workflow artifacts. Gunakan GitHub Releases
untuk mendistribusikan paket biner.

## Lisensi dan artwork

GPL-3.0; lihat `LICENSE`. Bentuk vektor dan glyph panel berasal dari kode
Eduka. Master utama dibuat dengan bantuan generasi gambar dari arahan desain
pengguna; provenance dan checksum ada di `assets/generated.json` serta
`assets/PROMPTS.md`. Gambar referensi pengguna tidak didistribusikan di source.

Source telah disiapkan untuk GitHub; repository jarak jauh belum dibuat dari
lingkungan ini. Pengujian sesi LXQt nyata dan ISO lengkap tetap perlu dilakukan
di perangkat Edukasaun OS.
