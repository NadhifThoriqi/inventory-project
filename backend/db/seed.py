"""
Module:
    db/seed.py
Deskripsi:
    mencaritahu apakah sudah ada user atau belum.
    jika belum ada user maka akan menambah akun admin pertama.
Author:
    Nadhif Thoriqi
"""

from sqlmodel import select

from ..db.utils import save_db
from ..core.enums import Role
from ..core.security import get_password_hash
from ..core.config import settings
from ..models.auth import Auth
from .sessions import async_session_factory

RESET = "\033[0m"
CYAN = "\033[96m"
KUNING = "\033[93m"
HIJAU = "\033[92m"

async def check_database_is_empty() -> None:
    """
    Membuat akun admin pertama jika tabel 'auth' masih kosong.

    Dipanggil saat startup. Data admin diambil dari .env (YOURNAME, EMAIL, PASSWORD).
    Jika sudah ada minimal satu pengguna, fungsi tidak melakukan apa-apa, jadi aman
    dijalankan pada setiap startup. Akun dibuat dengan peran ADMIN, status AKTIF, dan sudah terverifikasi.
    """

    async with async_session_factory() as session:
        statement = select(Auth).limit(1)
        
        # Jalankan query
        result = await session.exec(statement)
        first_row = result.first()
        
        # Jika first_row bernilai None, berarti tabel kosong
        if first_row is None:

            print(f"{CYAN}INFO{RESET}: \tBelum ada pengguna yang terdaftar.")
            print(f"{KUNING}PROSES{RESET}: \tMembuat akun admin pertama...")
            # Jika benar-external baru, buat object baru
            db_user = Auth(
                name=settings.name,
                email=settings.email,
                hashed_password=get_password_hash(settings.password),
                is_verified=True,
                role= Role.ADMIN,
            )

            await save_db(session, db_user)
            print(f"{HIJAU}SUKSES{RESET}: \tAkun admin berhasil dibuat.")
        else:
            print(f"{CYAN}INFO{RESET}: \tPengguna sudah terdaftar di database.")
            print(f"{KUNING}LEWATI{RESET}: \tPembuatan akun admin tidak diperlukan.")
        
    print(f"{HIJAU}SUKSES{RESET}: \tInisialisasi database selesai.")
    return
