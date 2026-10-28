"""
Module:
    models/transaction.py
Deskripsi:
    Model tabel 'transaction': riwayat mutasi stok (barang masuk/keluar).
"""

import uuid
from typing import Any, TYPE_CHECKING
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import func, DateTime

from ..core.enums import TypeMutasi

if TYPE_CHECKING:
    from .auth import Auth
    from .item import Item

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

    __tablename__: Any = "transaction"

    id: int | None = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id", index=True, nullable=False)
    user_id: uuid.UUID = Field(foreign_key="auth.id", index=True, nullable=False)
    
    type: TypeMutasi = Field(nullable=False)
    quantity: int
    notes: str | None = None  # Catatan tambahan tentang transaksi
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
        nullable=False,
    )

    auth: "Auth" = Relationship(back_populates="transaksi_dilakukan")
    item: "Item" = Relationship(back_populates="transaksi_list")