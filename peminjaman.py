import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import text
from tools import (
    bersihkan_layar,
    input_angka,
    input_menu,
    tampilkan_judul,
    tampilkan_menu,
    tampilkan_tabel,
    tekan_enter,
)


def tampilkan_buku_tersedia(koneksi):
    # Dipakai sebelum mahasiswa membuat pengajuan agar hanya stok tersedia yang terlihat.
    query = "" \
    "SELECT id as ID, " \
    "judul as Judul, " \
    "penulis as Penulis, kategori as Kategori, " \
    "stok as 'Jumlah Stok' FROM buku WHERE stok > 0"
    # DataFrame memudahkan data buku dicetak sebagai tabel terminal.
    df = pd.read_sql(query, koneksi)
    tampilkan_judul("BUKU TERSEDIA")
    if df.empty:
        print("Tidak ada buku dengan stok tersedia.")
    else:
        tampilkan_tabel(df)
    return df


def ambil_buku(koneksi, buku_id):
    # Mengambil satu buku untuk validasi stok saat form peminjaman berjalan.
    # Parameter :id membuat query tetap aman walaupun id berasal dari input user.
    query = text("SELECT id, judul, stok FROM buku WHERE id = :id")
    with koneksi.connect() as conn:
        # first mengambil satu baris buku; None jika id tidak ditemukan.
        return conn.execute(query, {"id": buku_id}).mappings().first()


def ajukan_peminjaman(koneksi, mahasiswa_id):
    # Mahasiswa membuat pengajuan; stok langsung dikurangi setelah pengajuan disimpan.
    tampilkan_judul("AJUKAN PEMINJAMAN BUKU")
    print("Masukkan 0 pada input apa pun untuk membatalkan form.")
    print("Maksimal total buku dalam 1 pengajuan adalah 3.")

    tampilkan_buku_tersedia(koneksi)

    durasi = input_angka("Durasi peminjaman (hari)")
    if durasi is None:
        print("Form dibatalkan.")
        return
    if durasi is False:
        return
    if durasi <= 0:
        print("Durasi harus lebih dari 0.")
        return

    daftar_buku = []
    total_jumlah = 0

    # Satu periode pengajuan maksimal berisi total 3 buku.
    while total_jumlah < 3:
        buku_id = input_angka("Masukkan ID buku yang ingin dipinjam")
        if buku_id is None:
            print("Form dibatalkan.")
            return
        if buku_id is False:
            return

        # cari buku berdasarkan id
        data_buku = ambil_buku(koneksi, buku_id)
        if not data_buku:
            print("Buku tidak ditemukan.")
            continue
        if data_buku["stok"] <= 0:
            print("Stok buku kosong.")
            continue

        sisa_limit = 3 - total_jumlah
        jumlah = input_angka(f"Jumlah pinjam, maksimal {sisa_limit}")
        if jumlah is None:
            print("Form dibatalkan.")
            return
        if jumlah is False:
            return
        if jumlah <= 0:
            print("Jumlah harus lebih dari 0.")
            continue
        if jumlah > sisa_limit:
            print("Jumlah melebihi batas maksimal 3 buku.")
            continue
        # Menghitung jumlah buku yang sama jika user memilih buku itu lebih dari sekali.
        jumlah_buku_sama = 0
        for item in daftar_buku:
            if item["buku_id"] == buku_id:
                jumlah_buku_sama = item["jumlah"]

        if jumlah + jumlah_buku_sama > data_buku["stok"]:
            print("Stok buku tidak mencukupi.")
            continue

        buku_sudah_dipilih = False
        for item in daftar_buku:
            if item["buku_id"] == buku_id:
                # Jika buku sudah ada di keranjang, jumlahnya digabung.
                item["jumlah"] += jumlah
                buku_sudah_dipilih = True
                break

        if not buku_sudah_dipilih:
            daftar_buku.append(
                {
                    "buku_id": buku_id,
                    "judul": data_buku["judul"],
                    "jumlah": jumlah,
                }
            )

        total_jumlah += jumlah
        print(f"Total buku dalam pengajuan: {total_jumlah}")

        if total_jumlah == 3:
            break

        lanjut = input("Tambah buku lain? (y/n) [0 untuk batal]: ").lower()
        if lanjut == "0":
            print("Form dibatalkan.")
            return
        if lanjut != "y":
            break

    if not daftar_buku:
        print("Tidak ada buku yang dipilih.")
        return

    print("\n" + "-" * 64)
    print("Ringkasan pengajuan")
    print("-" * 64)
    for item in daftar_buku:
        print(f"  - {item['judul']} sebanyak {item['jumlah']}")
    print("-" * 64)

    konfirmasi = input("Simpan pengajuan? (y/n) [0 untuk batal]: ").lower()
    if konfirmasi == "0" or konfirmasi != "y":
        print("Form dibatalkan.")
        return

    try:
        # Transaksi menjaga insert peminjaman, detail, dan update stok tetap satu proses.
        with koneksi.begin() as conn:
            result = conn.execute(
                text(
                    """
                    INSERT INTO peminjaman (mahasiswa_id, durasi, status, dikembalikan)
                    VALUES (:mahasiswa_id, :durasi, 'draft', NULL)
                    """
                ),
                {"mahasiswa_id": mahasiswa_id, "durasi": durasi},
            )
            # lastrowid dipakai untuk menghubungkan data ke peminjaman_detail.
            peminjaman_id = result.lastrowid

            for item in daftar_buku:
                # Detail menyimpan buku apa saja yang ada dalam satu pengajuan.
                conn.execute(
                    text(
                        """
                        INSERT INTO peminjaman_detail (peminjaman_id, buku_id, jumlah)
                        VALUES (:peminjaman_id, :buku_id, :jumlah)
                        """
                    ),
                    {
                        "peminjaman_id": peminjaman_id,
                        "buku_id": item["buku_id"],
                        "jumlah": item["jumlah"],
                    },
                )
                # Sesuai requirement, stok berkurang sejak pengajuan dibuat.
                conn.execute(
                    text(
                        """
                        UPDATE buku
                        SET stok = stok - :jumlah
                        WHERE id = :buku_id
                        """
                    ),
                    {"buku_id": item["buku_id"], "jumlah": item["jumlah"]},
                )

        print(f"Pengajuan peminjaman berhasil dibuat dengan ID {peminjaman_id}.")
    except Exception as e:
        print(f"Terjadi error: {e}")


