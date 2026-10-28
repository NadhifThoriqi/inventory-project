"""
Module:
    schemas/item.py
Deskripsi:
    Skema Pydantic untuk data barang: bentuk body request dan respons API.
"""

from pydantic import BaseModel, ConfigDict, Field

class ItemBase(BaseModel):
    """
    Module:
        schemas/item.py
    Deskripsi:
        Skema Pydantic untuk data barang: bentuk body request dan respons API.
    """

    sku: str
    name: str
    min_stock: int = Field(default=0, ge=0)
    description: str | None = None

class ItemCreate(ItemBase):
    """Body request tambah barang. Sama dengan ItemBase; `id` dibuat database."""

class ItemRead(ItemBase):
    """
    Respons data barang.

    Attributes:
        id (int): ID barang yang dibuat database.
    """
    stock: int
    id: int

class ItemSearch(BaseModel):
    """
    Body request pencarian barang.

    Attributes:
        search (str): Kata kunci (wajib, minimal 1 karakter setelah spasi di tepi dibuang).
            Dicocokkan ke nama atau SKU tanpa peduli huruf besar/kecil.
    """

    model_config = ConfigDict(str_strip_whitespace=True)
    search: str = Field(min_length=1)

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

    sku: str | None = None
    name: str | None = None
    min_stock: int | None = Field(default=None, ge=0)
    description: str | None = None
