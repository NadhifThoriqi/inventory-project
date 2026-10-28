# Panduan Docstring — inventory-project

File ini berisi docstring untuk kode Anda **di tempat terpisah**, sehingga kode asli tidak saya
ubah. Tujuannya dua: Anda tahu isi tiap bagian program, dan Anda belajar menulis docstring yang baik.
Silakan salin satu per satu ke file yang bersangkutan sambil membaca penjelasannya.

## Cara memakai

- 🆕 = belum ada docstring, **tambahkan**.
- ✏️ = docstring sudah ada, tetapi **tidak cocok dengan kode** (sisa proyek lain, atau kode sudah berubah) → **ganti**.
- Di tiap blok, baris `def ...:` / `class ...:` hanya menunjukkan letaknya. Salin bagian `"""..."""` saja,
  tempel tepat di bawah baris itu.
- Docstring menjelaskan perilaku yang **dimaksudkan**. Jika kode sekarang berbeda dari maksudnya,
  saya beri tanda ⚠️ dan rujukan ke `LAPORAN-BACKEND-3.md`. Perbaiki kodenya, bukan docstring-nya.

Cakupan: seluruh item yang belum punya docstring (37 item) ditambah docstring lama yang salah.
Yang sudah benar tidak saya ulang.

---

## Bagian 1 — Cara menulis docstring yang baik

### Apa itu docstring?
String tiga kutip yang diletakkan **tepat di bawah** `def`, `class`, atau di **paling atas** file.
Python menyimpannya sebagai dokumentasi yang bisa dibaca program:

```python
>>> import backend.services.items as m
>>> help(m.read_item)        # menampilkan docstring-nya
```

Bonus untuk FastAPI: docstring fungsi **endpoint** otomatis tampil sebagai deskripsi di halaman
`/docs` (Swagger). Jadi docstring endpoint dibaca oleh pemakai API, bukan hanya oleh Anda.
Untuk endpoint, tulis yang relevan bagi pemanggil (body, query, path, kode error), dan tidak perlu
menjelaskan `session` atau `user` (itu hasil `Depends`, urusan internal).

### Gaya Google (yang sudah Anda pakai)

```python
def fungsi(a: int, b: str) -> bool:
    """
    Ringkasan satu kalimat, diakhiri titik.

    Paragraf penjelasan (opsional): aturan bisnis, alasan, atau hal yang tidak
    terlihat dari kodenya.

    Args:
        a (int): Penjelasan parameter a.
        b (str): Penjelasan parameter b.

    Returns:
        bool: Penjelasan nilai kembalian.

    Raises:
        HTTPException: 404 jika data tidak ditemukan.
    """
```

Untuk **class** (model/skema) gunakan `Attributes:` sebagai pengganti `Args:`.
Untuk fungsi `async def ... yield` gunakan `Yields:`.

### Lima aturan praktis

1. **Baris pertama = satu kalimat** yang menjawab "ini ngapain?". Itu yang tampil di tooltip editor.
2. **Tulis *kenapa* dan aturannya, bukan terjemahan kode.** `# tambah 1` tidak berguna;
   "stok tidak boleh negatif" berguna.
3. **`Args` dan `Raises` hanya yang benar-benar ada di kode**, dengan nama persis sama seperti di `def`.
   Setiap kali Anda mengubah parameter, ubah docstring-nya.
4. **Tipe di dalam kurung:** `nama (tipe): penjelasan`.
5. **Docstring yang salah lebih berbahaya daripada tidak ada.** Contoh dari proyek Anda sendiri:
   peran `BUYER` yang tidak ada, "OTP dikirim ke email" padahal tidak ada email, dan "berlaku 3 hari"
   padahal 1 atau 30 hari. Pembaca percaya pada docstring, lalu salah paham.

---

## Bagian 2 — Docstring per file

### `main.py`

✏️ **Docstring modul** (baris 1–5) — masih menyebut proyek lain.

```python
"""
main.py — Entry point aplikasi Thorix API (Inventory Multi-Role System).

Merakit aplikasi FastAPI: siklus hidup startup/shutdown (menyiapkan tabel dan
akun admin pertama), CORS, file statis, router backend/frontend, serta
exception handler global yang membalas JSON untuk rute API dan halaman HTML
untuk rute lainnya.

Jalankan dari root proyek:  python main.py
"""
```

---

### `backend/routers.py`

🆕 **Docstring modul**

```python
"""
routers.py — Router induk API.

Menggabungkan router tiap fitur (auth, items, transactions) di bawah prefix
"/thorix-api/v1" lalu dipasang ke aplikasi oleh main.py. Menambah fitur baru =
membuat router di api/v1/ lalu mendaftarkannya di sini.
"""
```

> Catatan belajar: `run = backend_router` hanyalah nama lain untuk objek yang sama. Cukup pakai
> `backend_router.include_router(...)`; tidak perlu alias.

---

### `backend/api/v1/auth.py`

✏️ **Docstring modul** — daftar endpoint lama (`/forgot`, `/reset-password`) sudah tidak ada.

```python
"""
Module:
    api/v1/auth.py
Deskripsi:
    Endpoint HTTP untuk autentikasi dan manajemen akun. Lapisan ini hanya
    menerima request dan memeriksa login lewat dependency, lalu meneruskan
    pekerjaan ke services/auth.py.

Endpoints (prefix /thorix-api/v1/auth):
    GET    /me                - Data pengguna yang sedang login.
    POST   /sign-up           - Daftar akun baru (menunggu persetujuan admin).
    POST   /sign-in           - Masuk; token JWT disimpan di cookie HttpOnly.
    DELETE /log-out           - Keluar; token dimasukkan ke blacklist.
    PATCH  /edit-profile      - Ubah nama dan/atau email sendiri.
    POST   /show-not-verified - (Admin) Daftar akun yang belum diverifikasi.
    POST   /verify-email      - (Admin) Verifikasi akun berdasarkan email.
    PATCH  /edit-status       - (Admin) Ubah status kerja akun pengguna lain.
"""
```

✏️ **`read_users_me(user)`** — menyebut parameter `token` dan `session` yang tidak ada.

```python
async def read_users_me(user: Auth = Depends(get_current_user())) -> Auth:
    """
    Mengambil data profil pengguna yang sedang login.

    Returns:
        Auth: Data pengguna, dibentuk sesuai skema ShowMe (id, email, name, role).

    Raises:
        HTTPException: 401 jika belum login, token kedaluwarsa, atau sudah logout.
    """
```

