from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Tuple

from fplib import (
    alur_proses,
    bersih_teks,
    cari_item,
    cek_valid,
    filter_data,
    format_rupiah,
    gabung_rekursif,
    hitung_frekuensi,
    kelompok_data,
    nilai_ekstrem,
    potong_data,
    rerata_nilai,
    total_nilai,
    ubah_data,
    urut_data,
)

# --------------------------------------------------------------------------
# Data & konstanta (tidak pernah dimutasi)
# --------------------------------------------------------------------------
KATALOG: Tuple[Dict[str, Any], ...] = (
    {"kode": "MK1", "nama": "Nasi Goreng", "kategori": "Makanan", "harga": 15000},
    {"kode": "MK2", "nama": "Mie Ayam", "kategori": "Makanan", "harga": 13000},
    {"kode": "MK3", "nama": "Soto Ayam", "kategori": "Makanan", "harga": 14000},
    {"kode": "MK4", "nama": "Nasi Pecel", "kategori": "Makanan", "harga": 12000},
    {"kode": "MN1", "nama": "Es Teh Manis", "kategori": "Minuman", "harga": 4000},
    {"kode": "MN2", "nama": "Es Jeruk", "kategori": "Minuman", "harga": 6000},
    {"kode": "MN3", "nama": "Kopi Hitam", "kategori": "Minuman", "harga": 5000},
    {"kode": "MN4", "nama": "Air Mineral", "kategori": "Minuman", "harga": 3000},
    {"kode": "MN5", "nama": "Jus Alpukat", "kategori": "Minuman", "harga": 12000},
    {"kode": "SN1", "nama": "Risoles", "kategori": "Snack", "harga": 3000},
    {"kode": "SN2", "nama": "Pisang Goreng", "kategori": "Snack", "harga": 2000},
    {"kode": "SN3", "nama": "Keripik Singkong", "kategori": "Snack", "harga": 5000},
    {"kode": "SN4", "nama": "Roti Bakar", "kategori": "Snack", "harga": 8000},
)

Keranjang = Tuple[Tuple[str, int], ...]  # ((kode, jumlah), ...)

LEBAR = 46
GARIS = "-" * LEBAR
MAKS_JUMLAH = 20
UKURAN_HALAMAN = 5
BATAS_ATAS = 10**9


# --------------------------------------------------------------------------
# Parsing & validasi input (fungsi murni)
# --------------------------------------------------------------------------
def _ke_bilangan(teks: str) -> Optional[int]:
    """Ubah string angka ASCII menjadi int; None jika bukan bilangan bulat >= 0."""
    return int(teks) if teks.isascii() and teks.isdigit() else None


parse_bilangan: Callable[[str], Optional[int]] = alur_proses(bersih_teks, _ke_bilangan)

parse_uang: Callable[[str], Optional[int]] = alur_proses(
    bersih_teks,
    lambda s: "".join(filter_data(lambda c: c != ".", s)),  # buang pemisah ribuan
    lambda s: s[2:] if s.startswith("rp") else s,  # buang awalan "Rp"
    str.strip,
    _ke_bilangan,
)


def parse_batas(teks: str, bawaan: int) -> Optional[int]:
    """Parse batas harga; teks kosong -> ``bawaan``; tidak valid -> None."""
    return bawaan if bersih_teks(teks) == "" else parse_uang(teks)


# --------------------------------------------------------------------------
# Katalog: tampilan, pencarian, penyaringan
# --------------------------------------------------------------------------
def baris_menu(menu: Dict[str, Any]) -> str:
    """Satu baris tabel katalog untuk sebuah menu."""
    return (
        f"{menu['kode']:<6}{menu['nama']:<20}{menu['kategori']:<10}"
        f"{format_rupiah(menu['harga']):>10}"
    )


def tabel_menu(daftar: Tuple[Dict[str, Any], ...] | List[Dict[str, Any]]) -> List[str]:
    """Tabel menu terurut (kategori, nama) + rentang harga (via nilai_ekstrem)."""
    if not daftar:
        return ["(tidak ada menu yang cocok)"]
    termurah, termahal = nilai_ekstrem(daftar, kunci=lambda m: m["harga"])
    urut = urut_data(daftar, kunci=lambda m: (m["kategori"], m["nama"]))
    return [
        f"{'KODE':<6}{'NAMA':<20}{'KATEGORI':<10}{'HARGA':>10}",
        GARIS,
        *ubah_data(baris_menu, urut),
        GARIS,
        f"{len(daftar)} menu | rentang harga "
        f"{format_rupiah(termurah['harga'])} - {format_rupiah(termahal['harga'])}",
    ]


