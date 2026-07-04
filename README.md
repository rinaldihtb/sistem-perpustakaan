# Capstone Sistem Peminjaman Buku Perpustakaan

## Ringkasan

Aplikasi ini dibuat untuk kebutuhan Capstone Project Module 1. Project ini menerapkan dasar pemrograman Python, integrasi database MySQL, operasi CRUD, statistik deskriptif, dan visualisasi data sederhana.

Aplikasi memiliki dua role utama:

- **Mahasiswa**: login menggunakan NIM, melihat daftar buku, mengajukan peminjaman, melihat request aktif, dan melihat riwayat peminjaman.
- **Pustakawan**: mengelola data mahasiswa, mengelola data buku, memproses pengajuan peminjaman, mencatat pengembalian buku, dan melihat laporan.

## Fitur Utama

- Login mahasiswa menggunakan NIM.
- Manajemen data mahasiswa.
- Manajemen data buku.
- Pengajuan peminjaman buku.
- Approval dan penolakan pengajuan oleh pustakawan.
- Pengembalian buku dengan update stok otomatis.
- Navigasi terminal dengan menu kembali dan keluar.
- Pembatalan form menggunakan input `0`.
- Statistik deskriptif menggunakan pandas.
- Visualisasi data menggunakan seaborn dan matplotlib.

## Ringkasan Database

Database memiliki empat tabel utama:

- `mahasiswa`
- `buku`
- `peminjaman`
- `peminjaman_detail`

Tabel dibuat sebagai raw table tanpa foreign key constraint. Relasi tetap digunakan secara logika di aplikasi melalui kolom id dan query join.

## Struktur File

```text
main.py            File utama aplikasi dan navigasi
mahasiswa.py       Fitur data mahasiswa dan login mahasiswa
buku.py            Fitur manajemen buku
peminjaman.py      Workflow peminjaman, laporan, dan visualisasi
tools.py           Helper tampilan terminal dan input
perpustakaan.sql   Struktur database dan data awal
```
