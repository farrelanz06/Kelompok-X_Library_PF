"""
app_kalkulator.py
Kalkulator ilmiah/statistik berbasis CLI dengan paradigma fungsional.
Wajib memanfaatkan fplib.py.
"""

import math
from functools import reduce

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


RIWAYAT = []


# ---------- Fungsi murni ----------

def angka_dari_teks(teks):
    """Ubah teks menjadi angka; kembalikan None bila tidak valid."""
    teks = bersih_teks(str(teks))
    try:
        nilai = float(teks)
    except (TypeError, ValueError):
        return None
    return nilai


def valid_angka(nilai):
    """Predikat: angka bukan None dan bukan NaN."""
    return nilai is not None and cek_valid(nilai) and not math.isnan(nilai)


def tambah(a, b):
    return a + b


def kurang(a, b):
    return a - b


def kali(a, b):
    return a * b


def bagi(a, b):
    if b == 0:
        raise ZeroDivisionError("Pembagian dengan nol tidak diperbolehkan.")
    return a / b


def pangkat(a, b):
    return a ** b


def akar(a):
    if a < 0:
        raise ValueError("Akar kuadrat hanya untuk bilangan non-negatif.")
    return math.sqrt(a)


def logaritma(a, basis=math.e):
    if a <= 0:
        raise ValueError("Logaritma hanya untuk bilangan positif.")
    if basis <= 0 or basis == 1:
        raise ValueError("Basis logaritma harus positif dan tidak boleh 1.")
    return math.log(a, basis)


def sinus(sudut):
    return math.sin(math.radians(sudut))


def kosinus(sudut):
    return math.cos(math.radians(sudut))


def tangen(sudut):
    return math.tan(math.radians(sudut))


def hitung(operasi, a, b=None):
    """Terapkan operasi secara fungsional melalui pemetaan operasi."""
    operasi_tunggal = {
        "akar": akar,
        "sin": sinus,
        "cos": kosinus,
        "tan": tangen,
    }

    operasi_biner = {
        "+": tambah,
        "-": kurang,
        "*": kali,
        "/": bagi,
        "^": pangkat,
        "log": logaritma,
    }

    if operasi in operasi_tunggal:
        return operasi_tunggal[operasi](a)

    if operasi in operasi_biner:
        if b is None:
            raise ValueError(f"Operasi '{operasi}' membutuhkan dua angka.")
        return operasi_biner[operasi](a, b)

    raise ValueError(f"Operasi tidak dikenal: {operasi}")


def simpan_riwayat(operasi, a, b, hasil):
    """Buat entri riwayat sebagai struktur data immutable."""
    return {
        "operasi": operasi,
        "a": a,
        "b": b,
        "hasil": hasil,
    }


def tampilkan_riwayat(riwayat):
    """Ubah daftar riwayat menjadi daftar teks siap tampil."""
    def format_item(item):
        if item["b"] is None:
            ekspresi = f"{item['operasi']}({item['a']})"
        else:
            ekspresi = f"{item['a']} {item['operasi']} {item['b']}"
        return f"{ekspresi} = {item['hasil']}"

    return ubah_data(riwayat, format_item)


def statistik_dari_riwayat(riwayat):
    """Ambil hasil perhitungan yang valid lalu hitung statistiknya."""
    hasil = ubah_data(riwayat, lambda item: item["hasil"])
    hasil_valid = filter_data(hasil, valid_angka)

    if not hasil_valid:
        return {
            "jumlah": 0,
            "total": 0.0,
            "rata_rata": 0.0,
            "minimum": None,
            "maksimum": None,
        }

    minimum, maksimum = nilai_ekstrem(hasil_valid)

    return {
        "jumlah": len(hasil_valid),
        "total": total_nilai(hasil_valid),
        "rata_rata": rerata_nilai(hasil_valid),
        "minimum": minimum,
        "maksimum": maksimum,
    }