def halaman_katalog(
    katalog: Tuple[Dict[str, Any], ...], halaman: int, ukuran: int = UKURAN_HALAMAN
) -> Optional[List[Dict[str, Any]]]:
    """Ambil menu pada halaman ke-``halaman`` (mulai 1) memakai potong_data.

    Mengembalikan None bila nomor halaman di luar jangkauan.
    """
    urut = urut_data(katalog, kunci=lambda m: (m["kategori"], m["nama"]))
    potongan = potong_data(urut, ukuran)
    return potongan[halaman - 1] if 1 <= halaman <= len(potongan) else None


def jumlah_halaman(katalog: Tuple[Dict[str, Any], ...], ukuran: int = UKURAN_HALAMAN) -> int:
    """Banyaknya halaman katalog."""
    return len(potong_data(katalog, ukuran))


def cari_menu(katalog: Tuple[Dict[str, Any], ...], kata_kunci: str) -> List[Dict[str, Any]]:
    """Cari menu yang namanya memuat ``kata_kunci`` (tanpa peduli huruf besar/spasi)."""
    kata = bersih_teks(kata_kunci)
    return filter_data(lambda m: kata in bersih_teks(m["nama"]), katalog)


def cari_menu_kode(katalog: Tuple[Dict[str, Any], ...], kode_teks: str) -> Optional[Dict[str, Any]]:
    """Cari satu menu berdasarkan kode (mis. ``" mk1 "`` -> menu MK1)."""
    kode = bersih_teks(kode_teks)
    return cari_item(lambda m: bersih_teks(m["kode"]) == kode, katalog)


def kategori_tersedia(katalog: Tuple[Dict[str, Any], ...]) -> List[str]:
    """Daftar kategori unik, terurut abjad."""
    return urut_data(kelompok_data(lambda m: m["kategori"], katalog))


def temukan_kategori(katalog: Tuple[Dict[str, Any], ...], masukan: str) -> Optional[str]:
    """Terjemahkan masukan (nama kategori atau nomor urut) menjadi nama kategori."""
    daftar = kategori_tersedia(katalog)
    nomor = parse_bilangan(masukan)
    berdasar_nomor = daftar[nomor - 1] if nomor is not None and 1 <= nomor <= len(daftar) else None
    berdasar_nama = cari_item(lambda k: bersih_teks(k) == bersih_teks(masukan), daftar)
    return berdasar_nomor or berdasar_nama


def saring_kategori(katalog: Tuple[Dict[str, Any], ...], kategori: str) -> List[Dict[str, Any]]:
    """Menu pada kategori tertentu."""
    return filter_data(lambda m: m["kategori"] == kategori, katalog)


def saring_harga(
    katalog: Tuple[Dict[str, Any], ...], minimum: int, maksimum: int
) -> List[Dict[str, Any]]:
    """Menu dengan harga di antara ``minimum`` dan ``maksimum`` (inklusif)."""
    return filter_data(lambda m: minimum <= m["harga"] <= maksimum, katalog)


# --------------------------------------------------------------------------
# Keranjang belanja (immutable): setiap fungsi mengembalikan keranjang baru
# --------------------------------------------------------------------------
def jumlah_item(keranjang: Keranjang) -> int:
    """Total porsi di dalam keranjang."""
    return total_nilai(ubah_data(lambda b: b[1], keranjang))


def tambah_ke_keranjang(
    keranjang: Keranjang,
    katalog: Tuple[Dict[str, Any], ...],
    kode_teks: str,
    jumlah_teks: str,
) -> Tuple[Keranjang, str]:
    """Tambahkan menu ke keranjang dengan validasi input.

    Returns:
        ``(keranjang_baru, pesan)``. Bila validasi gagal, keranjang dikembalikan
        apa adanya bersama pesan kesalahan.
    """
    menu = cari_menu_kode(katalog, kode_teks)
    jumlah = parse_bilangan(jumlah_teks)
    sudah = cari_item(
        lambda b: menu is not None and b[0] == menu["kode"], keranjang, bawaan=(None, 0)
    )[1]

    aturan = (
        (menu is not None, f"Kode '{bersih_teks(kode_teks).upper()}' tidak ada di katalog."),
        (jumlah is not None and jumlah >= 1, "Jumlah harus bilangan bulat positif."),
        (
            jumlah is not None and sudah + jumlah <= MAKS_JUMLAH,
            f"Maksimal {MAKS_JUMLAH} porsi per menu.",
        ),
    )
    gagal = cari_item(lambda a: not a[0], aturan)
    if gagal is not None:
        return keranjang, f"[!] {gagal[1]}"

    baru = (
        tuple(
            ubah_data(
                lambda b: (b[0], b[1] + jumlah) if b[0] == menu["kode"] else b, keranjang
            )
        )
        if sudah > 0
        else keranjang + ((menu["kode"], jumlah),)
    )
    return baru, f"[+] {jumlah} x {menu['nama']} ditambahkan ke keranjang."


