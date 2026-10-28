# Inventory Multi-Role System (Thorix)

Aplikasi pencatatan stok barang (inventory) berbasis web dengan dua peran: **admin** dan **staff**.
Backend REST API dibuat dengan **FastAPI**, data disimpan di **PostgreSQL** lewat **SQLModel**
(async), dan login memakai **JWT** yang disimpan di cookie HttpOnly. Halaman depannya (login,
profil, dan halaman error) disajikan langsung oleh FastAPI memakai Jinja2.

## Fitur

| Bagian | Keterangan |
| --- | --- |
| Autentikasi | Daftar, masuk, keluar, lihat profil, ubah nama/email |
| Persetujuan akun | Pendaftar baru masuk antrean; **admin** memverifikasinya sebelum bisa masuk |
| Role | `admin`: kelola barang, verifikasi akun, ubah status akun. `staff`: lihat barang, catat transaksi |
| Barang (item) | Daftar dengan paginasi, detail, cari, tambah/ubah/hapus (admin) |
| Transaksi stok | Catat barang masuk/keluar; stok diperbarui otomatis dan tidak boleh negatif |
| Admin pertama | Dibuat otomatis saat server pertama kali menyala, dari nilai di `.env` |
| Halaman error | Halaman HTML untuk 400–504 (JSON untuk rute API) |

## Teknologi

- Python 3.12 (minimal 3.11, karena memakai `StrEnum`)
- FastAPI + Uvicorn
- SQLModel / SQLAlchemy async + asyncpg (PostgreSQL)
- PyJWT + bcrypt
- Jinja2 (template HTML)

## Struktur folder

```
inventory-project/
├── main.py                  # Entry point: app FastAPI, CORS, static, exception handler
├── debug_errors.py          # Rute uji halaman error (/debug/...) — hapus sebelum produksi
├── requirements.txt
├── .env.example             # Contoh konfigurasi (salin jadi .env)
├── backend/
│   ├── routers.py           # Router induk API (prefix /thorix-api)
│   ├── api/v1/              # Endpoint: auth, items, transactions
│   ├── services/            # Logika bisnis (dipanggil oleh endpoint)
│   ├── schemas/             # Model request/response (Pydantic)
│   ├── models/              # Tabel database (SQLModel)
│   ├── core/                # config (.env), security (JWT, bcrypt), enums
│   └── db/                  # Engine, session, helper simpan/ambil data, admin pertama
└── frontend/
    ├── routers.py           # Rute halaman HTML + mesin Jinja2
    ├── html/
    │   ├── index.html       # Halaman masuk / daftar / profil
    │   └── exceptions/      # Halaman error; semua mewarisi _base.html
    └── static/css/          # exceptions.css
```

Alur satu request API: `api/v1/*.py` (terima request) → `services/*.py` (logika) →
`models/*.py` (database), dengan `schemas/*.py` sebagai bentuk data masuk/keluar.

## Menjalankan di komputer sendiri

**Prasyarat:** Python 3.12 dan PostgreSQL yang sudah berjalan, dengan satu database kosong (mis. `inventory`).

```bash
# 1. Buat dan aktifkan virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Pasang dependensi
pip install -r requirements.txt

# 3. Siapkan konfigurasi, lalu isi nilainya di .env
cp .env.example .env

# 4. Jalankan server (dari root proyek)
python main.py
```

Pada `.env`, yang **wajib** diisi: `DATABASE_URL`, `SECRET_KEY`, serta `YOURNAME`, `EMAIL`, `PASSWORD`
untuk akun admin pertama. Penjelasan tiap variabel ada di `.env.example`.

Tabel dibuat otomatis saat server pertama kali menyala (`create_all`), jadi belum perlu migrasi.
Port server mengikuti `PORT` di `.env` (bawaan **8000**).

| Apa | Alamat (dengan PORT bawaan) |
| --- | --- |
| Halaman login / profil | http://localhost:8000/ |
| Dokumentasi API (Swagger) | http://localhost:8000/docs |
| Cek server hidup | http://localhost:8000/thorix-api/health |

### Masuk pertama kali

1. Saat server menyala dan tabel pengguna masih kosong, akun admin dibuat dari `YOURNAME`,
   `EMAIL`, dan `PASSWORD` di `.env`. Masuklah dengan email dan password itu.