def tampilkan_data_peminjaman(koneksi, query, params=None, judul="DATA PEMINJAMAN"):
    # Helper tampilan untuk query peminjaman yang bentuk outputnya mirip.
    try:
        # params dipakai untuk query yang membutuhkan filter seperti mahasiswa_id.
        df = pd.read_sql(text(query), koneksi, params=params)
        tampilkan_judul(judul)
        if df.empty:
            print("Tidak ada data.")
        else:
            tampilkan_tabel(df)
        return df
    except Exception as e:
        print(f"Terjadi error: {e}")
        return None


def lihat_request_aktif(koneksi, mahasiswa_id):
    # Request aktif adalah draft atau peminjaman disetujui yang belum dikembalikan.
    # GROUP_CONCAT menggabungkan beberapa buku detail menjadi satu kolom daftar_buku.
    query = """
        SELECT
            p.id as ID,
            p.durasi as 'Durasi (Hari)',
            p.status as 'Status',
            GROUP_CONCAT(CONCAT(b.judul, ' (x', pd.jumlah, ')') SEPARATOR ', ') AS 'Daftar Buku'
        FROM peminjaman p
        JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
        JOIN buku b ON pd.buku_id = b.id
        WHERE p.mahasiswa_id = :mahasiswa_id
          AND (p.status = 'draft' OR (p.status = 'disetujui' AND p.dikembalikan = FALSE))
        GROUP BY p.id, p.durasi, p.status, p.dikembalikan
        ORDER BY p.id DESC
    """
    return tampilkan_data_peminjaman(
        koneksi,
        query,
        {"mahasiswa_id": mahasiswa_id},
        "REQUEST PEMINJAMAN AKTIF",
    )


