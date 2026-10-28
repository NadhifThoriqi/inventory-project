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

from starlette.config import Config
from pydantic import EmailStr, TypeAdapter

config = Config(".env")


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
        not_remember_token_expire (int): Masa berlaku token biasa, dalam 1 HARI.
        remember_token_expire (int): Masa berlaku token "ingat saya", dalam 30 HARI.
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
            KeyError: Jika variabel admin pertama (YOURNAME, EMAIL, PASSWORD) tidak ada.
        """
        # 1. Parsing variabel wajib (tanpa default)
        try:
            self.database_url: str = config("DATABASE_URL", cast=str)
            self.secret_key: str = config("SECRET_KEY", cast=str)
        except KeyError as e:
            # Menangkap variabel yang lupa ditulis sama sekali di .env
            raise RuntimeError(f"Konfigurasi wajib tidak ditemukan di .env: {e}") from e

        # 2. Parsing variabel opsional (dengan nilai default yang benar)
        self.project_name: str = config("PROJECT_NAME", cast=str, default="FastAPI App")
        self.port: int = config("PORT", cast=int, default=8000)
        self.debug: bool = config("DEBUG", cast=bool, default=False)

        # --- Auth / JWT ---
        self.algorithm: str = config("ALGORITHM", cast=str, default="HS256")
        self.not_remember_token_expire: int = config(
            "NOT_REMEMBER_TOKEN_EXPIRE", cast=int, default=1
        )
        self.remember_token_expire: int = config(
            "REMEMBER_TOKEN_EXPIRE", cast=int, default=30
        )
        self.cookie_secure: bool = config("COOKIE_SECURE", cast=bool, default=False)

        # --- Network / Domain ---
        self.https: bool = config("HTTPS", cast=bool, default=False)
        self.domain: str | None = config("DOMAIN", default=None)

        # --- Admin Pertama ---
        self.name: str = config("YOURNAME", cast=str)
        self.email: EmailStr = config("EMAIL", cast=TypeAdapter(EmailStr).validate_python)
        self.password: str = config("PASSWORD", cast=str)

        # 3. Validasi isi (mencegah variabel ada tapi nilainya kosong "")
        self._validate_not_empty()


    def _validate_not_empty(self) -> None:
        """Memastikan variabel krusial tidak berupa string kosong."""
        if not self.secret_key.strip():
            raise RuntimeError("CRITICAL: 'SECRET_KEY' di .env tidak boleh kosong!")
        
        if not self.database_url.strip():
            raise RuntimeError("CRITICAL: 'DATABASE_URL' di .env tidak boleh kosong!")

settings = AppConfig()