✏️ **`show_not_verified(session, user)`**

```python
async def show_not_verified(...) -> dict[str, str]:
    """
    (Admin) Menampilkan akun yang belum diverifikasi.

    Berguna untuk melihat antrean pendaftar yang menunggu persetujuan.

    Returns:
        dict: {"status": "success",
               "not_verified_users": [{"id", "email", "name"}, ...]}

    Raises:
        HTTPException: 403 jika pemanggil bukan admin.
    """
```

> ⚠️ Anotasi `-> dict[str, str]` tidak cocok dengan isi (ada list), sehingga endpoint ini 500.
> Lihat B3 di laporan. Untuk operasi yang hanya **membaca**, lazimnya memakai `GET`, bukan `POST`.

✏️ **`sign_up(data_in, session)`** — menyebut OTP dan `background_tasks` yang tidak ada.

```python
async def sign_up(data_in: SignUp, session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    """
    Mendaftarkan akun baru dengan peran staff.

    Akun baru belum terverifikasi dan masuk antrean; admin harus memverifikasinya
    lewat POST /auth/verify-email sebelum akun itu bisa masuk.

    Args:
        data_in (SignUp): name, email, dan password. Password minimal 8 karakter
            dan mengandung huruf besar, huruf kecil, angka, serta simbol.

    Returns:
        dict[str, str]: Pesan sukses pendaftaran.

    Raises:
        HTTPException: 400 jika email sudah terdaftar atau masih dalam antrean.
    """
```

🆕/✏️ **`sign_in(response, request, session)`**

```python
async def sign_in(response: Response, request: SignIn, session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    """
    Masuk dengan email dan password.

    Jika berhasil, server menyimpan JWT di cookie HttpOnly "access_token_inventory".
    Frontend tidak perlu menyimpan token sendiri; browser mengirim cookie itu otomatis.

    Args:
        response (Response): Dipakai server untuk memasang cookie.
        request (SignIn): email, password, dan remember (True = sesi lebih lama).
            Catatan: ini adalah body JSON, bukan objek Request milik FastAPI.

    Returns:
        dict[str, str]: Pesan "Login berhasil".

    Raises:
        HTTPException: 401 jika email atau password salah.
            403 jika akun belum diverifikasi atau statusnya tidak aktif.
    """
```

> Catatan belajar: nama `request` untuk body JSON membingungkan, karena di FastAPI `request`
> biasanya berarti objek `Request`. `credentials` atau `data_in` (seperti di `sign_up`) lebih jelas.

🆕/✏️ **`verify_email(data, session, user)`**

```python
async def verify_email(data: VerifyEmail, session: AsyncSession = ..., user: Auth = ...) -> dict[str, str]:
    """
    (Admin) Memverifikasi akun pendaftar berdasarkan email.

    Args:
        data (VerifyEmail): Email akun yang akan diverifikasi.

    Returns:
        dict[str, str]: Pesan sukses.

    Raises:
        HTTPException: 403 jika pemanggil bukan admin; 404 jika email tidak ditemukan.
    """
```

✏️ **`log_out(response, get_token, session)`** — menyebut `request` yang tidak ada dan cookie bernama `access_token`.

```python
async def log_out(response: Response, get_token: Logout = ..., session: AsyncSession = ...) -> dict[str, str]:
    """
    Mengakhiri sesi pengguna (logout).

    Token yang sedang dipakai dimasukkan ke blacklist sehingga tidak bisa dipakai
    lagi walau belum kedaluwarsa, lalu cookie "access_token_inventory" dihapus dari browser.

    Returns:
        dict[str, str]: Pesan konfirmasi logout.

    Raises:
        HTTPException: 401 jika belum login atau token sudah tidak berlaku.
    """
```

> ⚠️ Saat ini endpoint ini selalu 401 (lihat B5 di laporan).

🆕 **`edit_profile(edit_in, user, session)`**

```python
async def edit_profile(edit_in: EditProfile, user: Auth = ..., session: AsyncSession = ...):
    """
    Mengubah nama dan/atau email milik pengguna yang sedang login.

    Hanya field yang dikirim yang diubah; field yang tidak dikirim dibiarkan.

    Args:
        edit_in (EditProfile): name dan/atau email baru (keduanya opsional).

    Returns:
        None: Respons berisi null jika berhasil.

    Raises:
        HTTPException: 401 jika belum login.
    """
```

✏️ **`edit_status(user_target, user, session)`** — yang diubah adalah pengguna **lain**, bukan yang login.

```python
async def edit_status(user_target: EditStatus, user: Auth = ..., session: AsyncSession = ...) -> dict[str, str]:
    """
    (Admin) Mengubah status kerja akun pengguna lain.

    Args:
        user_target (EditStatus): user_id akun yang diubah dan status barunya
            (aktif, resign, phk, atau pensiun).

    Returns:
        dict[str, str]: Pesan konfirmasi.

    Raises:
        HTTPException: 403 jika pemanggil bukan admin; 404 jika user target tidak ada.
    """
```

---

### `backend/api/v1/items.py`

🆕 **Docstring modul**

```python
"""
Module:
    api/v1/items.py
Deskripsi:
    Endpoint HTTP untuk data barang (item). Semua endpoint butuh login;
    menambah, mengubah, dan menghapus barang khusus admin (diperiksa di services/items.py).

Endpoints (prefix /thorix-api/v1/items):
    GET    /                   - Daftar barang dengan paginasi (?limit=&page=).
    POST   /                   - Tambah barang (admin).
    GET    /detail/{item_id}   - Detail satu barang.
    PUT    /update/{item_id}   - Ubah barang (admin).
    DELETE /delete/{item_id}   - Hapus barang (admin).
    POST   /search/            - Cari barang berdasarkan nama atau SKU.
"""
```

✏️ **`read_items(limit, page, session, user)`** — belum menjelaskan `limit` dan `page`.

```python
async def read_items(limit: int = Query(10, ge=1, le=100), page: int = Query(1, ge=1), ...) -> Sequence[Item]:
    """
    Mengambil daftar barang dengan paginasi.

    Args:
        limit (int): Jumlah barang per halaman, 1–100. Bawaan 10.
        page (int): Nomor halaman, mulai dari 1. Bawaan 1.

    Returns:
        Sequence[ItemRead]: Barang pada halaman tersebut (kosong jika halaman melewati data).
    """
```