def lihat_riwayat_mahasiswa(koneksi, mahasiswa_id):
    # Riwayat mahasiswa diurutkan dari peminjaman terbaru berdasarkan id terbesar.
    # Join dipakai agar judul buku bisa tampil bersama data peminjaman.
    query = """
        SELECT
            p.id as ID,
            p.durasi as 'Durasi (Hari)',
            p.status as 'Status',
            CASE 
                WHEN p.dikembalikan IS NULL Then '-'
                WHEN p.status = 'disetujui' AND p.dikembalikan = 1 Then 'Sudah'
                ELSE 'Belum'
            END as 'Dikembalikan',
            GROUP_CONCAT(CONCAT(b.judul, ' (x', pd.jumlah, ')') SEPARATOR ', ') AS 'Daftar Buku'
        FROM peminjaman p
        JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
        JOIN buku b ON pd.buku_id = b.id
        WHERE p.mahasiswa_id = :mahasiswa_id
        GROUP BY p.id, p.durasi, p.status, p.dikembalikan
        ORDER BY p.id DESC
    """
    return tampilkan_data_peminjaman(
        koneksi,
        query,
        {"mahasiswa_id": mahasiswa_id},
        "RIWAYAT PEMINJAMAN",
    )


def lihat_pengajuan(koneksi):
    # Pustakawan melihat pengajuan yang masih menunggu keputusan.
    # Hanya status draft yang perlu diproses pustakawan.
    query = """
        SELECT
            p.id as ID,
            m.nama as 'Nama Mahasiswa',
            p.durasi as 'Durasi(Hari)',
            p.status as Status,
            GROUP_CONCAT(CONCAT(b.judul, ' (x', pd.jumlah, ')') SEPARATOR ', ') AS 'Daftar Buku'
        FROM peminjaman p
        JOIN mahasiswa m ON p.mahasiswa_id = m.id
        JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
        JOIN buku b ON pd.buku_id = b.id
        WHERE p.status = 'draft'
        GROUP BY p.id, m.nama, p.durasi, p.status
        ORDER BY p.id DESC
    """
    return tampilkan_data_peminjaman(koneksi, query, judul="PENGAJUAN DRAFT")


def lihat_history_peminjaman(koneksi):
    # History pustakawan menampilkan seluruh status peminjaman.
    # Query ini tidak memakai WHERE agar semua status ikut muncul.
    query = """
        SELECT
            p.id as ID,
            m.nama AS 'Nama mahasiswa',
            p.durasi as 'Durasi (Hari)',
            p.status as 'Status',
            CASE 
                WHEN p.dikembalikan IS NULL Then '-'
                WHEN p.status = 'disetujui' AND p.dikembalikan = 1 Then 'Sudah'
                ELSE 'Belum'
            END as 'Dikembalikan',
            GROUP_CONCAT(CONCAT(b.judul, ' (x', pd.jumlah, ')') SEPARATOR ', ') AS daftar_buku
        FROM peminjaman p
        JOIN mahasiswa m ON p.mahasiswa_id = m.id
        JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
        JOIN buku b ON pd.buku_id = b.id
        GROUP BY p.id, m.nama, p.durasi, p.status, p.dikembalikan
        ORDER BY p.id DESC
    """
    return tampilkan_data_peminjaman(koneksi, query, judul="HISTORY PEMINJAMAN")


def kembalikan_stok(conn, peminjaman_id):
    # Mengembalikan stok berdasarkan semua detail buku dalam satu peminjaman.
    detail_query = text(
        """
        SELECT buku_id, jumlah
        FROM peminjaman_detail
        WHERE peminjaman_id = :peminjaman_id
        """
    )
    update_query = text(
        """
        UPDATE buku
        SET stok = stok + :jumlah
        WHERE id = :buku_id
        """
    )

    # Detail peminjaman dibaca dulu untuk tahu stok buku mana yang dikembalikan.
    detail = conn.execute(detail_query, {"peminjaman_id": peminjaman_id}).mappings()
    for item in detail:
        conn.execute(
            update_query,
            {"buku_id": item["buku_id"], "jumlah": item["jumlah"]},
        )