def gabungkan_hasil(riwayat):
    """Contoh penggunaan gabung_rekursif untuk menjumlahkan seluruh hasil."""
    hasil = ubah_data(riwayat, lambda item: item["hasil"])
    hasil_valid = filter_data(hasil, valid_angka)
    return gabung_rekursif(hasil_valid, tambah)


def format_statistik(stat):
    """Format hasil statistik untuk ditampilkan."""
    if stat["jumlah"] == 0:
        return "Belum ada hasil perhitungan yang valid."

    return (
        f"Jumlah hasil : {stat['jumlah']}\n"
        f"Total        : {stat['total']:.6f}\n"
        f"Rata-rata    : {stat['rata_rata']:.6f}\n"
        f"Nilai minimum: {stat['minimum']:.6f}\n"
        f"Nilai maksimum: {stat['maksimum']:.6f}"
    )


# ---------- Alur CLI ----------

def proses_input_dasar(token):
    """Proses input 'a operator b' atau 'operator a'."""
    bagian = bersih_teks(token).split()

    if len(bagian) == 3:
        a = angka_dari_teks(bagian[0])
        operasi = bagian[1]
        b = angka_dari_teks(bagian[2])
        return operasi, a, b

    if len(bagian) == 2:
        operasi = bagian[0]
        a = angka_dari_teks(bagian[1])
        return operasi, a, None

    raise ValueError(
        "Format salah. Gunakan: '12 + 3', '8 / 2', 'akar 16', atau 'sin 30'."
    )


def jalankan_perhitungan(token):
    """Fungsi utama untuk memproses satu perhitungan."""
    operasi, a, b = proses_input_dasar(token)

    if not valid_angka(a) or (b is not None and not valid_angka(b)):
        raise ValueError("Input harus berupa angka yang valid.")

    hasil = hitung(operasi, a, b)
    entri = simpan_riwayat(operasi, a, b, hasil)

    return hasil, entri


def tampilkan_menu():
    print("\n=== Kalkulator Ilmiah/Statistik ===")
    print("Perhitungan:")
    print("  12 + 3        Penjumlahan")
    print("  12 - 3        Pengurangan")
    print("  12 * 3        Perkalian")
    print("  12 / 3        Pembagian")
    print("  12 ^ 3        Pangkat")
    print("  8 log 2       Logaritma")
    print("  akar 16       Akar kuadrat")
    print("  sin 30        Sinus (derajat)")
    print("  cos 60        Kosinus (derajat)")
    print("  tan 45        Tangen (derajat)")
    print("\nPerintah:")
    print("  riwayat       Tampilkan riwayat")
    print("  statistik     Total, rata-rata, min, dan maks")
    print("  total         Jumlahkan seluruh hasil")
    print("  bantuan       Tampilkan menu")
    print("  keluar        Keluar aplikasi")


def jalankan_cli():
    tampilkan_menu()

    while True:
        try:
            token = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAplikasi ditutup.")
            break

        if not token:
            continue

        perintah = bersih_teks(token).lower()

        if perintah == "keluar":
            print("Terima kasih. Aplikasi ditutup.")
            break

        if perintah == "bantuan":
            tampilkan_menu()
            continue

        if perintah == "riwayat":
            if not RIWAYAT:
                print("Riwayat masih kosong.")
            else:
                print("\nRiwayat perhitungan:")
                for baris in tampilkan_riwayat(RIWAYAT):
                    print(f"- {baris}")
            continue

        if perintah == "statistik":
            print(format_statistik(statistik_dari_riwayat(RIWAYAT)))
            continue

        if perintah == "total":
            hasil = gabungkan_hasil(RIWAYAT)
            print(f"Total seluruh hasil valid: {hasil:.6f}")
            continue

        try:
            hasil, entri = jalankan_perhitungan(token)
            RIWAYAT.append(entri)
            print(f"Hasil: {hasil:.6f}")
        except (ValueError, ZeroDivisionError, OverflowError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    jalankan_cli()