> Catatan belajar: komentar `# Contoh data item, seharusnya diambil dari database` di beberapa
> fungsi (api/v1/items.py baris 86, 127, 148; services/items.py baris 27) sudah usang. Kodenya sudah
> memakai database, jadi hapus komentarnya. Komentar yang tidak benar sama berbahayanya dengan docstring yang salah.

---

### `backend/api/v1/transactions.py`

🆕 **Docstring modul** dan tiga endpoint

```python
"""
Module:
    api/v1/transactions.py
Deskripsi:
    Endpoint HTTP untuk transaksi stok (barang masuk/keluar). Butuh login.

Endpoints (prefix /thorix-api/v1/transactions):
    POST /                   - Catat transaksi baru dan sesuaikan stok barang.
    GET  /                   - Daftar transaksi (opsional ?item_id=).
    GET  /{transaction_id}   - Detail satu transaksi.
"""
```

```python
async def create_transaction(transaction: TransactionCreate, ...) -> Transaction:
    """
    Mencatat transaksi stok dan memperbarui stok barang dalam satu langkah.

    Pelaku transaksi diambil dari pengguna yang sedang login.

    Args:
        transaction (TransactionCreate): item_id, type ("in"/"out"), quantity (> 0), dan notes (opsional).

    Returns:
        Transaction: Catatan transaksi yang tersimpan.

    Raises:
        HTTPException: 404 jika barang tidak ada; 400 jika stok tidak cukup untuk transaksi "out".
    """
```

```python
async def read_transactions(item_id: int | None = None, ...) -> Sequence[Transaction]:
    """
    Menampilkan daftar transaksi.

    Args:
        item_id (int | None): Jika diisi, hanya transaksi untuk barang itu. Bawaan semua.

    Returns:
        Sequence[Transaction]: Daftar transaksi.
    """
```

```python
async def read_transaction(transaction_id: int, ...) -> Transaction:
    """
    Menampilkan detail satu transaksi.

    Args:
        transaction_id (int): ID transaksi.

    Raises:
        HTTPException: 404 jika transaksi tidak ditemukan.
    """
```

---

### `backend/core/config.py`

✏️ **Docstring modul** — judulnya `db_config.py` dan isinya tentang database (salinan dari file lain).

```python
"""
Module:
    core/config.py
Deskripsi:
    Membaca konfigurasi aplikasi dari environment dan file .env, lalu
    menyediakannya sebagai satu objek `settings` yang dipakai seluruh aplikasi.
    Prioritas nilai: variabel environment sistem > file .env > nilai default.
Author:
    Nadhif Thoriqi
"""
```

🆕 **`AppConfig`** dan **`__init__`**

```python
class AppConfig:
    """
    Kumpulan pengaturan aplikasi yang dibaca dari .env.

    Attributes:
        database_url (str): URL database async (WAJIB), mis. postgresql+asyncpg://...
        secret_key (str): Kunci penanda tangan JWT (WAJIB).
        project_name (str): Judul aplikasi di Swagger dan /health.
        port (int): Port server dan acuan origin CORS.
        debug (bool): True = cetak query SQL dan aktifkan reload server.
        algorithm (str): Algoritma JWT, bawaan HS256.
        access_token_expire_minutes (int): Masa berlaku token biasa, dalam MENIT.
        remember_token_expire_days (int): Masa berlaku token "ingat saya", dalam HARI.
        cookie_secure (bool): Belum dipakai kode (yang dipakai: `https`).
        https (bool): True = cookie login diberi flag Secure.
        domain (str | None): Domain cookie login; None = domain asal.
        name (str): Nama admin pertama (WAJIB).
        email (EmailStr): Email admin pertama (WAJIB, divalidasi formatnya).
        password (str): Password admin pertama (WAJIB).
    """

    def __init__(self):
        """
        Membaca dan memvalidasi semua pengaturan.

        Raises:
            RuntimeError: Jika DATABASE_URL atau SECRET_KEY tidak ada atau kosong.
            KeyError: Jika variabel admin pertama (USERNAME, EMAIL, PASSWORD) tidak ada.
        """
```

> ⚠️ Nama `USERNAME` bermasalah di Windows (lihat B4 di laporan), dan variabel admin dibaca di luar
> blok `try`, jadi pesan errornya mentah (`KeyError`), tidak sejelas pesan untuk `SECRET_KEY`.

---

### `backend/core/enums.py`

✏️ **`Role`** — `BUYER` tidak ada; nilainya `STAFF`.

```python
class Role(StrEnum):
    """
    Peran pengguna dalam sistem.

    Values:
        ADMIN: Akses penuh. Satu-satunya yang boleh mengubah data barang,
            memverifikasi akun, dan mengubah status akun.
        STAFF: Pengguna biasa (bawaan saat mendaftar). Boleh melihat barang dan mencatat transaksi.
    """
```

🆕 **`Status`**

```python
class Status(StrEnum):
    """
    Status kerja akun pengguna.

    Values:
        AKTIF: Masih bekerja; akun boleh dipakai (bawaan).
        Resign: Berhenti atas keinginan sendiri.
        PHK: Diberhentikan oleh perusahaan.
        PENSIUN: Berhenti karena memasuki masa pensiun.
    """
```

🆕 **`TypeMutasi`**

```python
class TypeMutasi(StrEnum):
    """
    Jenis mutasi stok pada transaksi.

    Values:
        IN: Barang masuk (stok bertambah).
        OUT: Barang keluar (stok berkurang, tidak boleh melebihi stok yang ada).
    """
```

> Catatan belajar: `Resign` memakai huruf besar-kecil campuran, sedangkan `AKTIF`, `PHK`, `PENSIUN` huruf besar semua.
> Konvensi Python untuk anggota enum adalah `HURUF_BESAR`, jadi `RESIGN` lebih konsisten.

---

### `backend/core/security.py`

✏️ **`create_access_token(data, expires_delta)`** — kembalian ditulis `bytes`, padahal PyJWT mengembalikan `str`.

```python
def create_access_token(data: CookieToken, expires_delta: timedelta) -> bytes:
    """
    Membuat JWT access token.

    Isi token berasal dari `data` ditambah klaim "exp" (waktu kedaluwarsa),
    lalu ditandatangani dengan SECRET_KEY memakai algoritma dari settings.

    Args:
        data (CookieToken): Isi token: sub (ID user), email, name, dan type ("access").
        expires_delta (timedelta): Lama token berlaku sejak dibuat.

    Returns:
        str: JWT yang sudah dienkode.
    """
```