def proses_pengajuan(koneksi):
    # Pustakawan menyetujui atau menolak pengajuan draft.
    tampilkan_judul("PROSES PENGAJUAN")
    print("Masukkan 0 pada input apa pun untuk membatalkan form.\n")

    lihat_pengajuan(koneksi)
    peminjaman_id = input_angka("Masukkan ID peminjaman")
    if peminjaman_id is None:
        print("Form dibatalkan.")
        return
    if peminjaman_id is False:
        return

    try:
        with koneksi.connect() as conn:
            # Cek status peminjaman sebelum pustakawan mengubah status.
            data = conn.execute(
                text("SELECT * FROM peminjaman WHERE id = :id"),
                {"id": peminjaman_id},
            ).mappings().first()

        if not data:
            print("Peminjaman tidak ditemukan.")
            return
        if data["status"] != "draft":
            print("Hanya pengajuan berstatus draft yang dapat diproses.")
            return

        tampilkan_menu(
            [
                ("1", "Setujui"),
                ("2", "Tolak"),
                ("0", "Batal"),
            ]
        )
        pilihan = input("Pilih keputusan [0 untuk batal]: ").strip()

        if pilihan == "0":
            print("Form dibatalkan.")
            return
        if pilihan == "1":
            with koneksi.begin() as conn:
                # Disetujui berarti buku masih dipinjam, jadi dikembalikan = FALSE.
                conn.execute(
                    text(
                        """
                        UPDATE peminjaman
                        SET status = 'disetujui',
                            dikembalikan = FALSE
                        WHERE id = :id
                        """
                    ),
                    {"id": peminjaman_id},
                )
            print("Pengajuan berhasil disetujui.")
        elif pilihan == "2":
            with koneksi.begin() as conn:
                # Jika ditolak, stok yang sudah dikurangi saat pengajuan dikembalikan.
                kembalikan_stok(conn, peminjaman_id)
                conn.execute(
                    text(
                        """
                        UPDATE peminjaman
                        SET status = 'ditolak',
                            dikembalikan = NULL
                        WHERE id = :id
                        """
                    ),
                    {"id": peminjaman_id},
                )
            print("Pengajuan ditolak dan stok buku dikembalikan.")
        else:
            print("Pilihan tidak valid.")
    except Exception as e:
        print(f"Terjadi error: {e}")


def pengembalian_buku(koneksi):
    # Pustakawan mencatat pengembalian buku berdasarkan id peminjaman.
    tampilkan_judul("PENGEMBALIAN BUKU")
    print("Masukkan 0 pada input apa pun untuk membatalkan form.\n")

    peminjaman_id = input_angka("Masukkan ID peminjaman")
    if peminjaman_id is None:
        print("Form dibatalkan.")
        return
    if peminjaman_id is False:
        return

    try:
        with koneksi.connect() as conn:
            # Data peminjaman dicek agar hanya yang disetujui dan belum kembali yang diproses.
            data = conn.execute(
                text("SELECT * FROM peminjaman WHERE id = :id"),
                {"id": peminjaman_id},
            ).mappings().first()

        if not data:
            print("Peminjaman tidak ditemukan.")
            return
        if data["status"] != "disetujui":
            print("Hanya peminjaman disetujui yang dapat dikembalikan.")
            return
        if data["dikembalikan"]:
            print("Peminjaman ini sudah dikembalikan.")
            return

        with koneksi.begin() as conn:
            # Saat buku dikembalikan, stok bertambah lagi dan status dikembalikan menjadi TRUE.
            kembalikan_stok(conn, peminjaman_id)
            conn.execute(
                text(
                    """
                    UPDATE peminjaman
                    SET dikembalikan = TRUE
                    WHERE id = :id
                    """
                ),
                {"id": peminjaman_id},
            )
        print("Pengembalian berhasil dicatat dan stok buku dikembalikan.")
    except Exception as e:
        print(f"Terjadi error: {e}")


