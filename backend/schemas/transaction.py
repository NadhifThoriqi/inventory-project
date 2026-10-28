"""
Module:
    schemas/transaction.py
Deskripsi:
    Skema Pydantic untuk transaksi stok: body request dan respons API.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from ..core.enums import TypeMutasi

class TransactionCreate(BaseModel):
    """
    Body request pencatatan transaksi stok.

    Attributes:
        item_id (int): ID barang yang dimutasi.
        type (TypeMutasi): "in" (masuk) atau "out" (keluar).
        quantity (int): Jumlah barang, harus lebih dari 0.
        notes (str | None): Catatan tambahan.
    """

    item_id: int
    type: TypeMutasi
    quantity: int = Field(gt=0, description="Kuantitas harus lebih dari 0")
    notes: str | None = None


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

    id: int
    item_id: int
    user_id: uuid.UUID
    type: TypeMutasi
    quantity: int
    notes: str | None = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
    