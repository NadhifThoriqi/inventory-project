"""
Module:
    services/items.py
Deskripsi:
    Logika bisnis data barang: baca (dengan paginasi), cari, tambah, ubah, dan hapus.
    Tambah/ubah/hapus hanya boleh dilakukan admin. Dipanggil oleh api/v1/items.py.
"""

from typing import Sequence

from fastapi import HTTPException
from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.auth import Auth
from ..models.item import Item
from ..schemas.item import ItemCreate, ItemUpdate, ItemSearch
from ..db.utils import save_db, show_db


async def read_low_stock(
    session: AsyncSession,
    get_limit: int = 10,
    get_page: int = 1
) -> Sequence[Item]:
    """
    Mengambil barang yang stoknya sudah mencapai atau di bawah batas minimum.

    Syarat: stock <= min_stock. Barang yang min_stock-nya 0 hanya muncul saat
    stoknya habis (0). Urutan: yang paling kekurangan lebih dulu
    (selisih min_stock - stock terbesar), lalu berdasarkan ID.

    Args:
        session (AsyncSession): Sesi database.
        get_limit (int): Jumlah barang per halaman. Bawaan 10.
        get_page (int): Nomor halaman, mulai dari 1. Bawaan 1.

    Returns:
        Sequence[Item]: Barang yang perlu diisi ulang pada halaman tersebut.
    """
    statement = (
        select(Item)
        .where(col(Item.stock) <= col(Item.min_stock))
        .order_by((col(Item.min_stock) - col(Item.stock)).desc(), col(Item.id))
    )
    return await show_db(session, statement, get_limit=get_limit, page=get_page)


async def read_items(
    session: AsyncSession,
    get_limit: int = 10,
    get_page: int = 1
) -> Sequence[Item]:
    """
    Mengambil daftar barang dengan paginasi.

    Args:
        session (AsyncSession): Sesi database.
        get_limit (int): Jumlah barang per halaman. Bawaan 10.
        get_page (int): Nomor halaman, mulai dari 1. Bawaan 1.

    Returns:
        Sequence[Item]: Barang pada halaman tersebut.
    """

    # Contoh data item, seharusnya diambil dari database
    # items =(await session.exec(select(Item))).all()
    items = await show_db(session, select(Item), get_limit=get_limit, page=get_page)

    return items


async def read_item(
    item_id: int,
    session: AsyncSession
) -> Item:
    """
    Mengambil detail item berdasarkan ID dari database.

    Args:
        item_id (int): ID item yang akan diambil.
        session (AsyncSession): Sesi database.

    Returns:
        Item: Detail item yang diambil dari database.
    """

    item_detail: Item | None = await session.get(Item, item_id)
    
    if not item_detail:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")
    
    return item_detail


async def create_item(
    item: ItemCreate,
    session: AsyncSession,
    user: Auth
) -> Item:
    """
    Membuat item baru di database.

    Args:
        item (ItemCreate): Data item yang akan dibuat.
        session (AsyncSession): Sesi database.
        user (Auth): Objek Auth yang mewakili pengguna saat ini.

    Returns:
        Item: Item yang telah dibuat.
    """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Hanya admin yang dapat membuat item baru")
    # Cek apakah SKU sudah terdaftar
    existing_sku = (await session.exec(select(Item).where(Item.sku == item.sku))).first()
    if existing_sku:
        raise HTTPException(status_code=400, detail="SKU sudah terdaftar")
    
    new_item: Item = Item(
        sku=item.sku,
        name=item.name,
        min_stock=item.min_stock,
        description=item.description
    )

    await save_db(session, new_item)

    return new_item


async def update_item(
    item_id: int,
    item: ItemUpdate,
    session: AsyncSession,
    user: Auth
) -> Item:
    """
    Memperbarui item yang sudah ada di database.

    Args:
        item_id (int): ID item yang akan diperbarui.
        item (ItemUpdate): Data item yang akan diperbarui.
        session (AsyncSession): Sesi database.

    Returns:
        Item: Item yang telah diperbarui.
    """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Hanya admin yang dapat memperbarui item")
    
    existing_item: Item | None = await session.get(Item, item_id)

    existing_sku = (await session.exec(
        select(
            Item
        ).where(
            Item.sku == item.sku,
            Item.id != item_id
        )
    )).first()
    
    if existing_sku:
        raise HTTPException(status_code=404, detail="SKU sudah terdaftar")

    if not existing_item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    # 1. Ekstrak data yang dikirim dalam request, abaikan field yang tidak diisi (unset)
    item_data = item.model_dump(exclude_unset=True)
    
    # 2. Update model database secara otomatis dengan data baru
    existing_item.sqlmodel_update(item_data)

    await save_db(session, existing_item)

    return existing_item


async def search_items(
    query: ItemSearch,
    session: AsyncSession
) -> Sequence[Item]:
    """
    Mencari barang berdasarkan nama atau SKU, tanpa peduli huruf besar/kecil.

    Args:
        query (ItemSearch): Berisi kata kunci pada field `search`.
        session (AsyncSession): Sesi database.

    Returns:
        Sequence[Item]: Barang yang nama atau SKU-nya mengandung kata kunci.
    """
    # Agar pengguna tetap bisa menemukan barang meskipun mengetik huruf kecil/besar,
    statement = select(Item).where(
        col(Item.name).icontains(query.search) | col(Item.sku).icontains(query.search)
    )
    
    # Eksekusi dan langsung kembalikan hasilnya dalam satu baris
    return (await session.exec(statement)).all()


async def delete_item(
    item_id: int,
    session: AsyncSession,
    user: Auth
) -> dict[str, str]:
    """
    Menghapus item dari database.

    Args:
        item_id (int): ID item yang akan dihapus.
        session (AsyncSession): Sesi database.

    Returns:
        dict: Pesan konfirmasi bahwa item telah dihapus.
    """
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Hanya admin yang dapat menghapus item")

    existing_item: Item | None = await session.get(Item, item_id)

    if not existing_item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    await session.delete(existing_item)
    await session.commit()

    return {"message": f"Item dengan ID {existing_item.name} telah dihapus."}