def tampilkan_laporan_angka(koneksi):
    # Berikut adalah rangkuman deskripsi statistik
    try:
        # Satu query mengambil data mentah; semua operasi statistik dilakukan pandas.
        # Query dimulai dari mahasiswa agar mahasiswa tanpa peminjaman tetap ikut dihitung.
        raw_query = """
            SELECT
                m.id AS mahasiswa_id,
                m.nim,
                m.nama,
                m.jurusan,
                m.tahun_masuk,
                m.status_aktif,
                p.id AS peminjaman_id,
                p.durasi,
                p.status,
                p.dikembalikan,
                b.id AS buku_id,
                b.judul,
                b.penulis,
                b.kategori,
                b.stok,
                pd.jumlah
            FROM mahasiswa m
            LEFT JOIN peminjaman p ON m.id = p.mahasiswa_id
            LEFT JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
            LEFT JOIN buku b ON pd.buku_id = b.id
        """

    
        raw_df = pd.read_sql(raw_query, koneksi)
        raw_df['jumlah'] = raw_df["jumlah"].astype('Int32')
        raw_df['stok'] = raw_df["stok"].astype('Int32')

        # Data peminjaman valid adalah baris yang sudah punya peminjaman_id.
        peminjaman_df = raw_df[raw_df["peminjaman_id"].notna()]

        # Statistik mahasiswa dihitung dari data mahasiswa unik.
        mahasiswa_df = raw_df[
            ["mahasiswa_id", "nim", "nama", "jurusan", "tahun_masuk", "status_aktif"]
        ].drop_duplicates()
        total_mahasiswa = len(mahasiswa_df)
        total_mahasiswa_aktif = len(
            mahasiswa_df[mahasiswa_df["status_aktif"] == "aktif"]
        )
        total_mahasiswa_nonaktif = len(
            mahasiswa_df[mahasiswa_df["status_aktif"] == "nonaktif"]
        )

        # Data disetujui dipisahkan untuk statistik peminjaman sukses.
        disetujui_df = raw_df[raw_df["status"] == "disetujui"]

        # nunique menghitung mahasiswa unik yang pernah punya peminjaman disetujui.
        total_peminjam = disetujui_df["mahasiswa_id"].nunique()

        # groupby menghitung total buku per mahasiswa, lalu mean mencari rata-ratanya.
        total_buku_per_mahasiswa = disetujui_df.groupby("mahasiswa_id")["jumlah"].sum()
        rata_rata = (
            total_buku_per_mahasiswa.mean()
            if not total_buku_per_mahasiswa.empty
            else 0
        )

        # Drop duplicate diperlukan karena satu peminjaman bisa punya beberapa detail buku.
        transaksi_df = peminjaman_df[["peminjaman_id", "status"]].drop_duplicates()
        total = len(transaksi_df)
        disetujui = len(transaksi_df[transaksi_df["status"] == "disetujui"])
        persentase = (disetujui / total * 100) if total else 0

        # Statistik status dihitung dari transaksi unik, bukan dari baris detail.
        status_df = transaksi_df["status"].value_counts().reset_index()
        status_df.columns = ["status", "jumlah"]
        if not status_df.empty:
            status_df["persentase"] = (
                status_df["jumlah"] / status_df["jumlah"].sum() * 100
            ).round(2)

        # Statistik durasi hanya memakai peminjaman disetujui dan transaksi unik.
        durasi_df = disetujui_df[["peminjaman_id", "durasi"]].drop_duplicates()

        # Agregasi buku dan kategori memakai jumlah buku dari detail peminjaman disetujui.
        buku_df = (
            disetujui_df.groupby(["buku_id", "judul", "kategori"], as_index=False)[
                "jumlah"
            ]
            .sum()
            .rename(columns={"jumlah": "total_dipinjam"})
            .sort_values("total_dipinjam", ascending=False)
        )
        kategori_df = (
            disetujui_df.groupby("kategori", as_index=False)["jumlah"]
            .sum()
            .rename(columns={"jumlah": "total_dipinjam"})
            .sort_values("total_dipinjam", ascending=False)
        )

        # Stok rendah diambil dari daftar buku unik agar tidak dobel karena join detail.
        stok_rendah_df = (
            raw_df[["buku_id", "judul", "penulis", "kategori", "stok"]]
            .drop_duplicates()
            .query("stok <= 2")
            .sort_values(["stok", "judul"])
        )

        tampilkan_judul("DESKRIPSI STATISTIK PERPUSTAKAAN")
        print(f"Total mahasiswa terdaftar                   : {total_mahasiswa}")
        print(f"Total mahasiswa aktif                       : {total_mahasiswa_aktif}")
        print(f"Total mahasiswa nonaktif                    : {total_mahasiswa_nonaktif}")
        print(f"Jumlah total peminjam                       : {total_peminjam}")
        print(f"Rata-rata buku dipinjam setiap mahasiswa    : {rata_rata or 0:.2f}")
        print(f"Persentase pengajuan yang disetujui         : {persentase:.2f}%")

        print("\nStatistik durasi peminjaman disetujui:")
        if durasi_df.empty:
            print("Belum ada peminjaman yang disetujui.")
        else:
            print(
                f"Rata-rata durasi                            : {durasi_df['durasi'].mean():.2f} hari"
            )
            print(f"Durasi minimum                              : {durasi_df['durasi'].min()} hari")
            print(f"Durasi maksimum                             : {durasi_df['durasi'].max()} hari")

        print("\nRingkasan status pengajuan:")
        tampilkan_tabel(status_df)

        print("\nBuku 5 terpopuler:")
        tampilkan_tabel(buku_df.head(5))

        print("\nKategori terpopuler:")
        tampilkan_tabel(kategori_df)

        print("\nBuku dengan stok rendah:")
        tampilkan_tabel(stok_rendah_df)
    except Exception as e:
        print(f"Terjadi error: {e}")


