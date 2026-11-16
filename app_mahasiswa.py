"""
app_mahasiswa.py
Pengolahan data mahasiswa berbasis CLI dengan paradigma fungsional.
Wajib memanfaatkan fplib.py.
"""

from fplib import (
    alur_proses,
    filter_data,
    ubah_data,
    cari_item,
    urut_data,
    kelompok_data,
    total_nilai,
    rerata_nilai,
    nilai_ekstrem,
    cek_valid,
    format_rupiah,
    bersih_teks,
    potong_data,
    hitung_frekuensi,
    gabung_rekursif,
)


# Data contoh: nama, kelas, nilai tugas, UTS, UAS.
MAHASISWA_AWAL = [
    {"nama": "Andi", "kelas": "A", "tugas": 80, "uts": 75, "uas": 85},
    {"nama": "Budi", "kelas": "A", "tugas": 70, "uts": 65, "uas": 72},
    {"nama": "Citra", "kelas": "B", "tugas": 90, "uts": 88, "uas": 92},
    {"nama": "Dewi", "kelas": "B", "tugas": 60, "uts": 70, "uas": 68},
    {"nama": "Eko", "kelas": "C", "tugas": 85, "uts": 80, "uas": 78},
    {"nama": "Farah", "kelas": "C", "tugas": 95, "uts": 92, "uas": 96},
]


# ---------- Fungsi murni ----------

def nilai_akhir(mahasiswa):
    """Hitung nilai akhir: 30% tugas, 30% UTS, 40% UAS."""
    return (
        mahasiswa["tugas"] * 0.30
        + mahasiswa["uts"] * 0.30
        + mahasiswa["uas"] * 0.40
    )


def predikat(nilai):
    """Tentukan predikat berdasarkan nilai akhir."""
    if nilai >= 85:
        return "A"
    if nilai >= 75:
        return "B"
    if nilai >= 65:
        return "C"
    if nilai >= 55:
        return "D"
    return "E"


def tambah_nilai_akhir(mahasiswa):
    """Kembalikan mahasiswa baru dengan nilai akhir dan predikat."""
    akhir = nilai_akhir(mahasiswa)
    return {
        **mahasiswa,
        "nilai_akhir": akhir,
        "predikat": predikat(akhir),
    }


def proses_mahasiswa(data_mahasiswa):
    """Terapkan alur proses: validasi, transformasi, dan pemeringkatan."""
    def valid(mahasiswa):
        nilai_wajib = [mahasiswa["tugas"], mahasiswa["uts"], mahasiswa["uas"]]
        return all(cek_valid(nilai) and 0 <= nilai <= 100 for nilai in nilai_wajib)

    data_valid = filter_data(data_mahasiswa, valid)
    data_lengkap = ubah_data(data_valid, tambah_nilai_akhir)
    data_terurut = urut_data(
        data_lengkap,
        kunci=lambda mahasiswa: mahasiswa["nilai_akhir"],
        terbalik=True,
    )

    return data_terurut


def tambah_peringkat(data_terurut):
    """Tambahkan peringkat berdasarkan urutan nilai akhir."""
    def beri_peringkat(pasangan):
        indeks, mahasiswa = pasangan
        return {**mahasiswa, "peringkat": indeks + 1}

    return ubah_data(list(enumerate(data_terurut)), beri_peringkat)


def filter_ipk(data_mahasiswa, batas_bawah=None, batas_atas=None):
    """Filter mahasiswa berdasarkan rentang IPK atau nilai akhir."""
    def dalam_rentang(mahasiswa):
        nilai = mahasiswa["nilai_akhir"]

        if batas_bawah is not None and nilai < batas_bawah:
            return False
        if batas_atas is not None and nilai > batas_atas:
            return False
        return True

    return filter_data(data_mahasiswa, dalam_rentang)


def filter_kelas(data_mahasiswa, kelas):
    """Filter mahasiswa berdasarkan kelas."""
    kelas_bersih = bersih_teks(str(kelas)).upper()
    return filter_data(
        data_mahasiswa,
        lambda mahasiswa: bersih_teks(mahasiswa["kelas"]).upper() == kelas_bersih,
    )


def rata_rata_nilai_akhir(data_mahasiswa):
    """Hitung rata-rata nilai akhir."""
    nilai = ubah_data(data_mahasiswa, lambda mahasiswa: mahasiswa["nilai_akhir"])
    return rerata_nilai(nilai) if nilai else 0.0


