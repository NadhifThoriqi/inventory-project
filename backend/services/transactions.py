"""
Module:
    services/transactions.py
Deskripsi:
    Logika bisnis transaksi stok: mencatat barang masuk/keluar sekaligus
    memperbarui stok barang, serta membaca riwayat transaksi.
"""

import uuid

from typing import Sequence
from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.enums import TypeMutasi
from ..models.item import Item
from ..models.transaction import Transaction
from ..schemas.transaction import TransactionCreate
from ..db.utils import save_db


async def create_transaction(
    data: TransactionCreate,
    user_id: uuid.UUID,  # Sesuaikan tipe data dengan tabel user (int / UUID)
    session: AsyncSession
) -> Transaction:
    """
    Mencatat transaksi stok dan memperbarui stok barang.

    Baris barang dikunci (SELECT ... FOR UPDATE) selama proses, sehingga dua
    transaksi bersamaan untuk barang yang sama dijalankan bergantian, bukan
    saling menimpa (mencegah race condition pada stok). Pengunci hanya
    berpengaruh di PostgreSQL; SQLite mengabaikannya.

    Aturan:
    - "out": ditolak jika stok kurang dari jumlah yang diminta.
    - "in": stok bertambah.
    Perubahan stok dan catatan transaksi disimpan dalam satu commit.

    Args:
        data (TransactionCreate): item_id, type, quantity, dan notes.
        user_id (uuid.UUID): ID pengguna yang mencatat.
        session (AsyncSession): Sesi database async.

    Returns:
        Transaction: Catatan transaksi yang tersimpan.

    Raises:
        HTTPException: 404 jika barang tidak ada; 400 jika stok tidak mencukupi.
    """

    # 1. Ambil item dari database
    stmt = select(Item).where(Item.id == data.item_id).with_for_update()
    item = (await session.exec(stmt)).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    # 2. Logika Mutasi Stok & Validasi Kecukupan
    if data.type == TypeMutasi.OUT:
        if item.stock < data.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Stok tidak mencukupi. Stok saat ini: {item.stock}"
            )
        item.stock -= data.quantity
    elif data.type == TypeMutasi.IN:
        item.stock += data.quantity

    # 3. Buat instance Transaction
    new_transaction = Transaction(
        item_id=data.item_id,
        user_id=user_id,
        type=data.type,
        quantity=data.quantity,
        notes=data.notes
    )

    # 4. Simpan perubahan stok item dan record transaksi baru
    session.add(item)
    await save_db(session, new_transaction)

    return new_transaction


async def read_transactions(
    session: AsyncSession,
    item_id: int | None = None
) -> Sequence[Transaction]:
    """
    Mengambil daftar transaksi.

    Args:
        session (AsyncSession): Sesi database async.
        item_id (int | None): Jika diisi, hanya transaksi untuk barang itu.

    Returns:
        Sequence[Transaction]: Daftar transaksi (belum ada paginasi).
    """

    statement = select(Transaction)
    if item_id:
        statement = statement.where(Transaction.item_id == item_id)
        
    return (await session.exec(statement)).all()


async def read_transaction_by_id(
    transaction_id: int,
    session: AsyncSession
) -> Transaction:
    """
    Mengambil satu transaksi berdasarkan ID.

    Args:
        transaction_id (int): ID transaksi.
        session (AsyncSession): Sesi database async.

    Returns:
        Transaction: Transaksi yang ditemukan.

    Raises:
        HTTPException: 404 jika transaksi tidak ditemukan.
    """
    
    transaction = await session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
        
    return transaction