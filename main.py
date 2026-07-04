from sqlalchemy import create_engine

import buku
import mahasiswa
import peminjaman

# silahkan lihat detail dari fungsi-fungsi berikut ini didalam file tools.py
from tools import bersihkan_layar, input_menu, tampilkan_judul, tampilkan_menu, tekan_enter


# Koneksi database dibuat sekali lalu dipakai bersama oleh semua menu.
def buat_koneksi():
    """Membuat koneksi ke database MySQL."""
    try:
        # create_engine menyiapkan object koneksi SQLAlchemy ke database perpustakaan.
        engine = create_engine("mysql+mysqlconnector://root:@localhost/perpustakaan")
        print("Engine database berhasil dibuat")
        return engine
    except Exception as e:
        print(f"Terjadi error koneksi: {e}")
        return None


def menu_mahasiswa(koneksi, data_mahasiswa):
    # Menu khusus mahasiswa setelah berhasil login menggunakan NIM.
    while True:
        bersihkan_layar()
        tampilkan_judul("MENU MAHASISWA")
        print(f"Login sebagai : {data_mahasiswa['nama']}")
        print(f"NIM           : {data_mahasiswa['nim']}\n")
        tampilkan_menu(
            [
                ("1", "Lihat Buku"),
                ("2", "Ajukan Peminjaman Buku"),
                ("3", "Lihat Request Peminjaman Aktif"),
                ("4", "Lihat Riwayat Peminjaman"),
                ("5", "Kembali"),
            ]
        )

        pilihan = input_menu("1-5")

        if pilihan == "1":
            # Lihat daftar buku
            buku.lihat_daftar_buku(koneksi)
            tekan_enter()
        elif pilihan == "2":
            # ID mahasiswa hasil login dipakai sebagai peminjam.
            peminjaman.ajukan_peminjaman(koneksi, data_mahasiswa["id"])
            tekan_enter()
        elif pilihan == "3":
            # Menampilkan draft dan peminjaman aktif milik mahasiswa login.
            peminjaman.lihat_request_aktif(koneksi, data_mahasiswa["id"])
            tekan_enter()
        elif pilihan == "4":
            # Riwayat diambil dari tabel peminjaman berdasarkan mahasiswa login.
            peminjaman.lihat_riwayat_mahasiswa(koneksi, data_mahasiswa["id"])
            tekan_enter()
        elif pilihan == "5":
            break
        else:
            print("Pilihan tidak valid.")
            tekan_enter()


def akses_mahasiswa(koneksi):
    # Login mengembalikan data mahasiswa, termasuk id untuk relasi peminjaman,
    # jika tidak ditemukan, mengembalikan tipe data None
    data_mahasiswa = mahasiswa.login_mahasiswa(koneksi)
    if data_mahasiswa:
        menu_mahasiswa(koneksi, data_mahasiswa)


def menu_pustakawan(koneksi):
    # Menu pustakawan
    while True:
        bersihkan_layar()
        tampilkan_judul("MENU PUSTAKAWAN")
        tampilkan_menu(
            [
                ("1", "Manajemen Mahasiswa"),
                ("2", "Manajemen Buku"),
                ("3", "Manajemen Peminjaman"),
                ("4", "Laporan"),
                ("5", "Kembali"),
            ]
        )

        pilihan = input_menu("1-5")

        if pilihan == "1":
            # Masuk ke submenu manajemen mahasiswa.
            mahasiswa.menu_manajemen_mahasiswa(koneksi)
        elif pilihan == "2":
            # Masuk ke submenu manajemen buku.
            buku.menu_manajemen_buku(koneksi)
        elif pilihan == "3":
            # Masuk ke submenu approval, pengembalian, dan history peminjaman.
            peminjaman.menu_manajemen_peminjaman(koneksi)
        elif pilihan == "4":
            # Masuk ke submenu statistik dan visualisasi.
            peminjaman.menu_laporan(koneksi)
        elif pilihan == "5":
            break
        else:
            print("Pilihan tidak valid.")
            tekan_enter()


def main():
    # Program utama: halaman selamat datang, navigasi menu, dan tutup koneksi saat selesai.
    
    # Hubungkan aplikasi ke database
    koneksi = buat_koneksi()
    # Jika tidak terhubung, maka aplikasi tidak akan dilanjutkan
    if not koneksi:
        print("Engine database gagal dibuat !")
        return
    
    try: 
        with koneksi.connect() as  periksa_koneksi:
            print("Database berhasil terhubung!")
    except Exception as e:
        print("Database gagal terhubung!")
        return

    try:
        while True:
            bersihkan_layar()
            tampilkan_judul("APLIKASI PERPUSTAKAAN")
            print("Sistem peminjaman buku sederhana berbasis terminal.\n")
            tampilkan_menu(
                [
                    ("1", "Akses sebagai Mahasiswa"),
                    ("2", "Akses sebagai Pustakawan"),
                    ("3", "Keluar"),
                ]
            )

            pilihan = input_menu("1-3")

            if pilihan == "1":
                # Menuju navigasi role mahasiswa
                akses_mahasiswa(koneksi)
            elif pilihan == "2":
                # Menuju navigasi role Pustakawan
                menu_pustakawan(koneksi)
            elif pilihan == "3":
                # Keluar dari program
                print("Terima kasih, program dihentikan.")
                break
            else:
                # Input salah, mengulang proses ke awal
                print("Pilihan tidak valid.")
                tekan_enter()
    finally:
        # dispose menutup koneksi pool SQLAlchemy setelah program selesai.
        koneksi.dispose()
        print("Koneksi database ditutup")


if __name__ == "__main__":
    main()
