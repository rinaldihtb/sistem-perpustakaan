import pandas as pd
from sqlalchemy import text
from tools import (
    bersihkan_layar,
    input_angka,
    input_menu,
    input_teks,
    tampilkan_judul,
    tampilkan_menu,
    tampilkan_tabel,
    tekan_enter,
)


def lihat_daftar_mahasiswa(koneksi):
    # Mengambil semua data mahasiswa untuk ditampilkan ke pustakawan.
    try:
        query = "SELECT " \
        "id as ID, " \
        "nim as NIM, " \
        "nama as Nama, " \
        "jurusan as Jurusan, " \
        "tahun_masuk as 'Tahun Masuk', status_aktif as 'Status' " \
        "FROM mahasiswa"

        # pd.read_sql mengubah hasil query menjadi DataFrame agar mudah ditampilkan.
        df = pd.read_sql(query, koneksi)
        tampilkan_judul("DAFTAR MAHASISWA")
        if df.empty:
            print("Belum ada data mahasiswa.")
        else:
            tampilkan_tabel(df)
        return df
    except Exception as e:
        print(f"Terjadi error: {e}")
        return None


def login_mahasiswa(koneksi):
    bersihkan_layar()
    tampilkan_judul("LOGIN MAHASISWA")
    print("Gunakan NIM mahasiswa untuk masuk.")
    print("Masukkan 0 untuk kembali.\n")

    # Ambil NIM Mahasiswa
    nim = input_teks("Masukkan NIM mahasiswa")
    
    # Jika input 0, kembali ke navigasi sebelumnya
    if nim is None:
        return

    try:
        # text dipakai agar query dengan parameter :nim aman dari input langsung.
        query = text(
            """
            SELECT id, nim, nama, jurusan, tahun_masuk, status_aktif
            FROM mahasiswa
            WHERE nim = :nim
            """
        )
        with koneksi.connect() as conn:
            # Eksekusi query, dan simpan baris pertama ke variabel data
            data = conn.execute(query, {"nim": nim}).mappings().first()

        # Jika data yang dicari kosong, maka return tidak ditemukan
        if not data:
            print("Mahasiswa tidak ditemukan.")
            tekan_enter()
            return None

        # Jika status mahasiswa non aktif, maka mahasiswa tidak bisa akses
        if data["status_aktif"] != "aktif":
            print("Mahasiswa berstatus nonaktif, tidak dapat login.")
            tekan_enter()
            return None

        print(f"Selamat datang, {data['nama']}!")
        # konversi object rowMapping Sql Alchemy kedalam bentuk dictionary
        return dict(data)
    except Exception as e:
        # Print error jika terjadi kegagalan
        print(f"Terjadi error: {e}")
        tekan_enter()
        return None


def tambah_mahasiswa(koneksi):
    # Form tambah mahasiswa baru dengan validasi status aktif/nonaktif.
    tampilkan_judul("TAMBAH MAHASISWA")
    print("Masukkan 0 pada input apa pun untuk membatalkan form.\n")

    nim = input_teks("NIM mahasiswa")
    if nim is None:
        print("Form dibatalkan.")
        return

    nama = input_teks("Nama mahasiswa")
    if nama is None:
        print("Form dibatalkan.")
        return

    jurusan = input_teks("Jurusan")
    if jurusan is None:
        print("Form dibatalkan.")
        return

    tahun_masuk = input_angka("Tahun masuk")
    if tahun_masuk is None:
        print("Form dibatalkan.")
        return
    if tahun_masuk is False:
        return

    status_aktif = input_teks("Status aktif (aktif/nonaktif)")
    if status_aktif is None:
        print("Form dibatalkan.")
        return

    status_aktif = status_aktif.lower()
    if status_aktif not in ["aktif", "nonaktif"]:
        print("Status harus aktif atau nonaktif.")
        return

    try:
        # NIM dibuat unique di database, sehingga duplikasi ditangkap di except.
        # Query insert memakai parameter agar data form masuk sesuai nama kolom.
        query = text(
            """
            INSERT INTO mahasiswa (nim, nama, jurusan, tahun_masuk, status_aktif)
            VALUES (:nim, :nama, :jurusan, :tahun_masuk, :status_aktif)
            """
        )
        # begin menjalankan insert dalam transaksi dan otomatis commit jika sukses.
        with koneksi.begin() as conn:
            result = conn.execute(
                query,
                {
                    "nim": nim,
                    "nama": nama,
                    "jurusan": jurusan,
                    "tahun_masuk": tahun_masuk,
                    "status_aktif": status_aktif,
                },
            )
        print(f"Mahasiswa berhasil ditambahkan dengan ID {result.lastrowid}.")
    except Exception as e:
        if "Duplicate entry" in str(e):
            print("NIM sudah digunakan mahasiswa lain.")
        else:
            print(f"Terjadi error: {e}")


