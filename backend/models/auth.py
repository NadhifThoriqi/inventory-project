"""
Module:
    models/auth.py
Deskripsi:
    Mendefinisikan model database (tabel) untuk fitur autentikasi
    menggunakan SQLModel sebagai ORM.

Tables:
    auth            - Menyimpan data pengguna terdaftar.
    blacklist_token - Menyimpan token JWT yang sudah tidak berlaku (logout).
"""

import uuid
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy import func, DateTime
from sqlmodel import Field, Relationship, SQLModel

from ..core.enums import Role, Status

if TYPE_CHECKING:
    from .transaction import Transaction


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

    __tablename__: Any = "auth"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, unique=True
    )
    name: str
    email: EmailStr = Field(max_length=255, index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_verified: bool = Field(default=False)
    role: Role = Field(default=Role.STAFF, nullable=False)
    status: Status = Field(default=Status.AKTIF)
    riwayat_status_kerja: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
        nullable=False,
    )

    transaksi_dilakukan: list["Transaction"] = Relationship(back_populates="auth")


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

    __tablename__: Any = "blacklist_token"

    token: str = Field(primary_key=True, nullable=False)
    blacklisted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
        nullable=False,
    )