> Sesuaikan juga anotasinya menjadi `-> str`, dan `str(...)` yang membungkus pemanggilnya di
> `services/auth.py` jadi tidak perlu.

✏️ **`_get_cookie(...)`** — versi yang lebih lengkap dari docstring satu baris yang sekarang

```python
async def _get_cookie(session, access_token_inventory=Cookie(None), authorization=Header(None), return_user_object=True) -> CookieToken | Logout:
    """
    Mengambil token JWT dari request lalu memvalidasinya.

    Urutan pencarian: cookie "access_token_inventory" dulu; jika tidak ada,
    header "Authorization: Bearer <token>".

    Args:
        session (AsyncSession): Sesi database, dipakai untuk mengecek blacklist.
        access_token_inventory (str | None): Nilai cookie login.
        authorization (str | None): Isi header Authorization.
        return_user_object (bool | None): True = token di-decode dan dikembalikan sebagai
            CookieToken. False = token mentah dibungkus Logout (dipakai oleh logout).

    Returns:
        CookieToken | Logout: Isi token yang valid, atau token mentah.

    Raises:
        HTTPException: 401 jika token tidak ada, sudah di-blacklist, kedaluwarsa, atau rusak.
    """
```

> ⚠️ Pada mode `False`, token **tidak** di-decode dan tidak punya `type`, sehingga logout gagal
> (B5 di laporan).

🆕 **`get_current_user(return_user_object)`** dan fungsi dalamnya `dependency`

```python
def get_current_user(return_user_object: bool | None = True):
    """
    Membuat dependency FastAPI untuk mengambil pengguna yang sedang login.

    Ini fungsi "pabrik": dipanggil saat mendefinisikan endpoint, dan hasilnya
    (fungsi `dependency`) yang dijalankan FastAPI pada setiap request.

        user  = Depends(get_current_user())                           # objek Auth
        token = Depends(get_current_user(return_user_object=False))   # token mentah (logout)

    Args:
        return_user_object (bool | None): True (bawaan) = kembalikan objek Auth dari database.
            False = kembalikan token mentah tanpa mengambil user, khusus untuk logout.

    Returns:
        Callable: Fungsi dependency async yang mengembalikan Auth atau Logout.
    """

    async def dependency(session=..., access_token_inventory=..., authorization=...):
        """
        Memvalidasi token pada request ini dan mengembalikan pemiliknya.

        Raises:
            HTTPException: 401 jika belum login, token tidak valid/kedaluwarsa/di-blacklist,
                tipe token bukan "access", atau user tidak ada di database.
        """
```

> Catatan belajar: kenapa `Depends(get_current_user())` ada tanda kurungnya? Karena
> `get_current_user` adalah pabrik; kurungnya **membuat** dependency-nya. Tanpa kurung, Anda menyerahkan pabriknya,
> bukan hasilnya.

---

### `backend/db/sessions.py`

✏️ **Docstring modul** — judulnya `database.py`; sekarang juga mengurus admin pertama.

```python
"""
Module:
    db/sessions.py
Deskripsi:
    Mengelola koneksi database: engine async, factory session, pembuatan
    tabel saat startup, dan pembuatan akun admin pertama.
Author:
    Nadhif Thoriqi
"""
```

🆕 **`get_session`**

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency FastAPI yang menyediakan satu AsyncSession per request.

    Sesi dibuka saat request mulai dan ditutup otomatis (`async with`) ketika
    request selesai, termasuk bila terjadi error.

    Yields:
        AsyncSession: Sesi database untuk dipakai endpoint dan service.
    """
```

🆕 **`create_engine`**

```python
async def create_engine():
    """
    Membuat semua tabel yang belum ada (SQLModel.metadata.create_all).

    Dipanggil sekali saat startup (lifespan di main.py). Hanya menambah tabel
    baru; tidak mengubah tabel yang sudah ada. Hanya model yang sudah di-import yang ikut dibuat.
    """
```

🆕 **`close_engine`**

```python
async def close_engine():
    """Menutup semua koneksi di pool database. Dipanggil saat shutdown aplikasi."""
```

🆕 **`check_database_is_empty`**

```python
async def check_database_is_empty() -> None:
    """
    Membuat akun admin pertama jika tabel 'auth' masih kosong.

    Dipanggil saat startup. Data admin diambil dari .env (USERNAME, EMAIL, PASSWORD).
    Jika sudah ada minimal satu pengguna, fungsi tidak melakukan apa-apa, jadi aman
    dijalankan pada setiap startup. Akun dibuat dengan peran ADMIN, status AKTIF, dan sudah terverifikasi.
    """
```

> ⚠️ Kode sekarang menulis `is_verified=False` (B1 di laporan); docstring di atas berlaku setelah diperbaiki.
>
> Catatan belajar: nama fungsi sebaiknya menggambarkan **semua** yang dilakukannya. Fungsi ini bukan
> hanya mengecek, tetapi membuat admin; `ensure_first_admin` lebih jujur. Begitu juga `create_engine`,
> yang sebenarnya membuat **tabel** (`create_tables`). Nama yang tepat sering menghilangkan kebutuhan komentar.

---

### `backend/db/utils.py`

🆕 **Docstring modul**

```python
"""
Module:
    db/utils.py
Deskripsi:
    Fungsi bantu database yang dipakai lintas service: paginasi (show_db)
    dan penyimpanan objek (save_db).
