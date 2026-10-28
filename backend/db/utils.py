"""
Module:
    db/utils.py
Deskripsi:
    Fungsi bantu database yang dipakai lintas service: paginasi (show_db)
    dan penyimpanan objek (save_db).
"""

from typing import Any
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

async def show_db(session: AsyncSession, statement: SelectOfScalar[Any], get_limit: int = 10, page: int = 0) -> list[Any]: 
    """
    Menjalankan query SELECT dengan paginasi.

    Halaman dihitung mulai dari 1: offset = (page - 1) * get_limit.
    Nilai page di bawah 1 (termasuk bawaan 0) diperlakukan sebagai halaman 1.

    Args:
        session (AsyncSession): Sesi database.
        statement (SelectOfScalar[Any]): Query SELECT yang belum dibatasi, mis. select(Item).
        get_limit (int): Jumlah baris per halaman. Bawaan 10.
        page (int): Nomor halaman, mulai dari 1.

    Returns:
        list[Any]: Baris pada halaman tersebut (kosong jika halaman melewati data).
    """

    get_offset = max(0, (page - 1) * get_limit)
    statement = statement.offset(get_offset).limit(get_limit)
    result = await session.exec(statement)
    return list(result.all())

async def save_db(session: AsyncSession, model_object: Any) -> None:
    """
    Menyimpan (insert atau update) satu objek, lalu menyegarkannya dari database.

    Langkah: session.add() → commit() → refresh(). Setelah refresh, kolom yang diisi
    database (id, default server) sudah tersedia di objek.

    Args:
        session (AsyncSession): Sesi database.
        model_object (Any): Objek model SQLModel (tabel) yang akan disimpan.

    Note:
        commit() ikut menyimpan semua perubahan lain yang sudah di-add pada sesi yang sama.
        Itulah sebabnya create_transaction menyimpan perubahan stok dan catatan
        transaksinya sekaligus dalam satu transaksi database.
    """
    
    session.add(model_object)
    await session.commit()
    await session.refresh(model_object)
    return