def total_nilai_akhir(data_mahasiswa):
    """Hitung total nilai akhir."""
    nilai = ubah_data(data_mahasiswa, lambda mahasiswa: mahasiswa["nilai_akhir"])
    return total_nilai(nilai)


def nilai_tertinggi_terendah(data_mahasiswa):
    """Kembalikan pasangan nilai tertinggi dan terendah."""
    nilai = ubah_data(data_mahasiswa, lambda mahasiswa: mahasiswa["nilai_akhir"])
    return nilai_ekstrem(nilai) if nilai else (None, None)


def kelompok_per_kelas(data_mahasiswa):
    """Kelompokkan mahasiswa berdasarkan kelas."""
    return kelompok_data(data_mahasiswa, kunci=lambda mahasiswa: mahasiswa["kelas"])


def kelompok_per_predikat(data_mahasiswa):
    """Kelompokkan mahasiswa berdasarkan predikat."""
    return kelompok_data(data_mahasiswa, kunci=lambda mahasiswa: mahasiswa["predikat"])


def frekuensi_predikat(data_mahasiswa):
    """Hitung frekuensi setiap predikat."""
    predikat_list = ubah_data(
        data_mahasiswa,
        lambda mahasiswa: mahasiswa["predikat"],
    )
    return hitung_frekuensi(predikat_list)


def cari_mahasiswa(data_mahasiswa, nama):
    """Cari satu mahasiswa berdasarkan nama."""
    nama_bersih = bersih_teks(nama).lower()
    return cari_item(
        data_mahasiswa,
        lambda mahasiswa: bersih_teks(mahasiswa["nama"]).lower() == nama_bersih,
    )


def format_mahasiswa(mahasiswa):
    """Format satu baris data mahasiswa."""
    return (
        f"{mahasiswa['peringkat']:>2}. "
        f"{mahasiswa['nama']:<10} "
        f"Kelas {mahasiswa['kelas']:<2} "
        f"Nilai akhir: {mahasiswa['nilai_akhir']:.2f} "
        f"Predikat: {mahasiswa['predikat']}"
    )


def tampilkan_mahasiswa(data_mahasiswa, judul="Data Mahasiswa"):
    print(f"\n=== {judul} ===")

    if not data_mahasiswa:
        print("Tidak ada data yang sesuai.")
        return

    for mahasiswa in data_mahasiswa:
        print(format_mahasiswa(mahasiswa))


def tampilkan_kelompok(kelompok, judul):
    print(f"\n=== {judul} ===")

    if not kelompok:
        print("Tidak ada data.")
        return

    for kunci, anggota in kelompok.items():
        print(f"\nKelompok {kunci} ({len(anggota)} mahasiswa):")
        for mahasiswa in anggota:
            print(f"- {mahasiswa['nama']} | Nilai akhir: {mahasiswa['nilai_akhir']:.2f}")


def tampilkan_statistik(data_mahasiswa):
    print("\n=== Statistik Nilai Akhir ===")

    if not data_mahasiswa:
        print("Tidak ada data.")
        return

    tertinggi, terendah = nilai_tertinggi_terendah(data_mahasiswa)

    print(f"Jumlah mahasiswa : {len(data_mahasiswa)}")
    print(f"Total nilai      : {total_nilai_akhir(data_mahasiswa):.2f}")
    print(f"Rata-rata nilai  : {rata_rata_nilai_akhir(data_mahasiswa):.2f}")
    print(f"Nilai tertinggi  : {tertinggi:.2f}")
    print(f"Nilai terendah   : {terendah:.2f}")

    print("\nFrekuensi predikat:")
    for pred, jumlah in frekuensi_predikat(data_mahasiswa).items():
        print(f"- {pred}: {jumlah} mahasiswa")


# ---------- Alur CLI ----------

def input_angka(prompt, batas_bawah=0, batas_atas=100):
    """Minta angka valid dari pengguna."""
    teks = input(prompt).strip()

    try:
        nilai = float(teks)
    except ValueError:
        raise ValueError("Input harus berupa angka.")

    if not cek_valid(nilai) or nilai < batas_bawah or nilai > batas_atas:
        raise ValueError(f"Nilai harus berada antara {batas_bawah} dan {batas_atas}.")

    return nilai


