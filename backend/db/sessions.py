"""
Module:
    db/sessions.py
Deskripsi:
    Mengelola koneksi database: engine async, factory session, pembuatan
    tabel saat startup, dan pembuatan akun admin pertama.
Author:
    Nadhif Thoriqi
"""

from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ..core.config import settings

# Inisialisasi engine async
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,      # Menampilkan query SQL jika DEBUG=True
    future=True,
    pool_size=10,
    max_overflow=20
)

# Factory untuk membuat session async
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Dependency FastAPI untuk inject session ke routes
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency FastAPI yang menyediakan satu AsyncSession per request.

    Sesi dibuka saat request mulai dan ditutup otomatis (`async with`) ketika
    request selesai, termasuk bila terjadi error.

    Yields:
        AsyncSession: Sesi database untuk dipakai endpoint dan service.
    """

    async with async_session_factory() as session:
        yield session

async def create_engine():
    """
    Membuat semua tabel yang belum ada (SQLModel.metadata.create_all).

    Dipanggil sekali saat startup (lifespan di main.py). Hanya menambah tabel
    baru; tidak mengubah tabel yang sudah ada. Hanya model yang sudah di-import yang ikut dibuat.
    """

    async with async_engine.begin() as conn:
        # Menjalankan create_all untuk membuat tabel jika belum ada
        await conn.run_sync(SQLModel.metadata.create_all)

async def close_engine():
    """Menutup semua koneksi di pool database. Dipanggil saat shutdown aplikasi."""
    
    await async_engine.dispose()
