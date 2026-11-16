# fplib — Pustaka Utilitas Pemrograman Fungsional

Tugas Mata Kuliah **Pemrograman Fungsional** — Informatika, Universitas Muhammadiyah Malang (UMM).

`fplib.py` berisi **15 fungsi utilitas umum** yang ditulis dengan gaya pemrograman fungsional:

- **Pure function** — hasil hanya bergantung pada argumen, tanpa side-effect.
- **Tanpa mutasi** — data masukan tidak pernah diubah; setiap fungsi mengembalikan data baru.
- Memanfaatkan **higher-order function**, **lambda**, **`functools.reduce`**, dan **rekursi**.

## Struktur Repositori

```
.
├── fplib.py         # pustaka berisi 15 fungsi
├── test_fplib.py    # unit test pytest
└── README.md        # dokumentasi ini
```

## Persyaratan

- Python 3.8 atau lebih baru
- `pytest` (hanya untuk menjalankan test; `fplib.py` sendiri tidak butuh library eksternal)

## Instalasi & Menjalankan Test

```bash
# 1. Clone repositori
git clone <url-repositori-kelompok>
cd <nama-folder-repositori>

# 2. (Opsional) buat virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Pasang pytest
pip install pytest

# 4. Jalankan seluruh test
pytest -v
```

Untuk menjalankan test satu fungsi saja:

```bash
pytest -v -k TestFilterData
```

Contoh-contoh di docstring juga dapat diuji dengan doctest:

```bash
python -m doctest fplib.py -v
```

## Daftar 15 Fungsi

| No | Fungsi | Parameter | Deskripsi | Contoh |
|----|--------|-----------|-----------|--------|
| 1 | `alur_proses` | `*fungsi` — fungsi satu-argumen | Merangkai beberapa fungsi menjadi satu pipeline (kiri ke kanan); mengembalikan fungsi baru. | `alur_proses(lambda x: x + 1, lambda x: x * 2)(3)` → `8` |
| 2 | `filter_data` | `predikat`, `data` | Menyaring elemen yang memenuhi `predikat`. | `filter_data(lambda x: x % 2 == 0, [1, 2, 3, 4])` → `[2, 4]` |
| 3 | `ubah_data` | `fungsi`, `data` | Mentransformasi tiap elemen (map). | `ubah_data(lambda x: x * x, [1, 2, 3])` → `[1, 4, 9]` |
| 4 | `cari_item` | `predikat`, `data`, `bawaan=None` | Mengambil elemen pertama yang cocok, atau `bawaan` bila tidak ada. | `cari_item(lambda x: x > 2, [1, 2, 3, 4])` → `3` |
| 5 | `urut_data` | `data`, `kunci=None`, `terbalik=False` | Mengurutkan data menjadi list baru. | `urut_data(["aa", "b", "ccc"], kunci=len, terbalik=True)` → `['ccc', 'aa', 'b']` |
| 6 | `kelompok_data` | `fungsi_kunci`, `data` | Mengelompokkan elemen berdasarkan kunci (group by) menjadi dict. | `kelompok_data(len, ["a", "bb", "c"])` → `{1: ['a', 'c'], 2: ['bb']}` |
| 7 | `total_nilai` | `data`, `awal=0` | Menjumlahkan seluruh elemen (reduce). | `total_nilai([1, 2, 3, 4])` → `10` |
| 8 | `rerata_nilai` | `data` | Rata-rata aritmetika; `0.0` bila data kosong. | `rerata_nilai([2, 4, 6])` → `4.0` |
| 9 | `nilai_ekstrem` | `data`, `kunci=None` | Mengembalikan tuple `(minimum, maksimum)`; `(None, None)` bila kosong. | `nilai_ekstrem([3, 1, 4, 1, 5])` → `(1, 5)` |
| 10 | `cek_valid` | `predikat`, `data`, `mode="semua"` | Validasi: `"semua"` = semua elemen valid, `"ada"` = minimal satu valid. `ValueError` bila mode salah. | `cek_valid(lambda x: x > 0, [1, 2, 3])` → `True` |
| 11 | `format_rupiah` | `angka` | Memformat angka ke Rupiah dengan pemisah ribuan titik (dibulatkan). | `format_rupiah(1500000)` → `'Rp1.500.000'` |
| 12 | `bersih_teks` | `teks`, `hapus_tanda_baca=False` | Trim, padatkan spasi, ubah ke huruf kecil; opsional hapus tanda baca. | `bersih_teks("  Halo,   DUNIA!  ", hapus_tanda_baca=True)` → `'halo dunia'` |
| 13 | `potong_data` | `data`, `ukuran` | Memotong data menjadi chunk berukuran tetap. `ValueError` bila `ukuran <= 0`. | `potong_data([1, 2, 3, 4, 5], 2)` → `[[1, 2], [3, 4], [5]]` |
| 14 | `hitung_frekuensi` | `data` | Menghitung kemunculan tiap elemen menjadi dict. | `hitung_frekuensi(["a", "b", "a"])` → `{'a': 2, 'b': 1}` |
| 15 | `gabung_rekursif` | `daftar` | Meratakan list/tuple bersarang secara rekursif (string tidak diratakan). | `gabung_rekursif([1, [2, [3, 4]], 5])` → `[1, 2, 3, 4, 5]` |

### Contoh Gabungan (pipeline)

```python
from fplib import alur_proses, filter_data, ubah_data, total_nilai, format_rupiah

# Total harga barang yang harganya di atas 10.000, setelah diskon 10%
hitung_total = alur_proses(
    lambda harga: filter_data(lambda h: h > 10_000, harga),
    lambda harga: ubah_data(lambda h: h * 0.9, harga),
    total_nilai,
    format_rupiah,
)

print(hitung_total([5_000, 20_000, 50_000]))  # Rp63.000
```

## Panduan Import untuk Anggota Kelompok

Letakkan `fplib.py` **di folder yang sama** dengan file aplikasi Anda, lalu import:

```python
# Cara 1: import seluruh modul dengan alias
import fplib as fp

print(fp.format_rupiah(25000))                       # Rp25.000
print(fp.filter_data(lambda x: x > 1, [1, 2, 3]))    # [2, 3]

# Cara 2: import fungsi tertentu saja
from fplib import filter_data, ubah_data, total_nilai

print(total_nilai(ubah_data(lambda x: x * 2, [1, 2, 3])))  # 12
```

Hal yang perlu diperhatikan:

1. **Jangan mengubah `fplib.py` secara langsung di branch `main`.** Buat branch baru dan ajukan pull request bila ada perubahan, lalu pastikan `pytest -v` tetap lulus.
2. **Jaga gaya fungsional:** jangan menambahkan mutasi data atau side-effect (`print`, variabel global, `list.append`, dll.) ke dalam fungsi pustaka.
3. Bila aplikasi Anda berada di subfolder, jalankan dari root repositori atau tambahkan `fplib.py` ke `PYTHONPATH`, atau ubah folder pustaka menjadi package dengan menambahkan `__init__.py`.
4. Setiap fungsi baru **wajib** disertai unit test di `test_fplib.py`.