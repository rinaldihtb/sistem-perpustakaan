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


def lihat_daftar_buku(koneksi):
    # Menampilkan daftar data buku beserta stoknya.
    try:
        query = "SELECT id as ID, judul as Judul, penulis as Penulis, kategori as Kategori, stok as 'Jumlah Stok' FROM buku"
        # pd.read_sql mengubah hasil SELECT menjadi DataFrame.
        df = pd.read_sql(query, koneksi)
        tampilkan_judul("DAFTAR BUKU")
        # Tampilkan data buku
        if df.empty:
            print("Belum ada data buku.")
        else:
            tampilkan_tabel(df)
        return df
    except Exception as e:
        print(f"Terjadi error: {e}")
        return None


def tambah_buku(koneksi):
    # Form tambah buku baru ke tabel buku.
    tampilkan_judul("TAMBAH BUKU")
    print("Masukkan 0 pada input apa pun untuk membatalkan form.\n")

    judul = input_teks("Judul buku")
    if judul is None:
        print("Form dibatalkan.")
        return

    penulis = input_teks("Penulis")
    if penulis is None:
        print("Form dibatalkan.")
        return

    kategori = input_teks("Kategori")
    if kategori is None:
        print("Form dibatalkan.")
        return

    # Input stok dalam format angka
    stok = input_angka("Stok")

    if stok is None:
        print("Form dibatalkan.")
        return
    # Validasi stok
    if stok is False:
        return
    if stok < 0:
        print("Stok tidak boleh negatif.")
        return

    try:
        # Query insert memakai parameter agar input form masuk ke kolom yang tepat.
        query = text(
            """
            INSERT INTO buku (judul, penulis, kategori, stok)
            VALUES (:judul, :penulis, :kategori, :stok)
            """
        )
        # begin otomatis commit jika insert berhasil.
        with koneksi.begin() as conn:
            result = conn.execute(
                query,
                {
                    "judul": judul,
                    "penulis": penulis,
                    "kategori": kategori,
                    "stok": stok,
                },
            )
        print(f"Buku berhasil ditambahkan dengan ID {result.lastrowid}.")
    except Exception as e:
        print(f"Terjadi error: {e}")


def ubah_buku(koneksi):
    # Form update data buku; input kosong berarti data lama tidak berubah.
    tampilkan_judul("UBAH BUKU")
    print("Masukkan 0 pada input apa pun untuk membatalkan form.\n")

    buku_id = input_angka("Masukkan ID buku yang ingin diubah")
    if buku_id is None:
        print("Form dibatalkan.")
        return
    if buku_id is False:
        return

    try:
        with koneksi.connect() as conn:
        # Eksekusi query, dan simpan baris pertama ke variabel data
            data = conn.execute(
                text("SELECT * FROM buku WHERE id = :id"), {"id": buku_id}
            ).mappings().first()

        # Jika data yang dicari kosong, maka return tidak ditemukan
        if not data:
            print("Buku tidak ditemukan.")
            return

        print("\nData saat ini:")
        print(f"  ID       : {data['id']}")
        print(f"  Judul    : {data['judul']}")
        print(f"  Penulis  : {data['penulis']}")
        print(f"  Kategori : {data['kategori']}")
        print(f"  Stok     : {data['stok']}")
        print("\nKosongkan input jika tidak ingin mengubah nilai.\n")

        judul = input("Judul baru [0 untuk batal, Enter jika tidak diubah]: ")
        if judul == "0":
            print("Form dibatalkan.")
            return
        penulis = input("Penulis baru [0 untuk batal, Enter jika tidak diubah]: ")
        if penulis == "0":
            print("Form dibatalkan.")
            return
        kategori = input("Kategori baru [0 untuk batal, Enter jika tidak diubah]: ")
        if kategori == "0":
            print("Form dibatalkan.")
            return
        stok = input("Stok baru [0 untuk batal, Enter jika tidak diubah]: ")
        if stok == "0":
            print("Form dibatalkan.")
            return

        # Jika input kosong, gunakan data lama
        judul = judul if judul else data["judul"]
        penulis = penulis if penulis else data["penulis"]
        kategori = kategori if kategori else data["kategori"]
        stok = int(stok) if stok else data["stok"]

        if stok < 0:
            print("Stok tidak boleh negatif.")
            return

        # Query update menyimpan perubahan buku berdasarkan id.
        query = text(
            """
            UPDATE buku
            SET judul = :judul,
                penulis = :penulis,
                kategori = :kategori,
                stok = :stok
            WHERE id = :id
            """
        )
        with koneksi.begin() as conn:
        # Eksekusi Query untuk update buku.
            conn.execute(
                query,
                {
                    "id": buku_id,
                    "judul": judul,
                    "penulis": penulis,
                    "kategori": kategori,
                    "stok": stok,
                },
            )
        print("Data buku berhasil diubah.")
    except ValueError:
        print("Stok harus berupa angka.")
    except Exception as e:
        print(f"Terjadi error: {e}")


def menu_manajemen_buku(koneksi):
    # Navigasi CRUD buku untuk pustakawan.
    while True:
        bersihkan_layar()
        tampilkan_judul("MANAJEMEN BUKU")
        tampilkan_menu(
            [
                ("1", "Lihat Daftar Buku"),
                ("2", "Tambah Buku"),
                ("3", "Ubah Buku"),
                ("4", "Kembali"),
            ]
        )

        pilihan = input_menu("1-4")

        if pilihan == "1":
            lihat_daftar_buku(koneksi)
            tekan_enter()
        elif pilihan == "2":
            tambah_buku(koneksi)
            tekan_enter()
        elif pilihan == "3":
            ubah_buku(koneksi)
            tekan_enter()
        elif pilihan == "4":
            break
        else:
            print("Pilihan tidak valid.")
            tekan_enter()