"""
```

✏️ **`show_db`** — jelaskan arti `page` dan nilai bawaannya.

```python
async def show_db(session, statement, get_limit: int = 10, page: int = 0) -> list[Any]:
    """
    Menjalankan query SELECT dengan paginasi.

    Halaman dihitung mulai dari 1: offset = (page - 1) * get_limit.
    Nilai page di bawah 1 (termasuk bawaan 0) diperlakukan sebagai halaman 1.

    Args:
        session (AsyncSession): Sesi database.
        statement (SelectOfScalar[Any]): Query SELECT yang belum dibatasi, mis. select(Item).
        get_limit (int): Jumlah baris per halaman. Bawaan 10.
        page (int): Nomor halaman, mulai dari 1.

    Returns:
        list[Any]: Baris pada halaman tersebut (kosong jika halaman melewati data).
    """
```

> Tambahkan `.order_by(...)` pada `statement` yang dikirim (mis. `select(Item).order_by(Item.id)`).
> Tanpa urutan yang pasti, isi halaman bisa bergeser antar request.

✏️ **`save_db`** — tambahkan `Args` dan catatan tentang commit

```python
async def save_db(session: AsyncSession, model_object: Any) -> None:
    """
    Menyimpan (insert atau update) satu objek, lalu menyegarkannya dari database.

    Langkah: session.add() → commit() → refresh(). Setelah refresh, kolom yang diisi
    database (id, default server) sudah tersedia di objek.

    Args:
        session (AsyncSession): Sesi database.
        model_object (Any): Objek model SQLModel (tabel) yang akan disimpan.

    Note:
        commit() ikut menyimpan semua perubahan lain yang sudah di-add pada sesi yang sama.
        Itulah sebabnya create_transaction menyimpan perubahan stok dan catatan
        transaksinya sekaligus dalam satu transaksi database.
    """
```

---

### `backend/models/auth.py`

✏️ **`Auth`** — menyebut `otp_code` (tidak ada), peran default `BUYER` (sebenarnya STAFF), dan melewatkan 3 kolom.

```python
class Auth(SQLModel, table=True):
    """
    Model tabel 'auth': akun pengguna.

    Attributes:
        id (uuid.UUID): Primary key, dibuat otomatis (uuid4).
        name (str): Nama lengkap.
        email (EmailStr): Email unik (maks. 255 karakter), dipakai untuk login.
        hashed_password (str): Hash bcrypt dari password; password asli tidak pernah disimpan.
        is_verified (bool): True jika admin sudah menyetujui akun. Bawaan False.
        role (Role): Peran pengguna (admin/staff). Bawaan STAFF.
        status (Status): Status kerja (aktif, resign, phk, pensiun). Bawaan AKTIF.
        riwayat_status_kerja (datetime): Waktu terakhir status berubah (UTC).
        transaksi_dilakukan (list[Transaction]): Relasi ke transaksi yang dibuat pengguna
            ini. Bukan kolom; diisi SQLAlchemy saat dibutuhkan.
    """
```

✏️ **`BlacklistToken`** — menyebut kolom `id` yang tidak ada (primary key-nya adalah `token`).

```python
class BlacklistToken(SQLModel, table=True):
    """
    Model tabel 'blacklist_token': token JWT yang sudah di-logout.

    Token yang ada di tabel ini ditolak walau belum kedaluwarsa. Pengecekannya
    dilakukan di core/security.py (_get_cookie).

    Attributes:
        token (str): String JWT yang di-blacklist (primary key).
        blacklisted_at (datetime): Waktu token dimasukkan ke blacklist (UTC).

    Note:
        Baris yang token-nya sudah kedaluwarsa aman dihapus secara berkala agar tabel tidak membengkak.
    """
```

---

### `backend/models/item.py`

🆕 **Docstring modul dan `Item`**

```python
"""
Module:
    models/item.py
Deskripsi:
    Model tabel 'item' (barang inventori).
"""
```

```python
class Item(SQLModel, table=True):
    """
    Model tabel 'item': barang yang stoknya dicatat.

    Attributes:
        id (int | None): Primary key (auto-increment); None sebelum disimpan.
        sku (str): Kode barang unik (maks. 100 karakter).
        name (str): Nama barang (maks. 255 karakter).
        stock (int): Jumlah stok saat ini; berubah lewat transaksi.
        min_stock (int): Batas stok minimum (disimpan untuk peringatan stok menipis,
            logikanya belum ada).
        description (str | None): Keterangan tambahan.
        transaksi_list (list[Transaction]): Relasi ke riwayat transaksi barang ini.
    """
```

---

### `backend/models/transaction.py`

🆕 **Docstring modul dan `Transaction`**

```python
"""
Module:
    models/transaction.py
Deskripsi:
    Model tabel 'transaction': riwayat mutasi stok (barang masuk/keluar).
"""
```

```python
class Transaction(SQLModel, table=True):
    """
    Model tabel 'transaction': satu catatan mutasi stok.

    Attributes:
        id (int | None): Primary key (auto-increment).
        item_id (int): Barang yang dimutasi (foreign key ke item.id).
        user_id (uuid.UUID): Pengguna yang mencatat (foreign key ke auth.id).
        type (TypeMutasi): "in" (masuk) atau "out" (keluar).
        quantity (int): Jumlah barang, harus > 0. Validasinya dilakukan oleh skema
            TransactionCreate; `Field(gt=0)` pada model tabel tidak memvalidasi apa pun.
        notes (str | None): Catatan tambahan.
        timestamp (datetime): Waktu transaksi (UTC), diisi otomatis.
        auth (Auth): Relasi ke pelaku.
        item (Item): Relasi ke barang.
    """
```

> Catatan belajar: model SQLModel dengan `table=True` **tidak** menjalankan validasi Pydantic saat objek
> dibuat. Itu sebabnya aturan seperti `gt=0` harus diletakkan di schema (class `BaseModel` biasa), bukan di model tabel.

---

### `backend/schemas/auth.py`

🆕 **`validate_password_strength`**

```python
def validate_password_strength(v: str) -> str:
    """
    Memeriksa kekuatan password saat pendaftaran.

    Aturan: minimal 8 karakter; mengandung huruf besar, huruf kecil, angka,
    dan satu simbol (karakter apa pun selain huruf dan angka).

    Args:
        v (str): Password yang diperiksa.

    Returns:
        str: Password yang sama jika lolos.

    Raises:
        ValueError: Berisi aturan yang dilanggar. Pydantic mengubahnya menjadi
            respons 422 dengan pesan "Value error, <pesan>".
    """
```

✏️ **`SignUp`** — "diwarisi dari OTP / SignIn" tidak benar (class ini mandiri).

```python
class SignUp(BaseModel):
    """
    Body request pendaftaran akun baru.

    Attributes:
        name (str): Nama lengkap.
        email (EmailStr): Alamat email (format divalidasi otomatis).
        password (str): Password; harus lolos validate_password_strength.
    """
```

✏️ **`SignIn`** — tambahkan `remember`.

```python
class SignIn(BaseModel):
    """
    Body request login.

    Attributes:
        email (EmailStr): Alamat email akun.
        password (str): Password asli (plaintext); dibandingkan dengan hash di database.
        remember (bool): True = sesi lebih lama ("ingat saya"). Bawaan False.
    """
```

🆕 **`EditProfile`**

```python
class EditProfile(BaseModel):
    """
    Body request ubah profil. Hanya field yang dikirim yang diubah.

    Attributes:
        email (EmailStr | None): Email baru, atau None untuk tidak mengubah.
        name (str | None): Nama baru, atau None untuk tidak mengubah.
    """
```

✏️ **`ShowMe`** — menyebut `is_verified` (tidak ada di skema) dan peran `buyer`.

```python
class ShowMe(BaseModel):
    """
    Respons data profil pengguna yang sedang login (GET /auth/me).

    Attributes:
        id (uuid.UUID): ID unik pengguna.
        email (EmailStr): Alamat email.
        name (str): Nama pengguna.
        role (str): Peran pengguna (admin/staff).
    """
```

✏️ **`VerifyEmail`** — menyebut OTP; field-nya `is_verified`.

```python
class VerifyEmail(BaseModel):
    """
    Body request verifikasi akun oleh admin.

    Attributes:
        email (EmailStr): Email akun yang akan diverifikasi.
        is_verified (bool): Saat ini tidak berpengaruh; service selalu mengisi True.
    """
```

> ⚠️ Lihat B6 di laporan: hapus field `is_verified`, atau gunakan nilainya.

✏️ **`EditStatus`** — nilai statusnya bukan "AKTIF/TIDAK_AKTIF".

```python
class EditStatus(BaseModel):
    """
    Body request ubah status kerja akun (khusus admin).

    Attributes:
        user_id (uuid.UUID): ID akun yang diubah.
        status (Status): Status baru: aktif, resign, phk, atau pensiun.
    """
```

✏️ **`CookieToken`** — atributnya `sub/email/name/type`, bukan `access_token`.

```python
class CookieToken(BaseModel):
    """
    Isi (payload) JWT login yang disimpan di cookie.

    Attributes:
        sub (str): ID pengguna (UUID dalam bentuk string); acuan utama identitas.
        email (EmailStr): Email pengguna saat token dibuat.
        name (str): Nama pengguna saat token dibuat.
        type (str): Jenis token; harus "access" untuk login biasa.
    """
```

---

### `backend/schemas/item.py`

🆕 **Docstring modul dan seluruh class**

```python
"""
Module:
    schemas/item.py