def tambah_mahasiswa(data_mahasiswa):
    """Tambah satu data mahasiswa baru secara fungsional."""
    print("\n=== Tambah Mahasiswa ===")

    nama = bersih_teks(input("Nama: "))
    kelas = bersih_teks(input("Kelas: ")).upper()

    if not nama or not kelas:
        raise ValueError("Nama dan kelas tidak boleh kosong.")

    tugas = input_angka("Nilai tugas (0-100): ")
    uts = input_angka("Nilai UTS (0-100): ")
    uas = input_angka("Nilai UAS (0-100): ")

    mahasiswa_baru = {
        "nama": nama,
        "kelas": kelas,
        "tugas": tugas,
        "uts": uts,
        "uas": uas,
    }

    return data_mahasiswa + [mahasiswa_baru]


def jalankan_cli():
    data_mahasiswa = MAHASISWA_AWAL

    print("=== Aplikasi Pengolahan Data Mahasiswa ===")

    while True:
        print(
            "\nMenu:\n"
            "1. Tampilkan semua mahasiswa\n"
            "2. Tambah mahasiswa\n"
            "3. Filter berdasarkan kelas\n"
            "4. Filter berdasarkan nilai akhir minimum\n"
            "5. Filter berdasarkan rentang nilai akhir\n"
            "6. Tampilkan peringkat\n"
            "7. Kelompokkan per kelas\n"
            "8. Kelompokkan per predikat\n"
            "9. Statistik nilai\n"
            "10. Cari mahasiswa\n"
            "0. Keluar"
        )

        pilihan = input("\nPilih menu: ").strip()

        try:
            if pilihan == "0":
                print("Aplikasi ditutup.")
                break

            elif pilihan == "1":
                data_proses = tambah_peringkat(proses_mahasiswa(data_mahasiswa))
                tampilkan_mahasiswa(data_proses, "Semua Mahasiswa")

            elif pilihan == "2":
                data_mahasiswa = tambah_mahasiswa(data_mahasiswa)
                print("Data mahasiswa berhasil ditambahkan.")

            elif pilihan == "3":
                kelas = input("Masukkan kelas: ")
                data_proses = tambah_peringkat(
                    proses_mahasiswa(filter_kelas(data_mahasiswa, kelas))
                )
                tampilkan_mahasiswa(data_proses, f"Mahasiswa Kelas {kelas.upper()}")

            elif pilihan == "4":
                batas = input_angka("Nilai akhir minimum: ", 0, 100)
                data_terfilter = filter_ipk(
                    proses_mahasiswa(data_mahasiswa),
                    batas_bawah=batas,
                )
                data_proses = tambah_peringkat(data_terfilter)
                tampilkan_mahasiswa(
                    data_proses,
                    f"Mahasiswa dengan Nilai Akhir >= {batas}",
                )

            elif pilihan == "5":
                bawah = input_angka("Nilai akhir minimum: ", 0, 100)
                atas = input_angka("Nilai akhir maksimum: ", 0, 100)

                if bawah > atas:
                    raise ValueError("Nilai minimum tidak boleh lebih besar dari maksimum.")

                data_terfilter = filter_ipk(
                    proses_mahasiswa(data_mahasiswa),
                    batas_bawah=bawah,
                    batas_atas=atas,
                )
                data_proses = tambah_peringkat(data_terfilter)
                tampilkan_mahasiswa(
                    data_proses,
                    f"Mahasiswa dengan Nilai Akhir {bawah}-{atas}",
                )

            elif pilihan == "6":
                data_proses = tambah_peringkat(proses_mahasiswa(data_mahasiswa))
                tampilkan_mahasiswa(data_proses, "Peringkat Mahasiswa")

            elif pilihan == "7":
                data_proses = proses_mahasiswa(data_mahasiswa)
                tampilkan_kelompok(
                    kelompok_per_kelas(data_proses),
                    "Pengelompokan per Kelas",
                )

            elif pilihan == "8":
                data_proses = proses_mahasiswa(data_mahasiswa)
                tampilkan_kelompok(
                    kelompok_per_predikat(data_proses),
                    "Pengelompokan per Predikat",
                )

            elif pilihan == "9":
                data_proses = proses_mahasiswa(data_mahasiswa)
                tampilkan_statistik(data_proses)

            elif pilihan == "10":
                nama = input("Masukkan nama mahasiswa: ")
                hasil = cari_mahasiswa(
                    proses_mahasiswa(data_mahasiswa),
                    nama,
                )

                if hasil:
                    print("\nMahasiswa ditemukan:")
                    print(format_mahasiswa({**hasil, "peringkat": "-"}))
                else:
                    print(f"Mahasiswa '{nama}' tidak ditemukan.")

            else:
                print("Pilihan menu tidak valid.")

        except ValueError as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    jalankan_cli()