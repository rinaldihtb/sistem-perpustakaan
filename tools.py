import subprocess
import os

# Karakter "=" sebanyak 64 karakter
GARIS_EQUAL = "=" * 64

# Karakter "-" sebanyak 64 karakter
GARIS_DASH = "-" * 64

# Fungsi-fungsi umum yang dipakai di banyak tempat
def tekan_enter():
    input("\nTekan Enter untuk melanjutkan...")


def bersihkan_layar():    
    # Proses untuk membersihkan layar
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)


def tampilkan_judul(teks):
    # Proses untuk print judul
    print("\n" + GARIS_EQUAL)
    # Menambahkan spasi kiri dan kanan setelah text dengan total 64 karakter
    print(teks.center(64))
    print(GARIS_EQUAL)


def tampilkan_menu(daftar_menu):
    # Fungsi untuk menampilkan navigasi dengan format sebagai contoh berikut :
    # daftar_menu = [
    #     ("1", "Menu Pertama")
    #     ("2", "Menu Pertama")
    # ]
    for nomor, menu in daftar_menu:
        print(f"  {nomor}. {menu}")
    print(GARIS_DASH)


def input_menu(rentang):
    # Fungsi untuk melakukan input dengan format :
    # Pilih Menu (1-3) :
    # .strip berfungsi menambahkan karakter ":" diakhir kalimat 
    return input(f"\nPilih menu ({rentang}): ").strip()


def potong_teks(nilai, panjang_maksimal=100):
    # Mengubah nilai apa pun menjadi teks agar aman saat dihitung panjangnya.
    teks = "" if nilai is None else str(nilai)
    # Jika teks terlalu panjang, potong agar tabel tidak melebar berlebihan.
    if len(teks) > panjang_maksimal:
        return teks[: panjang_maksimal - 3] + "..."
    return teks


def tampilkan_tabel(df):
    # Fungsi untuk menampilkan dataframe dalam bentuk tabel terminal yang lebih rapi.
    if df.empty:
        print("Tidak ada data.")
        return

    # DataFrame disalin agar proses formatting tidak mengubah data aslinya.
    data = df.copy()

    # Semua cell diubah menjadi teks pendek agar lebar kolom stabil.
    for kolom in data.columns:
        data[kolom] = data[kolom].apply(potong_teks)

    # Lebar kolom dihitung dari nama kolom dan isi terpanjang.
    lebar_kolom = {}
    for kolom in data.columns:
        panjang_header = len(str(kolom))
        panjang_data = data[kolom].map(len).max()
        lebar_kolom[kolom] = max(panjang_header, panjang_data) + 2

    # Garis pembatas dibuat dinamis mengikuti jumlah dan lebar kolom.
    garis = "+"
    for kolom in data.columns:
        garis += "-" * lebar_kolom[kolom] + "+"

    # Header tabel.
    print(garis)
    baris_header = "|"
    for kolom in data.columns:
        baris_header += f" {str(kolom).upper():<{lebar_kolom[kolom] - 1}}|"
    print(baris_header)
    print(garis)

    # Isi tabel.
    for _, baris in data.iterrows():
        baris_tabel = "|"
        for kolom in data.columns:
            baris_tabel += f" {baris[kolom]:<{lebar_kolom[kolom] - 1}}|"
        print(baris_tabel)

    print(garis)


def input_teks(pesan):
    # Input form mengembalikan None jika user memilih batal dengan angka 0.
    nilai = input(f"{pesan} [0 untuk batal]: ")
    if nilai == "0":
        return None
    return nilai


def input_angka(pesan):
    # fungsi Input untuk mengambil data angka
    nilai = input(f"{pesan} [0 untuk batal]: ")
    if nilai == "0":
        return None
    try:
        # konversi string ke integer
        return int(nilai)
    except ValueError:
        # mengembalikan error agar input harus berupa angka.
        print("Input harus berupa angka.")
        return False
