"""Unit test untuk fplib.py menggunakan pytest.

Jalankan dengan:  pytest -v
"""

import pytest

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


# --------------------------------------------------------------- alur_proses
class TestAlurProses:
    def test_urutan_kiri_ke_kanan(self):
        alur = alur_proses(lambda x: x + 1, lambda x: x * 2)
        assert alur(3) == 8  # (3 + 1) * 2, bukan 3 * 2 + 1

    def test_satu_fungsi(self):
        assert alur_proses(str.upper)("abc") == "ABC"

    def test_tanpa_fungsi_adalah_identitas(self):
        assert alur_proses()(42) == 42

    def test_alur_dapat_dipakai_ulang(self):
        alur = alur_proses(lambda x: x + 1)
        assert alur(1) == 2
        assert alur(10) == 11

    def test_dengan_fungsi_lain_di_fplib(self):
        alur = alur_proses(
            lambda xs: filter_data(lambda x: x > 1, xs),
            lambda xs: ubah_data(lambda x: x * 10, xs),
            total_nilai,
        )
        assert alur([1, 2, 3]) == 50


# --------------------------------------------------------------- filter_data
class TestFilterData:
    def test_normal(self):
        assert filter_data(lambda x: x % 2 == 0, [1, 2, 3, 4]) == [2, 4]

    def test_tidak_ada_yang_lolos(self):
        assert filter_data(lambda x: x > 10, [1, 2, 3]) == []

    def test_semua_lolos(self):
        assert filter_data(lambda x: True, [1, 2]) == [1, 2]

    def test_list_kosong(self):
        assert filter_data(lambda x: True, []) == []

    def test_tidak_memutasi_input(self):
        asli = [1, 2, 3, 4]
        filter_data(lambda x: x > 2, asli)
        assert asli == [1, 2, 3, 4]

    def test_menerima_tuple_dan_generator(self):
        assert filter_data(lambda x: x > 1, (1, 2, 3)) == [2, 3]
        assert filter_data(lambda x: x > 1, (i for i in range(4))) == [2, 3]


# ----------------------------------------------------------------- ubah_data
class TestUbahData:
    def test_normal(self):
        assert ubah_data(lambda x: x * x, [1, 2, 3]) == [1, 4, 9]

    def test_ubah_tipe(self):
        assert ubah_data(str, [1, 2]) == ["1", "2"]

    def test_list_kosong(self):
        assert ubah_data(lambda x: x, []) == []

    def test_tidak_memutasi_input(self):
        asli = [1, 2, 3]
        ubah_data(lambda x: x + 1, asli)
        assert asli == [1, 2, 3]


# ----------------------------------------------------------------- cari_item
class TestCariItem:
    def test_menemukan_item_pertama(self):
        assert cari_item(lambda x: x > 2, [1, 2, 3, 4]) == 3

    def test_tidak_ditemukan_mengembalikan_none(self):
        assert cari_item(lambda x: x > 9, [1, 2, 3]) is None

    def test_nilai_bawaan(self):
        assert cari_item(lambda x: x > 9, [1, 2, 3], bawaan=-1) == -1

    def test_list_kosong(self):
        assert cari_item(lambda x: True, []) is None
        assert cari_item(lambda x: True, [], bawaan="kosong") == "kosong"

    def test_item_falsy_tetap_ditemukan(self):
        assert cari_item(lambda x: x == 0, [5, 0, 7], bawaan=-1) == 0


# ----------------------------------------------------------------- urut_data
class TestUrutData:
    def test_naik_default(self):
        assert urut_data([3, 1, 2]) == [1, 2, 3]

    def test_terbalik(self):
        assert urut_data([3, 1, 2], terbalik=True) == [3, 2, 1]

    def test_dengan_kunci(self):
        assert urut_data(["aa", "b", "ccc"], kunci=len) == ["b", "aa", "ccc"]

    def test_kunci_dan_terbalik(self):
        assert urut_data(["aa", "b", "ccc"], kunci=len, terbalik=True) == [
            "ccc",
            "aa",
            "b",
        ]

    def test_list_kosong(self):
        assert urut_data([]) == []

    def test_satu_elemen(self):
        assert urut_data([7]) == [7]

    def test_tidak_memutasi_input(self):
        asli = [3, 1, 2]
        hasil = urut_data(asli)
        assert asli == [3, 1, 2]
        assert hasil is not asli

    def test_stabil_untuk_kunci_sama(self):
        data = [("a", 1), ("b", 1), ("c", 0)]
        assert urut_data(data, kunci=lambda t: t[1]) == [("c", 0), ("a", 1), ("b", 1)]