2. Staf mendaftar lewat halaman login. Akun mereka belum bisa masuk sampai admin
   memverifikasinya: lihat antrean di `POST /auth/show-not-verified`, lalu setujui lewat
   `POST /auth/verify-email` (keduanya bisa dicoba di `/docs`).

## Ringkasan endpoint

Semua endpoint berada di bawah `/thorix-api/v1`. Selain daftar dan masuk, endpoint butuh login
(cookie `access_token_inventory`, atau header `Authorization: Bearer <token>`).

### Auth

| Method | Path | Fungsi | Akses |
| --- | --- | --- | --- |
| POST | `/auth/sign-up` | Daftar akun baru (`name`, `email`, `password`) | Publik |
| POST | `/auth/sign-in` | Masuk (`email`, `password`, `remember` opsional) | Publik |
| GET | `/auth/me` | Data pengguna yang sedang login | Login |
| PATCH | `/auth/edit-profile` | Ubah `name` dan/atau `email` | Login |
| DELETE | `/auth/sign-out` | Keluar | Login |
| POST | `/auth/show-not-verified` | Daftar akun yang belum diverifikasi | Admin |
| POST | `/auth/verify-email` | Verifikasi akun berdasarkan email | Admin |
| PATCH | `/auth/edit-status` | Ubah status kerja akun lain (`aktif`, `resign`, `phk`, `pensiun`) | Admin |

Password minimal 8 karakter dan mengandung huruf besar, huruf kecil, angka, serta simbol.

### Barang (items)

| Method | Path | Fungsi | Akses |
| --- | --- | --- | --- |
| GET | `/items/?limit=10&page=1` | Daftar barang dengan paginasi (limit 1–100) | Login |
| GET | `/items/detail/{item_id}` | Detail satu barang | Login |
| POST | `/items/search/` | Cari berdasarkan nama/SKU (body: `{"search": "pulpen"}`) | Login |
| POST | `/items/` | Tambah barang | Admin |
| PUT | `/items/update/{item_id}` | Ubah barang | Admin |
| DELETE | `/items/delete/{item_id}` | Hapus barang | Admin |

### Transaksi

| Method | Path | Fungsi | Akses |
| --- | --- | --- | --- |
| POST | `/transactions/` | Catat transaksi (`item_id`, `type`: `in`/`out`, `quantity`, `notes`) | Login |
| GET | `/transactions/?item_id=1` | Daftar transaksi (filter barang opsional) | Login |
| GET | `/transactions/{transaction_id}` | Detail satu transaksi | Login |

## Konfigurasi

Semua konfigurasi ada di `.env` (contoh lengkap dan penjelasannya di `.env.example`).

Beberapa nilai masih ditulis langsung di `main.py` dan perlu disesuaikan saat deploy:

- `ORIGINS` — daftar alamat frontend yang diizinkan (CORS), memakai `PORT` dari `.env`.
- `root_path="/thorix"` — harus sama dengan prefix di reverse proxy (Nginx).

## Frontend

- **Halaman login/profil** (`frontend/html/index.html`): HTML, CSS, dan JavaScript jadi
  satu file. Alamat API dan nama endpoint dikumpulkan di objek `CONFIG` di bagian
  atas `<script>`; ubah di sana jika backend berubah.
- **Halaman error**: `frontend/html/exceptions/_base.html` adalah kerangka bersama.
  Menambah halaman baru cukup 3 baris:

  ```jinja
  {% extends "html/exceptions/_base.html" %}
  {% set code = 418 %}
  {% set title = "Judul Singkat" %}
  {% set default_desc = "Pesan bawaan jika backend tidak mengirim detail." %}
  ```

  Lalu daftarkan kodenya di `STATUS_TEMPLATE_MAP` pada `main.py`.
  Untuk mengecek tampilannya, buka `/debug/error/<kode>` di browser.

## Sebelum deploy ke produksi

- Hapus `debug_errors.py` (atau jangan sertakan di server). `main.py` hanya memasang rute `/debug` jika berkasnya ada.
- Isi `SECRET_KEY` dengan string acak yang panjang, dan set `HTTPS=true` jika memakai HTTPS.
- Pastikan `DEBUG=false`.
- Ganti `PASSWORD` admin pertama dengan password yang kuat, dan ubah setelah masuk pertama kali.