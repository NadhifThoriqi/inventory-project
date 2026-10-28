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

from typing import Sequence

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from ...db.sessions import get_session
from ...core.security import get_current_user
from ...models.auth import Auth
from ...models.item import Item
from ...schemas.item import ItemCreate, ItemUpdate, ItemRead, ItemSearch
from ...services.items import (
    read_items as ri,
    read_item as rdi,
    create_item as ci,
    update_item as ui,
    delete_item as di,
    search_items as si,
    read_low_stock as rls
)

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)

@router.get("/", response_model=Sequence[ItemRead])
async def read_items(
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Sequence[Item]:
    """
    Mengambil daftar barang dengan paginasi.

    Args:
        limit (int): Jumlah barang per halaman, 1–100. Bawaan 10.
        page (int): Nomor halaman, mulai dari 1. Bawaan 1.

    Returns:
        Sequence[ItemRead]: Barang pada halaman tersebut (kosong jika halaman melewati data).
    """
    items: Sequence[Item] = await ri(session=session, get_limit=limit, get_page=page)
    
    return items


@router.post("/", response_model=ItemRead)
async def create_item(
    item: ItemCreate,
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Item:
    """
    Membuat item baru dan menyimpannya ke database.

    Args:
        item (ItemCreate): Data item yang akan dibuat.
        session (AsyncSession): Sesi database.
        user (Auth): Objek Auth yang mewakiti pengguna saat ini.

    Returns:
        Item: Item yang baru dibuat.
    """
    new_item: Item = await ci(item, session, user)
    
    return new_item


@router.put("/update/{item_id}", response_model=ItemRead)
async def update_item(
    item_id: int,
    item: ItemUpdate,
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Item:
    """
    Memperbarui item yang sudah ada di database.

    Args:
        item_id (int): ID item yang akan diperbarui.
        item (ItemUpdate): Data item yang akan diperbarui.
        session (AsyncSession): Sesi database.
        user (Auth): Objek Auth yang mewakili pengguna saat ini.

    Returns:
        Item: Item yang telah diperbarui.
    """
    # Contoh pembaruan item, seharusnya diperbarui di database
    updated_item: Item = await ui(item_id, item, session, user)

    return updated_item


@router.delete("/delete/{item_id}", response_model=dict[str, str])
async def delete_item(
    item_id: int,
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> dict[str, str]:
    """
    Menghapus item dari database.

    Args:
        item_id (int): ID item yang akan dihapus.
        session (AsyncSession): Sesi database.
        user (Auth): Objek Auth yang mewakili pengguna saat ini.

    Returns:
        dict: Pesan konfirmasi bahwa item telah dihapus.
    """
    return await di(item_id, session, user)


@router.get("/detail/{item_id}", response_model=ItemRead)
async def read_item(
    item_id: int,
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Item:
    """
    Mengambil detail item berdasarkan ID dari database.

    Args:
        item_id (int): ID item yang akan diambil.
        session (AsyncSession): Sesi database.
        user (Auth): Objek Auth yang mewakili pengguna saat ini.

    Returns:
        Item: Detail item yang diambil dari database.
    """
    # Contoh pengambilan detail item, seharusnya diambil dari database
    item_detail: Item = await rdi(item_id, session)
    return item_detail


@router.post("/search/", response_model=Sequence[ItemRead])
async def search_items(
    search: ItemSearch,
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Sequence[Item]:
    """
    Mencari item berdasarkan search di database.

    Args:
        search (ItemSearch): Parameter pencarian.
        session (AsyncSession): Sesi database.
        user (Auth): Objek Auth yang mewakili pengguna saat ini.

    Returns:
        Sequence[ItemRead]: Daftar item yang sesuai dengan search pencarian.
    """
    # Contoh pencarian item, seharusnya dicari di database
    search_results: Sequence[Item] = await si(search, session)

    return search_results

@router.get("/low-stock", response_model=Sequence[ItemRead])
async def read_low_stock(
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Sequence[Item]:
    """
    Menampilkan barang yang stoknya sudah mencapai atau di bawah batas minimum.

    Args:
        limit (int): Jumlah barang per halaman, 1–100. Bawaan 10.
        page (int): Nomor halaman, mulai dari 1. Bawaan 1.

    Returns:
        Sequence[ItemRead]: Barang yang perlu diisi ulang, yang paling kekurangan lebih dulu.
    """
    return await rls(session=session, get_limit=limit, get_page=page)