# ------------------------------------------------------------- kelompok_data
class TestKelompokData:
    def test_normal(self):
        assert kelompok_data(len, ["a", "bb", "c", "dd"]) == {
            1: ["a", "c"],
            2: ["bb", "dd"],
        }

    def test_kunci_genap_ganjil(self):
        assert kelompok_data(lambda x: x % 2, [1, 2, 3, 4, 5]) == {
            1: [1, 3, 5],
            0: [2, 4],
        }

    def test_satu_kelompok(self):
        assert kelompok_data(lambda x: "x", [1, 2, 3]) == {"x": [1, 2, 3]}

    def test_list_kosong(self):
        assert kelompok_data(len, []) == {}

    def test_urutan_kemunculan_terjaga(self):
        hasil = kelompok_data(lambda x: x % 3, [3, 1, 2, 4])
        assert list(hasil.keys()) == [0, 1, 2]
        assert hasil[1] == [1, 4]

    def test_tidak_memutasi_input(self):
        asli = ["a", "bb"]
        kelompok_data(len, asli)
        assert asli == ["a", "bb"]


# --------------------------------------------------------------- total_nilai
class TestTotalNilai:
    def test_normal(self):
        assert total_nilai([1, 2, 3, 4]) == 10

    def test_list_kosong_adalah_nol(self):
        assert total_nilai([]) == 0

    def test_dengan_nilai_awal(self):
        assert total_nilai([1, 2], awal=10) == 13
        assert total_nilai([], awal=5) == 5

    def test_bilangan_negatif_dan_float(self):
        assert total_nilai([-1, 1.5, 2.5]) == 3.0

    def test_menjumlah_string_dengan_awal(self):
        assert total_nilai(["a", "b", "c"], awal="") == "abc"


# -------------------------------------------------------------- rerata_nilai
class TestRerataNilai:
    def test_normal(self):
        assert rerata_nilai([2, 4, 6]) == 4.0

    def test_hasil_pecahan(self):
        assert rerata_nilai([1, 2]) == 1.5

    def test_satu_elemen(self):
        assert rerata_nilai([5]) == 5.0

    def test_list_kosong(self):
        assert rerata_nilai([]) == 0.0

    def test_bilangan_negatif(self):
        assert rerata_nilai([-2, 2]) == 0.0

    def test_menerima_generator(self):
        assert rerata_nilai(x for x in [1, 2, 3]) == 2.0


# ------------------------------------------------------------- nilai_ekstrem
class TestNilaiEkstrem:
    def test_normal(self):
        assert nilai_ekstrem([3, 1, 4, 1, 5]) == (1, 5)

    def test_satu_elemen(self):
        assert nilai_ekstrem([9]) == (9, 9)

    def test_list_kosong(self):
        assert nilai_ekstrem([]) == (None, None)

    def test_dengan_kunci(self):
        assert nilai_ekstrem(["aa", "b", "cccc"], kunci=len) == ("b", "cccc")

    def test_bilangan_negatif(self):
        assert nilai_ekstrem([-5, -1, -9]) == (-9, -1)

    def test_menerima_generator(self):
        assert nilai_ekstrem(x for x in [2, 8, 4]) == (2, 8)


# ----------------------------------------------------------------- cek_valid
class TestCekValid:
    def test_semua_valid(self):
        assert cek_valid(lambda x: x > 0, [1, 2, 3]) is True

    def test_semua_tidak_valid_jika_ada_yang_gagal(self):
        assert cek_valid(lambda x: x > 0, [1, -2, 3]) is False

    def test_mode_ada_true(self):
        assert cek_valid(lambda x: x > 2, [1, 2, 3], mode="ada") is True

    def test_mode_ada_false(self):
        assert cek_valid(lambda x: x > 5, [1, 2, 3], mode="ada") is False

    def test_list_kosong_mode_semua_true(self):
        assert cek_valid(lambda x: False, []) is True

    def test_list_kosong_mode_ada_false(self):
        assert cek_valid(lambda x: True, [], mode="ada") is False

    def test_mode_tidak_dikenal(self):
        with pytest.raises(ValueError):
            cek_valid(lambda x: True, [1], mode="lainnya")


# ------------------------------------------------------------- format_rupiah
class TestFormatRupiah:
    def test_ribuan(self):
        assert format_rupiah(1500) == "Rp1.500"

    def test_jutaan(self):
        assert format_rupiah(1500000) == "Rp1.500.000"

    def test_di_bawah_seribu(self):
        assert format_rupiah(999) == "Rp999"

    def test_nol(self):
        assert format_rupiah(0) == "Rp0"

    def test_negatif(self):
        assert format_rupiah(-2500) == "-Rp2.500"

    def test_float_dibulatkan(self):
        assert format_rupiah(1234.6) == "Rp1.235"
        assert format_rupiah(1234.2) == "Rp1.234"

    def test_negatif_kecil_menjadi_nol_tanpa_tanda(self):
        assert format_rupiah(-0.2) == "Rp0"

    def test_miliaran(self):
        assert format_rupiah(1234567890) == "Rp1.234.567.890"


