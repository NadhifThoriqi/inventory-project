"""
Module:
    api/v1/transactions.py
Deskripsi:
    Endpoint HTTP untuk transaksi stok (barang masuk/keluar). Butuh login.

Endpoints (prefix /thorix-api/v1/transactions):
    POST /                   - Catat transaksi baru dan sesuaikan stok barang.
    GET  /                   - Daftar transaksi (opsional ?item_id=).
    GET  /{transaction_id}   - Detail satu transaksi.
"""

from typing import Sequence
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ...db.sessions import get_session
from ...core.security import get_current_user
from ...models.auth import Auth
from ...models.transaction import Transaction
from ...schemas.transaction import TransactionCreate, TransactionRead
from ...services.transactions import (
    create_transaction as service_create,
    read_transactions as service_read_all,
    read_transaction_by_id as service_read_by_id,
)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.post("/", response_model=TransactionRead)
async def create_transaction(
    transaction: TransactionCreate,
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Transaction:
    """
    Mencatat transaksi stok dan memperbarui stok barang dalam satu langkah.

    Pelaku transaksi diambil dari pengguna yang sedang login.

    Args:
        transaction (TransactionCreate): item_id, type ("in"/"out"), quantity (> 0), dan notes (opsional).

    Returns:
        Transaction: Catatan transaksi yang tersimpan.

    Raises:
        HTTPException: 404 jika barang tidak ada; 400 jika stok tidak cukup untuk transaksi "out".
    """
    return await service_create(transaction, user.id, session)


@router.get("/", response_model=Sequence[TransactionRead])
async def read_transactions(
    item_id: int | None = None,
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Sequence[Transaction]:
    """
    Menampilkan daftar transaksi.

    Args:
        item_id (int | None): Jika diisi, hanya transaksi untuk barang itu. Bawaan semua.

    Returns:
        Sequence[Transaction]: Daftar transaksi.
    """
    return await service_read_all(session, item_id=item_id)


@router.get("/{transaction_id}", response_model=TransactionRead)
async def read_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Transaction:
    """
    Menampilkan detail satu transaksi.

    Args:
        transaction_id (int): ID transaksi.

    Raises:
        HTTPException: 404 jika transaksi tidak ditemukan.
    """
    return await service_read_by_id(transaction_id, session)