def tampilkan_ringkasan_status(koneksi):
    # Menghitung proporsi draft, ditolak, dan disetujui.
    try:
        query = """
            SELECT status, COUNT(*) AS jumlah
            FROM peminjaman
            GROUP BY status
            ORDER BY jumlah DESC
        """
        df = pd.read_sql(query, koneksi)
        tampilkan_judul("RINGKASAN STATUS PENGAJUAN")

        if df.empty:
            print("Belum ada data peminjaman.")
            return

        # Persentase dihitung dari jumlah status dibagi total semua pengajuan.
        total = df["jumlah"].sum()
        df["persentase"] = (df["jumlah"] / total * 100).round(2)
        tampilkan_tabel(df)
    except Exception as e:
        print(f"Terjadi error: {e}")


def tampilkan_statistik_durasi(koneksi):
    # Statistik deskriptif sederhana untuk kolom durasi.
    try:
        query = """
            SELECT durasi
            FROM peminjaman
            WHERE status = 'disetujui'
        """
        df = pd.read_sql(query, koneksi)
        tampilkan_judul("STATISTIK DURASI PEMINJAMAN")

        if df.empty:
            print("Belum ada peminjaman yang disetujui.")
            return

        # mean/min/max berasal dari fungsi statistik dasar pandas.
        print(f"Rata-rata durasi : {df['durasi'].mean():.2f} hari")
        print(f"Durasi minimum   : {df['durasi'].min()} hari")
        print(f"Durasi maksimum  : {df['durasi'].max()} hari")
    except Exception as e:
        print(f"Terjadi error: {e}")


def tampilkan_buku_terpopuler(koneksi):
    # Tabel agregasi buku berdasarkan jumlah yang dipinjam.
    try:
        query = """
            SELECT
                b.id,
                b.judul,
                b.kategori,
                SUM(pd.jumlah) AS total_dipinjam AS "Total Dipinjam"
            FROM peminjaman p
            JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
            JOIN buku b ON pd.buku_id = b.id
            WHERE p.status = 'disetujui'
            GROUP BY b.id, b.judul, b.kategori
            ORDER BY total_dipinjam DESC
        """
        # SUM(pd.jumlah) menghitung total eksemplar yang dipinjam per buku.
        df = pd.read_sql(query, koneksi)
        tampilkan_judul("BUKU TERPOPULER")

        if df.empty:
            print("Belum ada data peminjaman yang disetujui.")
            return

        tampilkan_tabel(df)
    except Exception as e:
        print(f"Terjadi error: {e}")


