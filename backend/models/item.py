"""
Module:
    models/item.py
Deskripsi:
    Model tabel 'item' (barang inventori).
"""

from typing import Any, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .transaction import Transaction


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

    __tablename__: Any = "item"

    id: int | None = Field(default=None, primary_key=True)
    sku: str = Field(max_length=100, index=True, unique=True)
    name: str = Field(max_length=255, index=True)
    stock: int = Field(default=0)
    min_stock: int = Field(default=0)
    description: str | None = None

    transaksi_list: list["Transaction"] = Relationship(back_populates="item")