def hapus_dari_keranjang(
    keranjang: Keranjang, katalog: Tuple[Dict[str, Any], ...], kode_teks: str
) -> Tuple[Keranjang, str]:
    """Hapus satu jenis menu dari keranjang. Mengembalikan ``(keranjang_baru, pesan)``."""
    menu = cari_menu_kode(katalog, kode_teks)
    ada = menu is not None and cari_item(lambda b: b[0] == menu["kode"], keranjang) is not None
    if not ada:
        return keranjang, "[!] Menu tersebut tidak ada di keranjang."
    baru = tuple(filter_data(lambda b: b[0] != menu["kode"], keranjang))
    return baru, f"[-] {menu['nama']} dihapus dari keranjang."


def rincian_keranjang(
    keranjang: Keranjang, katalog: Tuple[Dict[str, Any], ...]
) -> List[Dict[str, Any]]:
    """Gabungkan keranjang dengan data katalog -> daftar rincian + subtotal."""
    pasangan = ubah_data(lambda b: (cari_menu_kode(katalog, b[0]), b[1]), keranjang)
    valid = filter_data(lambda p: p[0] is not None, pasangan)
    return ubah_data(lambda p: {**p[0], "jumlah": p[1], "subtotal": p[0]["harga"] * p[1]}, valid)


