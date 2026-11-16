import random
from typing import Any, Dict, Optional, Sequence, Tuple

import fplib as fp


# --------------------------------------------------------------------------
# Konstanta
# --------------------------------------------------------------------------
ANGKA_MIN = 1
ANGKA_MAKS = 100
BATAS_TEBAKAN = 10
POIN_PER_SISA_KESEMPATAN = 10
HADIAH_PER_POIN = 1000
UKURAN_HALAMAN = 3
BATAS_PAPAN_SKOR = 5
MENANG = "menang"
MENYERAH = "menyerah"

Rekor = Dict[str, Any]


# --------------------------------------------------------------------------
# Fungsi murni
# --------------------------------------------------------------------------
def hitung_skor(status: str, jumlah_tebakan: int) -> int:
    if status != MENANG:
        return 0
    return max(
        0,
        (BATAS_TEBAKAN - jumlah_tebakan + 1) * POIN_PER_SISA_KESEMPATAN,
    )


def buat_rekor(
    nama: str, status: str, tebakan: Tuple[int, ...]
) -> Rekor:
    skor = hitung_skor(status, len(tebakan))
    return {
        "nama": nama,
        "status": status,
        "percobaan": len(tebakan),
        "skor": skor,
        "hadiah": skor * HADIAH_PER_POIN,
        "tebakan": [list(tebakan)],
    }


def hitung_statistik(riwayat: Sequence[Rekor]) -> Dict[str, Any]:
    selesai = fp.filter_data(lambda item: item["status"] == MENANG, riwayat)
    jumlah_menang = fp.ubah_data(lambda item: item["percobaan"], selesai)
    terbaik = (
        fp.cari_item(lambda item: item["percobaan"] == min(jumlah_menang), selesai)
        if jumlah_menang
        else None
    )
    percobaan = fp.ubah_data(lambda item: item["percobaan"], riwayat)
    skor = fp.ubah_data(lambda item: item["skor"], riwayat)
    skor_min, skor_maks = fp.nilai_ekstrem(skor)
    semua_tebakan = fp.gabung_rekursif(
        fp.ubah_data(lambda item: item["tebakan"], riwayat)
    )

    return {
        "total_permainan": len(riwayat),
        "menang": len(selesai),
        "menyerah": len(
            fp.filter_data(lambda item: item["status"] == MENYERAH, riwayat)
        ),
        "total_percobaan": fp.total_nilai(percobaan),
        "rata_percobaan": fp.rerata_nilai(percobaan),
        "skor_min": skor_min,
        "skor_maks": skor_maks,
        "terbaik": terbaik,
        "papan_skor": fp.urut_data(
            riwayat, kunci=lambda item: item["skor"], terbalik=True
        )[:BATAS_PAPAN_SKOR],
        "total_hadiah": fp.total_nilai(
            fp.ubah_data(lambda item: item["hadiah"], riwayat)
        ),
        "halaman_riwayat": fp.potong_data(riwayat, UKURAN_HALAMAN),
        "frekuensi_tebakan": fp.urut_data(
            list(fp.hitung_frekuensi(semua_tebakan).items()),
            kunci=lambda pasangan: pasangan[1],
            terbalik=True,
        ),
    }


# --------------------------------------------------------------------------
# Input & validasi
# --------------------------------------------------------------------------
def minta_angka(
    prompt: str, minimum: int = ANGKA_MIN, maksimum: int = ANGKA_MAKS
) -> Optional[int]:
    while True:
        teks = fp.bersih_teks(input(prompt))
        if teks in {"keluar", "q"}:
            return None
        try:
            angka = int(teks)
        except ValueError:
            print("Masukkan angka bulat, atau ketik 'keluar'/'q' untuk berhenti.")
            continue
        if minimum <= angka <= maksimum:
            return angka
        print(f"Angka harus berada di antara {minimum} dan {maksimum}.")