Deskripsi:
    Skema Pydantic untuk data barang: bentuk body request dan respons API.
"""
```

```python
class ItemBase(BaseModel):
    """
    Field dasar barang yang dipakai bersama oleh skema lain.

    Attributes:
        sku (str): Kode barang unik.
        name (str): Nama barang.
        stock (int): Jumlah stok.
        min_stock (int): Batas stok minimum.
        description (str | None): Keterangan tambahan.
    """

class ItemCreate(ItemBase):
    """Body request tambah barang. Sama dengan ItemBase; `id` dibuat database."""

class ItemRead(ItemBase):
    """
    Respons data barang.

    Attributes:
        id (int): ID barang yang dibuat database.
    """

class ItemSearch(BaseModel):
    """
    Body request pencarian barang.

    Attributes:
        search (str): Kata kunci (wajib, minimal 1 karakter setelah spasi di tepi dibuang).
            Dicocokkan ke nama atau SKU tanpa peduli huruf besar/kecil.
    """

class ItemUpdate(BaseModel):
    """
    Body request ubah barang. Semua field opsional; hanya yang dikirim yang diubah.

    Attributes:
        sku (str | None): Kode barang baru.
        name (str | None): Nama baru.
        stock (int | None): Stok baru.
        min_stock (int | None): Batas stok minimum baru.
        description (str | None): Keterangan baru.
    """
```

> Catatan belajar: pola **Base / Create / Read / Update** itu umum. Base memuat field bersama; Create =
> apa yang dikirim klien; Read = apa yang dikembalikan server (ada `id`); Update = semua opsional.

---

### `backend/schemas/transaction.py`

🆕 **Docstring modul dan class**

```python
"""
Module:
    schemas/transaction.py
Deskripsi:
    Skema Pydantic untuk transaksi stok: body request dan respons API.
"""
```

```python
class TransactionCreate(BaseModel):
    """
    Body request pencatatan transaksi stok.

    Attributes:
        item_id (int): ID barang yang dimutasi.
        type (TypeMutasi): "in" (masuk) atau "out" (keluar).
        quantity (int): Jumlah barang, harus lebih dari 0.
        notes (str | None): Catatan tambahan.
    """

class TransactionRead(BaseModel):
    """
    Respons data transaksi.

    Attributes:
        id (int): ID transaksi.
        item_id (int): ID barang.
        user_id (uuid.UUID): ID pengguna yang mencatat.
        type (TypeMutasi): Jenis mutasi.
        quantity (int): Jumlah barang.
        notes (str | None): Catatan tambahan.
        timestamp (datetime): Waktu transaksi (UTC).
    """

    class Config:
        """Mengizinkan objek ORM (Transaction) dibaca langsung (`from_attributes`)."""
```

> Catatan belajar: `class Config:` adalah gaya Pydantic v1 dan akan dihapus. Gaya Pydantic v2:
> `model_config = ConfigDict(from_attributes=True)` (sudah Anda pakai di `ItemSearch`).

---

### `backend/services/auth.py`

✏️ **Docstring modul** — judul `auth_service.py`, "Sign-In" seharusnya Sign-Up, dan OTP tidak ada.

```python
"""
Module:
    services/auth.py
Deskripsi:
    Logika bisnis autentikasi: pendaftaran, login (JWT di cookie HttpOnly),
    logout (blacklist token), verifikasi dan pengelolaan akun oleh admin.
    Dipanggil oleh endpoint di api/v1/auth.py.
Author:
    Nadhif Thoriqi