def tampilkan_kategori_terpopuler(koneksi):
    # Tabel agregasi kategori untuk melihat minat baca paling tinggi.
    try:
        query = """
            SELECT
                b.kategori,
                SUM(pd.jumlah) AS total_dipinjam
            FROM peminjaman p
            JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
            JOIN buku b ON pd.buku_id = b.id
            WHERE p.status = 'disetujui'
            GROUP BY b.kategori
            ORDER BY total_dipinjam DESC
        """
        # Agregasi per kategori menunjukkan jenis buku yang paling diminati.
        df = pd.read_sql(query, koneksi)
        tampilkan_judul("KATEGORI TERPOPULER")

        if df.empty:
            print("Belum ada data peminjaman yang disetujui.")
            return

        tampilkan_tabel(df)
    except Exception as e:
        print(f"Terjadi error: {e}")


def lihat_buku_stok_rendah(koneksi):
    # Laporan operasional untuk membantu pustakawan melihat stok yang hampir habis.
    try:
        query = """
            SELECT id, judul, penulis, kategori, stok
            FROM buku
            WHERE stok <= 2
            ORDER BY stok ASC, judul ASC
        """
        # Stok <= 2 dianggap rendah untuk membantu prioritas penambahan stok.
        df = pd.read_sql(query, koneksi)
        tampilkan_judul("BUKU DENGAN STOK RENDAH")

        if df.empty:
            print("Tidak ada buku dengan stok rendah.")
            return

        tampilkan_tabel(df)
    except Exception as e:
        print(f"Terjadi error: {e}")


def grafik_peminjaman_mahasiswa(koneksi):
    # Grafik horizontal cocok untuk nama mahasiswa yang cenderung panjang.
    try:
        query = """
            SELECT
                m.nama,
                SUM(pd.jumlah) AS total_dipinjam
            FROM peminjaman p
            JOIN mahasiswa m ON p.mahasiswa_id = m.id
            JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
            WHERE p.status = 'disetujui'
            GROUP BY m.id, m.nama
            ORDER BY total_dipinjam DESC
        """
        # Hasil query menjadi sumber data untuk bar chart seaborn.
        df = pd.read_sql(query, koneksi)
        if df.empty:
            print("Belum ada data peminjaman yang disetujui.")
            return

        # figsize mengatur ukuran jendela grafik agar label tidak terlalu padat.
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x="total_dipinjam", y="nama")
        plt.title("Jumlah Buku Dipinjam per Mahasiswa")
        plt.xlabel("Total Buku Dipinjam")
        plt.ylabel("Mahasiswa")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Terjadi error: {e}")


def grafik_status_peminjaman(koneksi):
    # Grafik status membantu melihat perbandingan draft, ditolak, dan disetujui.
    try:
        query = """
            SELECT status, COUNT(*) AS jumlah
            FROM peminjaman
            GROUP BY status
        """
        # Data status dipakai sebagai sumbu x, jumlah sebagai sumbu y.
        df = pd.read_sql(query, koneksi)
        if df.empty:
            print("Belum ada data peminjaman.")
            return

        plt.figure(figsize=(8, 5))
        sns.barplot(data=df, x="status", y="jumlah")
        plt.title("Jumlah Pengajuan Berdasarkan Status")
        plt.xlabel("Status")
        plt.ylabel("Jumlah")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Terjadi error: {e}")


def grafik_buku_terpopuler(koneksi):
    # Visualisasi buku paling sering dipinjam.
    try:
        query = """
            SELECT
                b.judul,
                SUM(pd.jumlah) AS total_dipinjam
            FROM peminjaman p
            JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
            JOIN buku b ON pd.buku_id = b.id
            WHERE p.status = 'disetujui'
            GROUP BY b.id, b.judul
            ORDER BY total_dipinjam DESC
        """
        # Judul buku panjang, sehingga grafik horizontal lebih mudah dibaca.
        df = pd.read_sql(query, koneksi)
        if df.empty:
            print("Belum ada data peminjaman yang disetujui.")
            return

        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x="total_dipinjam", y="judul")
        plt.title("Buku Paling Sering Dipinjam")
        plt.xlabel("Total Dipinjam")
        plt.ylabel("Judul Buku")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Terjadi error: {e}")