# --------------------------------------------------------------------------
# Statistik & tampilan
# --------------------------------------------------------------------------
def tampilkan_statistik(riwayat: Sequence[Rekor]) -> None:
    if not riwayat:
        print("Belum ada data permainan.")
        return

    statistik = hitung_statistik(riwayat)
    print("\n========== STATISTIK ==========")
    print(f"Total permainan : {statistik['total_permainan']}")
    print(f"Menang          : {statistik['menang']}")
    print(f"Belum tertebak  : {statistik['menyerah']}")
    print(f"Total percobaan : {statistik['total_percobaan']}")
    print(f"Rata-rata coba  : {statistik['rata_percobaan']:.2f}")
    print(f"Skor terendah   : {statistik['skor_min']}")
    print(f"Skor tertinggi  : {statistik['skor_maks']}")

    terbaik = statistik["terbaik"]
    if terbaik:
        print(f"Rekor terbaik   : {terbaik['nama']} ({terbaik['percobaan']} percobaan)")

    print("\nPapan skor:")
    for nomor, item in enumerate(statistik["papan_skor"], start=1):
        print(f"{nomor}. {item['nama']} - {item['skor']} poin")

    total_hadiah = statistik["total_hadiah"]
    print(f"Total hadiah terkumpul: {fp.format_rupiah(total_hadiah)}")
    print(f"\nRiwayat per halaman ({UKURAN_HALAMAN} data):")

    for nomor, bagian in enumerate(statistik["halaman_riwayat"], start=1):
        ringkas = fp.ubah_data(
            lambda item: f"{item['nama']}:{item['status']}", bagian
        )
        print(f"Halaman {nomor}: {', '.join(ringkas)}")

    if statistik["frekuensi_tebakan"]:
        angka, jumlah = statistik["frekuensi_tebakan"][0]
        print(f"Angka tebakan paling sering muncul: {angka} ({jumlah} kali)")


# --------------------------------------------------------------------------
# Alur permainan
# --------------------------------------------------------------------------
def main() -> None:
    riwayat: Tuple[Rekor, ...] = ()
    print("====================================")
    print("       GAME TEBAK ANGKA 1-100       ")
    print("====================================")
    print(f"Tebak angka rahasia dari {ANGKA_MIN} sampai {ANGKA_MAKS}.")
    print("Ketik 'keluar' atau 'q' saat diminta angka untuk berhenti menebak.\n")

    try:
        while True:
            nama = fp.bersih_teks(input("Nama pemain: ")) or "pemain"
            rahasia = random.randint(ANGKA_MIN, ANGKA_MAKS)
            tebakan: Tuple[int, ...] = ()
            status = MENYERAH
            print(f"\nSaya sudah memilih angka. Kamu punya {BATAS_TEBAKAN} kesempatan!")

            for _ in range(BATAS_TEBAKAN):
                angka = minta_angka(f"Tebakan ke-{len(tebakan) + 1}: ")
                if angka is None:
                    break

                tebakan += (angka,)
                if angka == rahasia:
                    print(f"Benar! Angka rahasianya {rahasia}.")
                    status = MENANG
                    break

                print("Terlalu kecil!" if angka < rahasia else "Terlalu besar!")
                print(f"Sisa kesempatan: {BATAS_TEBAKAN - len(tebakan)}")

            if status == MENYERAH:
                print(f"Permainan selesai. Angka rahasianya adalah {rahasia}.")

            rekor = buat_rekor(nama, status, tebakan)
            riwayat += (rekor,)
            print(
                f"Skor ronde: {rekor['skor']} poin | "
                f"Hadiah: {fp.format_rupiah(rekor['hadiah'])}"
            )

            lagi = fp.bersih_teks(input("Main lagi? (y/n): "))
            if lagi not in {"y", "ya", "yes"}:
                break
            print()
    except (EOFError, KeyboardInterrupt):
        print("\nInput dihentikan. Aplikasi ditutup.")

    tampilkan_statistik(riwayat)
    print("\nTerima kasih sudah bermain!")


# --------------------------------------------------------------------------
# Titik masuk
# --------------------------------------------------------------------------
if __name__ == "__main__":
    main()