# --------------------------------------------------------------- bersih_teks
class TestBersihTeks:
    def test_trim_spasi_dan_huruf_kecil(self):
        assert bersih_teks("  Halo DUNIA  ") == "halo dunia"

    def test_spasi_berulang_dipadatkan(self):
        assert bersih_teks("a    b \t\n c") == "a b c"

    def test_tanda_baca_dipertahankan_secara_default(self):
        assert bersih_teks("  Halo,   DUNIA!  ") == "halo, dunia!"

    def test_hapus_tanda_baca(self):
        assert bersih_teks("  Halo,   DUNIA!  ", hapus_tanda_baca=True) == "halo dunia"

    def test_string_kosong(self):
        assert bersih_teks("") == ""

    def test_hanya_spasi(self):
        assert bersih_teks("   \t  ") == ""

    def test_angka_tetap_ada(self):
        assert bersih_teks(" ABC-123 ", hapus_tanda_baca=True) == "abc123"


# --------------------------------------------------------------- potong_data
class TestPotongData:
    def test_normal_dengan_sisa(self):
        assert potong_data([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]

    def test_habis_dibagi(self):
        assert potong_data([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]

    def test_ukuran_lebih_besar_dari_data(self):
        assert potong_data([1, 2], 10) == [[1, 2]]

    def test_ukuran_satu(self):
        assert potong_data([1, 2, 3], 1) == [[1], [2], [3]]

    def test_list_kosong(self):
        assert potong_data([], 3) == []

    @pytest.mark.parametrize("ukuran", [0, -1, -10])
    def test_ukuran_tidak_valid(self, ukuran):
        with pytest.raises(ValueError):
            potong_data([1, 2, 3], ukuran)

    def test_tidak_memutasi_input(self):
        asli = [1, 2, 3]
        potong_data(asli, 2)
        assert asli == [1, 2, 3]

    def test_menerima_string(self):
        assert potong_data("abcde", 2) == [["a", "b"], ["c", "d"], ["e"]]


# ---------------------------------------------------------- hitung_frekuensi
class TestHitungFrekuensi:
    def test_normal(self):
        assert hitung_frekuensi(["a", "b", "a"]) == {"a": 2, "b": 1}

    def test_semua_sama(self):
        assert hitung_frekuensi([1, 1, 1]) == {1: 3}

    def test_semua_unik(self):
        assert hitung_frekuensi([1, 2, 3]) == {1: 1, 2: 1, 3: 1}

    def test_list_kosong(self):
        assert hitung_frekuensi([]) == {}

    def test_string_sebagai_iterable(self):
        assert hitung_frekuensi("aab") == {"a": 2, "b": 1}

    def test_urutan_kemunculan_pertama_terjaga(self):
        assert list(hitung_frekuensi(["b", "a", "b"]).keys()) == ["b", "a"]

    def test_tidak_memutasi_input(self):
        asli = ["a", "b", "a"]
        hitung_frekuensi(asli)
        assert asli == ["a", "b", "a"]


# --------------------------------------------------------- gabung_rekursif
class TestGabungRekursif:
    def test_satu_tingkat(self):
        assert gabung_rekursif([[1, 2], [3]]) == [1, 2, 3]

    def test_bersarang_dalam(self):
        assert gabung_rekursif([1, [2, [3, [4]]], 5]) == [1, 2, 3, 4, 5]

    def test_sudah_datar(self):
        assert gabung_rekursif([1, 2, 3]) == [1, 2, 3]

    def test_list_kosong(self):
        assert gabung_rekursif([]) == []

    def test_sarang_kosong(self):
        assert gabung_rekursif([[], [[]], []]) == []

    def test_tuple_ikut_diratakan(self):
        assert gabung_rekursif([1, (2, 3), [4]]) == [1, 2, 3, 4]

    def test_string_tidak_diratakan(self):
        assert gabung_rekursif(["ab", ["cd"]]) == ["ab", "cd"]

    def test_list_datar_panjang_tidak_overflow(self):
        data = list(range(5000))
        assert gabung_rekursif(data) == data

    def test_tidak_memutasi_input(self):
        asli = [1, [2, 3]]
        gabung_rekursif(asli)
        assert asli == [1, [2, 3]]