def grafik_kategori_terpopuler(koneksi):
    # Visualisasi kategori buku terpopuler.
    try:
        query = """
            SELECT
                b.kategori,
                SUM(pd.jumlah) AS total_dipinjam
            FROM peminjaman p
            JOIN peminjaman_detail pd ON p.id = pd.peminjaman_id
            JOIN buku b ON pd.buku_id = b.id
            WHERE p.status = 'disetujui'
            GROUP BY b.kategori
            ORDER BY total_dipinjam DESC
        """
        # Grafik kategori dibuat vertikal karena label kategori relatif pendek.
        df = pd.read_sql(query, koneksi)
        if df.empty:
            print("Belum ada data peminjaman yang disetujui.")
            return

        plt.figure(figsize=(9, 5))
        sns.barplot(data=df, x="kategori", y="total_dipinjam")
        plt.title("Kategori Buku Paling Populer")
        plt.xlabel("Kategori")
        plt.ylabel("Total Dipinjam")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Terjadi error: {e}")


def grafik_durasi_peminjaman(koneksi):
    # Histogram untuk melihat sebaran durasi peminjaman.
    try:
        query = """
            SELECT durasi
            FROM peminjaman
            WHERE status = 'disetujui'
        """
        # Histogram cocok untuk melihat sebaran angka durasi peminjaman.
        df = pd.read_sql(query, koneksi)
        if df.empty:
            print("Belum ada peminjaman yang disetujui.")
            return

        plt.figure(figsize=(8, 5))
        sns.histplot(df["durasi"], bins=5, kde=True)
        plt.title("Distribusi Durasi Peminjaman")
        plt.xlabel("Durasi (hari)")
        plt.ylabel("Jumlah Peminjaman")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Terjadi error: {e}")


def menu_manajemen_peminjaman(koneksi):
    # Navigasi pustakawan untuk approval, pengembalian, dan history.
    while True:
        bersihkan_layar()
        tampilkan_judul("MANAJEMEN PEMINJAMAN")
        tampilkan_menu(
            [
                ("1", "Lihat Pengajuan"),
                ("2", "Proses Pengajuan"),
                ("3", "Form Pengembalian Buku"),
                ("4", "Lihat History Peminjaman"),
                ("5", "Kembali"),
            ]
        )

        pilihan = input_menu("1-5")

        if pilihan == "1":
            lihat_pengajuan(koneksi)
            tekan_enter()
        elif pilihan == "2":
            proses_pengajuan(koneksi)
            tekan_enter()
        elif pilihan == "3":
            pengembalian_buku(koneksi)
            tekan_enter()
        elif pilihan == "4":
            lihat_history_peminjaman(koneksi)
            tekan_enter()
        elif pilihan == "5":
            break
        else:
            print("Pilihan tidak valid.")
            tekan_enter()


def menu_laporan(koneksi):
    # Menu laporan: nomor 1 untuk semua statistik, sisanya untuk grafik.
    while True:
        bersihkan_layar()
        tampilkan_judul("LAPORAN")
        tampilkan_menu(
            [
                ("1", "Deskripsi Statistik Perpustakaan"),
                ("2", "Grafik Peminjaman Mahasiswa"),
                ("3", "Grafik Status Pengajuan"),
                ("4", "Grafik Buku Terpopuler"),
                ("5", "Grafik Kategori Terpopuler"),
                ("6", "Grafik Distribusi Durasi"),
                ("7", "Kembali"),
            ]
        )

        pilihan = input_menu("1-7")

        if pilihan == "1":
            tampilkan_laporan_angka(koneksi)
            tekan_enter()
        elif pilihan == "2":
            grafik_peminjaman_mahasiswa(koneksi)
            tekan_enter()
        elif pilihan == "3":
            grafik_status_peminjaman(koneksi)
            tekan_enter()
        elif pilihan == "4":
            grafik_buku_terpopuler(koneksi)
            tekan_enter()
        elif pilihan == "5":
            grafik_kategori_terpopuler(koneksi)
            tekan_enter()
        elif pilihan == "6":
            grafik_durasi_peminjaman(koneksi)
            tekan_enter()
        elif pilihan == "7":
            break
        else:
            print("Pilihan tidak valid.")
            tekan_enter()