# --------------------------------------------------------------------------
# Perhitungan & struk
# --------------------------------------------------------------------------
def statistik_keranjang(rincian: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Hitung total, rata-rata harga per porsi, rekap kategori, dan ekstrem harga."""
    subtotal = lambda r: r["subtotal"]  # noqa: E731
    per_porsi = gabung_rekursif(ubah_data(lambda r: [r["harga"]] * r["jumlah"], rincian))
    kategori_porsi = gabung_rekursif(ubah_data(lambda r: [r["kategori"]] * r["jumlah"], rincian))
    termurah, termahal = nilai_ekstrem(rincian, kunci=lambda r: r["harga"])
    return {
        "porsi": total_nilai(ubah_data(lambda r: r["jumlah"], rincian)),
        "jenis": len(rincian),
        "total": total_nilai(ubah_data(subtotal, rincian)),
        "rerata_harga": rerata_nilai(per_porsi),
        "per_kategori": dict(
            ubah_data(
                lambda kv: (kv[0], total_nilai(ubah_data(subtotal, kv[1]))),
                kelompok_data(lambda r: r["kategori"], rincian).items(),
            )
        ),
        "frekuensi_kategori": hitung_frekuensi(kategori_porsi),
        "termurah": termurah,
        "termahal": termahal,
    }


def _baris_kv(label: str, nilai: str) -> str:
    return f"{label:<{LEBAR - 18}}{nilai:>18}"


def baris_rincian(r: Dict[str, Any]) -> str:
    """Satu baris rincian belanja: nama, qty x harga, subtotal."""
    return (
        f"{r['nama']:<18}{r['jumlah']:>3} x {format_rupiah(r['harga']):>9}"
        f"{format_rupiah(r['subtotal']):>14}"
    )


def tabel_keranjang(rincian: List[Dict[str, Any]]) -> List[str]:
    """Tampilan isi keranjang beserta total sementara."""
    if not rincian:
        return ["Keranjang masih kosong."]
    s = statistik_keranjang(rincian)
    return [
        GARIS,
        *ubah_data(baris_rincian, urut_data(rincian, kunci=lambda r: r["nama"])),
        GARIS,
        _baris_kv(f"TOTAL ({s['porsi']} porsi)", format_rupiah(s["total"])),
    ]


def susun_struk(rincian: List[Dict[str, Any]], bayar: int, waktu: str) -> List[str]:
    """Susun struk pembayaran lengkap sebagai daftar baris teks."""
    s = statistik_keranjang(rincian)
    kategori_terbanyak = nilai_ekstrem(
        s["frekuensi_kategori"].items(), kunci=lambda kv: kv[1]
    )[1]
    rekap_kategori = ubah_data(
        lambda kv: _baris_kv(f"  {kv[0]}", format_rupiah(kv[1])),
        urut_data(s["per_kategori"].items()),
    )
    return [
        "=" * LEBAR,
        "KANTIN INFORMATIKA UMM".center(LEBAR),
        waktu.center(LEBAR),
        "=" * LEBAR,
        *ubah_data(baris_rincian, urut_data(rincian, kunci=lambda r: r["nama"])),
        GARIS,
        _baris_kv("Jenis menu", str(s["jenis"])),
        _baris_kv("Jumlah porsi", str(s["porsi"])),
        _baris_kv("Rata-rata harga/porsi", format_rupiah(s["rerata_harga"])),
        _baris_kv("Termurah", s["termurah"]["nama"]),
        _baris_kv("Termahal", s["termahal"]["nama"]),
        _baris_kv(
            "Kategori terbanyak",
            f"{kategori_terbanyak[0]} ({kategori_terbanyak[1]} porsi)",
        ),
        "Rekap per kategori:",
        *rekap_kategori,
        GARIS,
        _baris_kv("TOTAL", format_rupiah(s["total"])),
        _baris_kv("BAYAR", format_rupiah(bayar)),
        _baris_kv("KEMBALI", format_rupiah(bayar - s["total"])),
        "=" * LEBAR,
        "Terima kasih, selamat menikmati!".center(LEBAR),
    ]


# --------------------------------------------------------------------------
# Lapisan I/O: konteks + aksi menu. Setiap aksi: (keranjang, ctx) -> keranjang baru
# --------------------------------------------------------------------------
class Konteks(NamedTuple):
    """Dependensi I/O yang disuntikkan (immutable)."""

    katalog: Tuple[Dict[str, Any], ...]
    ambil: Callable[[str], str]
    tulis: Callable[[str], None]
    sekarang: Callable[[], str]


def cetak(tulis: Callable[[str], None], baris: List[str]) -> None:
    """Tulis banyak baris sekaligus (satu-satunya tempat efek samping keluaran)."""
    ubah_data(tulis, baris)


def aksi_lihat_katalog(keranjang: Keranjang, ctx: Konteks) -> Keranjang:
    total_hal = jumlah_halaman(ctx.katalog)
    teks = ctx.ambil(f"Halaman 1-{total_hal} (Enter = 1): ")
    halaman = 1 if bersih_teks(teks) == "" else parse_bilangan(teks)
    isi = halaman_katalog(ctx.katalog, halaman) if halaman is not None else None
    if isi is None:
        cetak(ctx.tulis, [f"[!] Halaman harus berupa angka 1-{total_hal}."])
    else:
        cetak(ctx.tulis, [*tabel_menu(isi), f"Halaman {halaman}/{total_hal}"])
    return keranjang


def aksi_cari(keranjang: Keranjang, ctx: Konteks) -> Keranjang:
    kata = ctx.ambil("Kata kunci nama menu: ")
    if bersih_teks(kata) == "":
        cetak(ctx.tulis, ["[!] Kata kunci tidak boleh kosong."])
    else:
        cetak(ctx.tulis, tabel_menu(cari_menu(ctx.katalog, kata)))
    return keranjang


def aksi_filter_kategori(keranjang: Keranjang, ctx: Konteks) -> Keranjang:
    daftar = kategori_tersedia(ctx.katalog)
    cetak(ctx.tulis, [f"  {i}. {k}" for i, k in enumerate(daftar, start=1)])
    kategori = temukan_kategori(ctx.katalog, ctx.ambil("Pilih kategori (nama/nomor): "))
    if kategori is None:
        cetak(ctx.tulis, ["[!] Kategori tidak dikenal."])
    else:
        cetak(ctx.tulis, tabel_menu(saring_kategori(ctx.katalog, kategori)))
    return keranjang


def aksi_filter_harga(keranjang: Keranjang, ctx: Konteks) -> Keranjang:
    bawah = parse_batas(ctx.ambil("Harga minimum (Enter = tanpa batas): "), 0)
    atas = parse_batas(ctx.ambil("Harga maksimum (Enter = tanpa batas): "), BATAS_ATAS)
    if not cek_valid(lambda x: x is not None, [bawah, atas]):
        cetak(ctx.tulis, ["[!] Nominal harus berupa angka (contoh: 5000 atau Rp 5.000)."])
    elif bawah > atas:
        cetak(ctx.tulis, ["[!] Harga minimum tidak boleh lebih besar dari maksimum."])
    else:
        cetak(ctx.tulis, tabel_menu(saring_harga(ctx.katalog, bawah, atas)))
    return keranjang


def aksi_tambah(keranjang: Keranjang, ctx: Konteks) -> Keranjang:
    kode = ctx.ambil("Kode menu (mis. MK1): ")
    jumlah = ctx.ambil("Jumlah: ")
    baru, pesan = tambah_ke_keranjang(keranjang, ctx.katalog, kode, jumlah)
    cetak(ctx.tulis, [pesan])
    return baru


def aksi_hapus(keranjang: Keranjang, ctx: Konteks) -> Keranjang:
    baru, pesan = hapus_dari_keranjang(keranjang, ctx.katalog, ctx.ambil("Kode menu yang dihapus: "))
    cetak(ctx.tulis, [pesan])
    return baru


def aksi_lihat_keranjang(keranjang: Keranjang, ctx: Konteks) -> Keranjang:
    cetak(ctx.tulis, tabel_keranjang(rincian_keranjang(keranjang, ctx.katalog)))
    return keranjang


def aksi_bayar(keranjang: Keranjang, ctx: Konteks) -> Keranjang:
    if not keranjang:
        cetak(ctx.tulis, ["[!] Keranjang kosong, tidak ada yang dibayar."])
        return keranjang
    rincian = rincian_keranjang(keranjang, ctx.katalog)
    total = statistik_keranjang(rincian)["total"]
    cetak(ctx.tulis, tabel_keranjang(rincian))
    bayar = parse_uang(ctx.ambil("Uang bayar: "))
    if bayar is None:
        cetak(ctx.tulis, ["[!] Nominal tidak valid. Pembayaran dibatalkan."])
        return keranjang
    if bayar < total:
        cetak(ctx.tulis, [f"[!] Uang kurang {format_rupiah(total - bayar)}. Pembayaran dibatalkan."])
        return keranjang
    cetak(ctx.tulis, ["", *susun_struk(rincian, bayar, ctx.sekarang())])
    return ()  # transaksi selesai -> keranjang baru yang kosong


DAFTAR_PERINTAH = (
    ("1", "Lihat katalog menu", aksi_lihat_katalog),
    ("2", "Cari menu (nama)", aksi_cari),
    ("3", "Saring menu per kategori", aksi_filter_kategori),
    ("4", "Saring menu per rentang harga", aksi_filter_harga),
    ("5", "Tambah item ke keranjang", aksi_tambah),
    ("6", "Hapus item dari keranjang", aksi_hapus),
    ("7", "Lihat keranjang", aksi_lihat_keranjang),
    ("8", "Bayar & cetak struk", aksi_bayar),
)


def teks_menu(keranjang: Keranjang) -> List[str]:
    """Teks menu utama; menampilkan jumlah porsi pada keranjang saat ini."""
    return [
        "",
        "=== KASIR KANTIN INFORMATIKA UMM ===",
        *ubah_data(lambda p: f"  {p[0]}. {p[1]}", DAFTAR_PERINTAH),
        "  0. Keluar",
        f"[Keranjang: {jumlah_item(keranjang)} porsi]",
    ]


def jalankan(ctx: Konteks, keranjang: Keranjang = ()) -> Keranjang:
    """Loop utama. ``kini`` hanya di-rebind ke keranjang baru, tidak pernah dimutasi."""
    kini = keranjang
    try:
        while True:
            cetak(ctx.tulis, teks_menu(kini))
            pilihan = bersih_teks(ctx.ambil("Pilih menu: "))
            if pilihan == "0":
                break
            perintah = cari_item(lambda p: p[0] == pilihan, DAFTAR_PERINTAH)
            if perintah is None:
                cetak(ctx.tulis, ["[!] Pilihan tidak dikenal, masukkan angka 0-8."])
                continue
            kini = perintah[2](kini, ctx)
    except (EOFError, KeyboardInterrupt):
        pass
    cetak(ctx.tulis, ["", "Terima kasih telah menggunakan aplikasi kasir."])
    return kini


def main() -> None:
    """Titik masuk program: rangkai konteks I/O nyata lalu jalankan aplikasi."""
    jalankan(
        Konteks(
            katalog=KATALOG,
            ambil=input,
            tulis=print,
            sekarang=lambda: datetime.now().strftime("%d-%m-%Y %H:%M"),
        )
    )


if __name__ == "__main__":
    main()
