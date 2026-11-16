from __future__ import annotations

from functools import reduce
from operator import add
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

__all__ = [
    "alur_proses",
    "filter_data",
    "ubah_data",
    "cari_item",
    "urut_data",
    "kelompok_data",
    "total_nilai",
    "rerata_nilai",
    "nilai_ekstrem",
    "cek_valid",
    "format_rupiah",
    "bersih_teks",
    "potong_data",
    "hitung_frekuensi",
    "gabung_rekursif",
]


def alur_proses(*fungsi: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Menyusun beberapa fungsi menjadi satu alur (pipeline) kiri ke kanan.

    Fungsi pertama menerima nilai awal, hasilnya dioper ke fungsi kedua,
    dan seterusnya. Tanpa argumen, hasilnya adalah fungsi identitas.

    Args:
        *fungsi: Fungsi-fungsi satu-argumen yang akan dirangkai berurutan.

    Returns:
        Fungsi baru yang menerima satu nilai dan menjalankan seluruh alur.

    Contoh:
        >>> alur_proses(lambda x: x + 1, lambda x: x * 2)(3)
        8
    """
    return lambda nilai: reduce(lambda hasil, f: f(hasil), fungsi, nilai)


def filter_data(predikat: Callable[[Any], bool], data: Iterable[Any]) -> List[Any]:
    """Menyaring data: hanya elemen yang memenuhi ``predikat`` yang dipertahankan.

    Args:
        predikat: Fungsi yang mengembalikan True jika elemen dipertahankan.
        data: Kumpulan data yang diiterasi (list, tuple, dsb.).

    Returns:
        List baru berisi elemen yang lolos saringan (urutan asli terjaga).

    Contoh:
        >>> filter_data(lambda x: x % 2 == 0, [1, 2, 3, 4])
        [2, 4]
    """
    return list(filter(predikat, data))


def ubah_data(fungsi: Callable[[Any], Any], data: Iterable[Any]) -> List[Any]:
    """Mengubah (transformasi) setiap elemen data dengan ``fungsi`` (map).

    Args:
        fungsi: Fungsi satu-argumen yang diterapkan pada tiap elemen.
        data: Kumpulan data yang diiterasi.

    Returns:
        List baru berisi hasil penerapan ``fungsi`` pada tiap elemen.

    Contoh:
        >>> ubah_data(lambda x: x * x, [1, 2, 3])
        [1, 4, 9]
    """
    return list(map(fungsi, data))


def cari_item(
    predikat: Callable[[Any], bool],
    data: Iterable[Any],
    bawaan: Optional[Any] = None,
) -> Optional[Any]:
    """Mencari elemen pertama yang memenuhi ``predikat``.

    Args:
        predikat: Fungsi yang mengembalikan True untuk elemen yang dicari.
        data: Kumpulan data yang diiterasi.
        bawaan: Nilai yang dikembalikan bila tidak ada elemen yang cocok.

    Returns:
        Elemen pertama yang cocok, atau ``bawaan`` (default ``None``).

    Contoh:
        >>> cari_item(lambda x: x > 2, [1, 2, 3, 4])
        3
        >>> cari_item(lambda x: x > 9, [1, 2, 3], bawaan=-1)
        -1
    """
    return next(filter(predikat, data), bawaan)


def urut_data(
    data: Iterable[Any],
    kunci: Optional[Callable[[Any], Any]] = None,
    terbalik: bool = False,
) -> List[Any]:
    """Mengurutkan data tanpa mengubah data asli.

    Args:
        data: Kumpulan data yang akan diurutkan.
        kunci: Fungsi pengambil kunci pembanding (opsional).
        terbalik: Jika True, urutan menurun (descending).

    Returns:
        List baru yang sudah terurut.

    Contoh:
        >>> urut_data([3, 1, 2])
        [1, 2, 3]
        >>> urut_data(["aa", "b", "ccc"], kunci=len, terbalik=True)
        ['ccc', 'aa', 'b']
    """
    return sorted(data, key=kunci, reverse=terbalik)


def kelompok_data(
    fungsi_kunci: Callable[[Any], Any], data: Iterable[Any]
) -> Dict[Any, List[Any]]:
    """Mengelompokkan elemen berdasarkan hasil ``fungsi_kunci`` (group by).

    Dibangun dengan ``reduce``; setiap langkah membuat dict baru sehingga
    tidak ada mutasi data.

    Args:
        fungsi_kunci: Fungsi yang menentukan kunci kelompok tiap elemen.
        data: Kumpulan data yang akan dikelompokkan.

    Returns:
        Dict ``{kunci: [elemen, ...]}`` dengan urutan kemunculan terjaga.

    Contoh:
        >>> kelompok_data(len, ["a", "bb", "c", "dd"])
        {1: ['a', 'c'], 2: ['bb', 'dd']}
    """

    def tambah(hasil: Dict[Any, List[Any]], item: Any) -> Dict[Any, List[Any]]:
        kunci = fungsi_kunci(item)
        return {**hasil, kunci: [*hasil.get(kunci, []), item]}

    return reduce(tambah, data, {})


def total_nilai(data: Iterable[Any], awal: Any = 0) -> Any:
    """Menjumlahkan seluruh elemen (fold/reduce dengan operator tambah).

    Args:
        data: Kumpulan nilai yang dijumlahkan.
        awal: Nilai awal akumulator (default 0).

    Returns:
        Jumlah semua elemen ditambah ``awal``; ``awal`` bila data kosong.

    Contoh:
        >>> total_nilai([1, 2, 3, 4])
        10
        >>> total_nilai([])
        0
    """
    return reduce(add, data, awal)


def rerata_nilai(data: Iterable[float]) -> float:
    """Menghitung rata-rata aritmetika.

    Args:
        data: Kumpulan nilai numerik.

    Returns:
        Rata-rata sebagai float; ``0.0`` bila data kosong.

    Contoh:
        >>> rerata_nilai([2, 4, 6])
        4.0
        >>> rerata_nilai([])
        0.0
    """
    nilai = tuple(data)
    return total_nilai(nilai) / len(nilai) if nilai else 0.0


def nilai_ekstrem(
    data: Iterable[Any], kunci: Optional[Callable[[Any], Any]] = None
) -> Tuple[Any, Any]:
    """Mencari nilai terkecil dan terbesar sekaligus.

    Args:
        data: Kumpulan data yang dapat dibandingkan.
        kunci: Fungsi pengambil kunci pembanding (opsional).

    Returns:
        Tuple ``(minimum, maksimum)``; ``(None, None)`` bila data kosong.

    Contoh:
        >>> nilai_ekstrem([3, 1, 4, 1, 5])
        (1, 5)
        >>> nilai_ekstrem([])
        (None, None)
    """
    nilai = tuple(data)
    return (min(nilai, key=kunci), max(nilai, key=kunci)) if nilai else (None, None)


def cek_valid(
    predikat: Callable[[Any], bool], data: Iterable[Any], mode: str = "semua"
) -> bool:
    """Memeriksa apakah data memenuhi ``predikat``.

    Args:
        predikat: Fungsi yang mengembalikan True untuk elemen valid.
        data: Kumpulan data yang diperiksa.
        mode: ``"semua"`` (semua elemen harus valid) atau ``"ada"``
            (minimal satu elemen valid).

    Returns:
        bool. Untuk data kosong: ``"semua"`` -> True, ``"ada"`` -> False.

    Raises:
        ValueError: Jika ``mode`` bukan ``"semua"`` atau ``"ada"``.

    Contoh:
        >>> cek_valid(lambda x: x > 0, [1, 2, 3])
        True
        >>> cek_valid(lambda x: x > 2, [1, 2, 3], mode="ada")
        True
    """
    if mode == "semua":
        return all(map(predikat, data))
    if mode == "ada":
        return any(map(predikat, data))
    raise ValueError("mode harus 'semua' atau 'ada'")


def format_rupiah(angka: float) -> str:
    """Memformat angka menjadi mata uang Rupiah (pemisah ribuan titik).

    Angka desimal dibulatkan ke rupiah terdekat.

    Args:
        angka: Nilai numerik (int atau float, boleh negatif).

    Returns:
        String berformat, mis. ``"Rp1.500.000"`` atau ``"-Rp2.500"``.

    Contoh:
        >>> format_rupiah(1500000)
        'Rp1.500.000'
        >>> format_rupiah(-2500)
        '-Rp2.500'
    """
    bulat = int(round(abs(angka)))
    tanda = "-" if bulat and angka < 0 else ""
    return f"{tanda}Rp{bulat:,}".replace(",", ".")


def bersih_teks(teks: str, hapus_tanda_baca: bool = False) -> str:
    """Membersihkan teks: rapikan spasi dan ubah ke huruf kecil.

    Spasi di awal/akhir dibuang dan spasi/tab/baris-baru berulang
    dipadatkan menjadi satu spasi.

    Args:
        teks: Teks masukan.
        hapus_tanda_baca: Jika True, karakter selain huruf, angka, dan
            spasi dihapus.

    Returns:
        String baru yang sudah bersih.

    Contoh:
        >>> bersih_teks("  Halo,   DUNIA!  ")
        'halo, dunia!'
        >>> bersih_teks("  Halo,   DUNIA!  ", hapus_tanda_baca=True)
        'halo dunia'
    """
    dasar = (
        "".join(filter(lambda c: c.isalnum() or c.isspace(), teks))
        if hapus_tanda_baca
        else teks
    )
    return " ".join(dasar.split()).lower()


def potong_data(data: Iterable[Any], ukuran: int) -> List[List[Any]]:
    """Memotong data menjadi potongan-potongan (chunk) berukuran tetap.

    Args:
        data: Kumpulan data yang dipotong.
        ukuran: Banyak elemen maksimum per potongan (harus > 0).

    Returns:
        List berisi list potongan; potongan terakhir bisa lebih pendek.

    Raises:
        ValueError: Jika ``ukuran`` kurang dari atau sama dengan 0.

    Contoh:
        >>> potong_data([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    if ukuran <= 0:
        raise ValueError("ukuran harus lebih besar dari 0")
    urutan = tuple(data)
    return [list(urutan[i : i + ukuran]) for i in range(0, len(urutan), ukuran)]


def hitung_frekuensi(data: Iterable[Any]) -> Dict[Any, int]:
    """Menghitung frekuensi kemunculan tiap elemen.

    Args:
        data: Kumpulan elemen yang dapat di-hash.

    Returns:
        Dict ``{elemen: jumlah}`` dengan urutan kemunculan pertama terjaga.

    Contoh:
        >>> hitung_frekuensi(["a", "b", "a"])
        {'a': 2, 'b': 1}
    """
    return reduce(lambda hasil, item: {**hasil, item: hasil.get(item, 0) + 1}, data, {})


def gabung_rekursif(daftar: Iterable[Any]) -> List[Any]:
    """Meratakan list/tuple bersarang menjadi satu list datar secara rekursif.

    String tidak ikut diratakan (diperlakukan sebagai satu elemen).
    Kedalaman rekursi mengikuti kedalaman sarang, bukan panjang list.

    Args:
        daftar: List/tuple yang boleh berisi list/tuple lain di dalamnya.

    Returns:
        List datar baru dengan urutan elemen asli terjaga.

    Contoh:
        >>> gabung_rekursif([1, [2, [3, 4]], 5])
        [1, 2, 3, 4, 5]
    """
    return reduce(
        lambda hasil, item: hasil
        + (gabung_rekursif(item) if isinstance(item, (list, tuple)) else [item]),
        daftar,
        [],
    )