"""
```

✏️ **`sign_up`** — "OTP telah dikirim" tidak benar.

```python
async def sign_up(data_in: SignUp, session: AsyncSession) -> dict[str, str]:
    """
    Mendaftarkan akun baru ke antrean verifikasi.

    Alur:
    1. Cari akun dengan email yang sama.
    2. Jika ada dan sudah terverifikasi → tolak (email sudah dipakai).
    3. Jika ada tetapi belum terverifikasi → tolak (masih dalam antrean).
    4. Jika belum ada → hash password lalu simpan sebagai akun belum terverifikasi.

    Args:
        data_in (SignUp): Data pendaftaran (name, email, password).
        session (AsyncSession): Sesi database async.

    Returns:
        dict[str, str]: Pesan sukses pendaftaran.

    Raises:
        HTTPException: 400 jika email sudah terdaftar atau masih dalam antrean.
    """
```

> ⚠️ Pesan sukses di kode ("Kode verifikasi baru telah dikirim ke email Anda") tidak benar karena tidak ada email.
> Ganti, mis. "Pendaftaran berhasil, menunggu persetujuan admin."

✏️ **`token`** — "berlaku 3 hari" salah, dan `durasi` belum dijelaskan.

```python
async def token(user_id: uuid.UUID, durasi: int, response: Response, session: AsyncSession) -> dict[str, str]:
    """
    Membuat JWT lalu menyimpannya di cookie HttpOnly.

    Keamanan cookie:
    - httponly=True : JavaScript tidak bisa membaca token (proteksi XSS).
    - samesite="lax": proteksi dasar terhadap CSRF.
    - secure        : mengikuti settings.https (True di HTTPS).
    - max_age       : sama dengan masa berlaku token.

    Args:
        user_id (uuid.UUID): ID pengguna yang menjadi isi `sub` token.
        durasi (int): Masa berlaku token dalam HARI.
        response (Response): Response FastAPI untuk memasang cookie.
        session (AsyncSession): Sesi database untuk mengambil data pengguna.

    Returns:
        dict[str, str]: Pesan "Login berhasil".

    Raises:
        HTTPException: 401 jika user tidak ditemukan.
    """
```

> ⚠️ Satuan `durasi` adalah **hari**. Lihat B2 di laporan: `settings.access_token_expire_minutes` (menit) masih dikirim ke sini.

✏️ **`sign_in`** — "form OAuth2" dan "OTP" salah; belum menjelaskan `remember` dan status.

```python
async def sign_in(response: Response, request: SignIn, session: AsyncSession) -> dict[str, str]:
    """
    Memeriksa email dan password lalu memasang cookie login.

    Syarat masuk:
    1. Email terdaftar dan password cocok dengan hash di database.
    2. Akun sudah diverifikasi admin.
    3. Status kerja akun AKTIF.

    Lama sesi: settings.access_token_expire_minutes (bawaan 1440 menit = 1 hari), atau
    settings.remember_token_expire_days (bawaan 30 hari) jika request.remember True.

    Args:
        response (Response): Response FastAPI untuk memasang cookie token.
        request (SignIn): email, password, dan remember (body JSON).
        session (AsyncSession): Sesi database async.

    Returns:
        dict[str, str]: Pesan sukses; token ada di cookie, bukan di body.

    Raises:
        HTTPException: 401 jika email/password salah; 403 jika akun belum
            diverifikasi atau tidak aktif.
    """
```

> ⚠️ Kode sekarang berbeda dari docstring ini: syarat 2 dan 3 digabung dengan `and` sehingga pendaftar baru
> bisa masuk tanpa verifikasi, dan nilai `remember` tertukar. Perbaiki kodenya (B1 dan B2 di laporan).

✏️ **`show_not_verified`** — lupa menjelaskan `user`.

```python
async def show_not_verified(session: AsyncSession, user: Auth) -> dict[str, Any]:
    """
    (Admin) Mengambil daftar akun yang belum diverifikasi.

    Args:
        session (AsyncSession): Sesi database async.
        user (Auth): Pengguna yang memanggil; harus admin.

    Returns:
        dict[str, Any]: {"status": "success", "not_verified_users": [{"id", "email", "name"}, ...]}

    Raises:
        HTTPException: 403 jika pemanggil bukan admin.
    """
```

✏️ **`edit_auth`** — ini salinan dari fungsi reset password.

```python
async def edit_auth(edit_in: EditProfile, session: AsyncSession, user: Auth) -> None:
    """
    Mengubah nama dan/atau email milik pengguna yang sedang login.

    Hanya field yang tidak None pada `edit_in` yang diubah.

    Args:
        edit_in (EditProfile): name dan/atau email baru.
        session (AsyncSession): Sesi database async.
        user (Auth): Pengguna yang sedang login (objek yang diubah).

    Returns:
        None
    """
```

> Catatan: anotasi `-> None` tetapi kode `return await save_db(...)`; boleh, karena `save_db` mengembalikan `None`.
> Namun menulis `await save_db(...)` lalu `return` kosong lebih jelas bagi pembaca.

✏️ **`verify_email`** — OTP dan "400 jika OTP salah" tidak ada.

```python
async def verify_email(data: VerifyEmail, session: AsyncSession, user: Auth) -> dict[str, str]:
    """
    (Admin) Menandai akun sebagai terverifikasi.

    Args:
        data (VerifyEmail): Berisi email akun yang diverifikasi.
        session (AsyncSession): Sesi database async.
        user (Auth): Pengguna yang memanggil; harus admin.

    Returns:
        dict[str, str]: Pesan sukses.

    Raises:
        HTTPException: 403 jika pemanggil bukan admin; 404 jika email tidak ditemukan.
    """
```

✏️ **`logout_account`** — menyebut `request` dan 404 yang tidak ada.

```python
async def logout_account(response: Response, get_token: Logout, session: AsyncSession) -> dict[str, str]:
    """
    Mengakhiri sesi pengguna.

    Proses:
    1. Menyimpan token ke tabel BlacklistToken agar tidak bisa dipakai lagi.
    2. Menghapus cookie "access_token_inventory" dari browser.

    Args:
        response (Response): Response FastAPI untuk menghapus cookie.
        get_token (Logout): Berisi token JWT yang sedang dipakai.
        session (AsyncSession): Sesi database async.

    Returns:
        dict[str, str]: Pesan konfirmasi logout.
    """
```

🆕 **`edit_status`**

```python
async def edit_status(user_target: EditStatus, user: Auth, session: AsyncSession):
    """
    (Admin) Mengubah status kerja akun pengguna lain.

    Waktu perubahan dicatat di `riwayat_status_kerja`.

    Args:
        user_target (EditStatus): user_id akun yang diubah dan status barunya.
        user (Auth): Pengguna yang memanggil; harus admin.
        session (AsyncSession): Sesi database async.

    Returns:
        dict[str, str]: {"message": "Status akun berhasil diperbarui"}

    Raises:
        HTTPException: 403 jika pemanggil bukan admin; 404 jika user target tidak ada.
    """
```

> ⚠️ Kode juga mengubah `is_verified` menjadi False untuk status non-aktif, yang mencampur dua
> konsep (verifikasi vs status kerja). Lihat B1 di laporan. Jika diperbaiki, docstring di atas sudah benar.

---

### `backend/services/items.py`

🆕 **Docstring modul**

```python
"""
Module:
    services/items.py