def ubah_mahasiswa(koneksi):
    # Form update data mahasiswa; input kosong berarti nilai lama dipertahankan.
    tampilkan_judul("UBAH MAHASISWA")
    print("Masukkan 0 pada input apa pun untuk membatalkan form.\n")

    mahasiswa_id = input_angka("Masukkan ID mahasiswa yang ingin diubah")
    if mahasiswa_id is None:
        print("Form dibatalkan.")
        return
    if mahasiswa_id is False:
        return

    try:
        # Data lama diambil dulu untuk ditampilkan dan menjadi fallback update.
        with koneksi.connect() as conn:
            data = conn.execute(
                text("SELECT * FROM mahasiswa WHERE id = :id"), {"id": mahasiswa_id}
            ).mappings().first()

        if not data:
            print("Mahasiswa tidak ditemukan.")
            return

        print("\nData saat ini:")
        print(f"  ID           : {data['id']}")
        print(f"  NIM          : {data['nim']}")
        print(f"  Nama         : {data['nama']}")
        print(f"  Jurusan      : {data['jurusan']}")
        print(f"  Tahun Masuk  : {data['tahun_masuk']}")
        print(f"  Status Aktif : {data['status_aktif']}")
        print("\nKosongkan input jika tidak ingin mengubah nilai.\n")

        nim = input("NIM baru [0 untuk batal, Enter jika tidak diubah]: ")
        if nim == "0":
            print("Form dibatalkan.")
            return
        nama = input("Nama baru [0 untuk batal, Enter jika tidak diubah]: ")
        if nama == "0":
            print("Form dibatalkan.")
            return
        jurusan = input("Jurusan baru [0 untuk batal, Enter jika tidak diubah]: ")
        if jurusan == "0":
            print("Form dibatalkan.")
            return
        tahun_masuk = input(
            "Tahun masuk baru [0 untuk batal, Enter jika tidak diubah]: "
        )
        if tahun_masuk == "0":
            print("Form dibatalkan.")
            return
        status_aktif = input(
            "Status baru (aktif/nonaktif) [0 untuk batal, Enter jika tidak diubah]: "
        )
        if status_aktif == "0":
            print("Form dibatalkan.")
            return

        # Jika input kosong, nilai lama dari database tetap dipakai.
        nim = nim if nim else data["nim"]
        nama = nama if nama else data["nama"]
        jurusan = jurusan if jurusan else data["jurusan"]
        tahun_masuk = int(tahun_masuk) if tahun_masuk else data["tahun_masuk"]
        status_aktif = status_aktif.lower() if status_aktif else data["status_aktif"]

        if status_aktif not in ["aktif", "nonaktif"]:
            print("Status harus aktif atau nonaktif.")
            return

        # Query update hanya mengubah mahasiswa berdasarkan id yang dipilih.
        query = text(
            """
            UPDATE mahasiswa
            SET nim = :nim,
                nama = :nama,
                jurusan = :jurusan,
                tahun_masuk = :tahun_masuk,
                status_aktif = :status_aktif
            WHERE id = :id
            """
        )
        # begin memastikan update tersimpan sebagai satu transaksi.
        with koneksi.begin() as conn:
            conn.execute(
                query,
                {
                    "id": mahasiswa_id,
                    "nim": nim,
                    "nama": nama,
                    "jurusan": jurusan,
                    "tahun_masuk": tahun_masuk,
                    "status_aktif": status_aktif,
                },
            )
        print("Data mahasiswa berhasil diubah.")
    except ValueError:
        print("Tahun masuk harus berupa angka.")
    except Exception as e:
        if "Duplicate entry" in str(e):
            print("NIM sudah digunakan mahasiswa lain.")
        else:
            print(f"Terjadi error: {e}")


def menu_manajemen_mahasiswa(koneksi):
    # Navigasi manajemen mahasiswa untuk pustakawan.
    while True:
        bersihkan_layar()
        tampilkan_judul("MANAJEMEN MAHASISWA")
        tampilkan_menu(
            [
                ("1", "Lihat Daftar Mahasiswa"),
                ("2", "Tambah Mahasiswa"),
                ("3", "Ubah Mahasiswa"),
                ("4", "Kembali"),
            ]
        )

        pilihan = input_menu("1-4")

        if pilihan == "1":
            lihat_daftar_mahasiswa(koneksi)
            tekan_enter()
        elif pilihan == "2":
            tambah_mahasiswa(koneksi)
            tekan_enter()
        elif pilihan == "3":
            ubah_mahasiswa(koneksi)
            tekan_enter()
        elif pilihan == "4":
            break
        else:
            print("Pilihan tidak valid.")
            tekan_enter()