Deskripsi:
    Logika bisnis data barang: baca (dengan paginasi), cari, tambah, ubah, dan hapus.
    Tambah/ubah/hapus hanya boleh dilakukan admin. Dipanggil oleh api/v1/items.py.
"""
```

✏️ **`read_items`** — `get_limit` dan `get_page` belum dijelaskan.

```python
async def read_items(session: AsyncSession, get_limit: int = 10, get_page: int = 1) -> Sequence[Item]:
    """
    Mengambil daftar barang dengan paginasi.

    Args:
        session (AsyncSession): Sesi database.
        get_limit (int): Jumlah barang per halaman. Bawaan 10.
        get_page (int): Nomor halaman, mulai dari 1. Bawaan 1.

    Returns:
        Sequence[Item]: Barang pada halaman tersebut.
    """
```

✏️ **`search_items`** — `query` bukan `str`, melainkan `ItemSearch`.

```python
async def search_items(query: ItemSearch, session: AsyncSession) -> Sequence[Item]:
    """
    Mencari barang berdasarkan nama atau SKU, tanpa peduli huruf besar/kecil.

    Args:
        query (ItemSearch): Berisi kata kunci pada field `search`.
        session (AsyncSession): Sesi database.

    Returns:
        Sequence[Item]: Barang yang nama atau SKU-nya mengandung kata kunci.
    """
```

> Catatan: pada `update_item` dan `delete_item`, docstring belum menyebut parameter `user` dan error 403/404.
> Tambahkan `user (Auth): Pengguna yang memanggil; harus admin.` dan bagian `Raises:`.
>
> ⚠️ `delete_item` mengembalikan pesan "Item dengan ID {nama}"; yang dicetak adalah nama, bukan ID.

---

### `backend/services/transactions.py`

🆕 **Docstring modul**

```python
"""
Module:
    services/transactions.py
Deskripsi:
    Logika bisnis transaksi stok: mencatat barang masuk/keluar sekaligus
    memperbarui stok barang, serta membaca riwayat transaksi.
"""
```

✏️ **`create_transaction`** — perluas dari satu baris.

```python
async def create_transaction(data: TransactionCreate, user_id: uuid.UUID, session: AsyncSession) -> Transaction:
    """
    Mencatat transaksi stok dan memperbarui stok barang.

    Baris barang dikunci (SELECT ... FOR UPDATE) selama proses, sehingga dua
    transaksi bersamaan untuk barang yang sama dijalankan bergantian, bukan
    saling menimpa (mencegah race condition pada stok). Pengunci hanya
    berpengaruh di PostgreSQL; SQLite mengabaikannya.

    Aturan:
    - "out": ditolak jika stok kurang dari jumlah yang diminta.
    - "in": stok bertambah.
    Perubahan stok dan catatan transaksi disimpan dalam satu commit.

    Args:
        data (TransactionCreate): item_id, type, quantity, dan notes.
        user_id (uuid.UUID): ID pengguna yang mencatat.
        session (AsyncSession): Sesi database async.

    Returns:
        Transaction: Catatan transaksi yang tersimpan.

    Raises:
        HTTPException: 404 jika barang tidak ada; 400 jika stok tidak mencukupi.
    """
```

✏️ **`read_transactions`** dan **`read_transaction_by_id`**

```python
async def read_transactions(session: AsyncSession, item_id: int | None = None) -> Sequence[Transaction]:
    """
    Mengambil daftar transaksi.

    Args:
        session (AsyncSession): Sesi database async.
        item_id (int | None): Jika diisi, hanya transaksi untuk barang itu.

    Returns:
        Sequence[Transaction]: Daftar transaksi (belum ada paginasi).
    """
```

```python
async def read_transaction_by_id(transaction_id: int, session: AsyncSession) -> Transaction:
    """
    Mengambil satu transaksi berdasarkan ID.

    Args:
        transaction_id (int): ID transaksi.
        session (AsyncSession): Sesi database async.

    Returns:
        Transaction: Transaksi yang ditemukan.

    Raises:
        HTTPException: 404 jika transaksi tidak ditemukan.
    """
```

---

### `debug_errors.py`

🆕 **`ContohBody`**

```python
class ContohBody(BaseModel):
    """
    Body contoh untuk /debug/validate: sengaja dikirim tidak valid agar memicu
    error 422 sungguhan. Hanya untuk uji halaman error.

    Attributes:
        nama (str): Teks bebas.
        umur (int): Harus angka; mengirim teks memicu 422.
    """
```

---

## Bagian 3 — Template untuk dipakai ke depan

**Fungsi service**
```python
async def nama_fungsi(param_a: int, session: AsyncSession) -> Hasil:
    """
    Satu kalimat: apa yang dilakukan.

    Aturan bisnis atau alasan penting (opsional).

    Args:
        param_a (int): Arti parameter.
        session (AsyncSession): Sesi database async.

    Returns:
        Hasil: Arti nilai kembalian.

    Raises:
        HTTPException: Kode dan kapan terjadi.
    """
```

**Endpoint** (tampil di `/docs`, tulis untuk pemanggil API)
```python
@router.get("/contoh/{id}")
async def contoh(id: int, ...):
    """
    Satu kalimat untuk pemakai API.

    Args:
        id (int): ID yang dicari (path).

    Raises:
        HTTPException: 404 jika tidak ditemukan.
    """
```

**Class model/skema**
```python
class Contoh(BaseModel):
    """
    Satu kalimat: untuk apa class ini.

    Attributes:
        nama (str): Arti field.
    """
```

**Modul** (paling atas file)
```python
"""
Module:
    folder/nama_file.py
Deskripsi:
    Apa isi dan peran file ini dalam alur aplikasi.
"""
```

## Bagian 4 — Cara memeriksa hasilnya

Setelah menyalin, jalankan:

```bash
python -c "import backend.services.items as m; help(m.read_items)"
```

dan buka `http://localhost:<PORT>/docs`. Docstring endpoint tampil sebagai deskripsi tiap rute.
Terakhir, baca ulang satu pertanyaan tiap docstring: **"apakah semua parameter dan error di sini
benar-benar ada di kodenya?"** Kalau jawabannya tidak, ubah salah satunya.