"""
Module:
    services/auth.py
Deskripsi:
    Logika bisnis autentikasi: pendaftaran, login (JWT di cookie HttpOnly),
    logout (blacklist token), verifikasi dan pengelolaan akun oleh admin.
    Dipanggil oleh endpoint di api/v1/auth.py.
Author:
    Nadhif Thoriqi
"""

import uuid
from typing import Sequence
from datetime import timedelta, datetime, timezone

from fastapi import HTTPException, Response, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.security import (create_access_token,
                             get_password_hash, verify_password)
from ..core.enums import Status, Role
from ..db.utils import save_db
from ..core.config import settings
from ..models.auth import Auth, BlacklistToken
from ..schemas.auth import (
    EditStatus, SignIn,
    SignUp, EditProfile,
    VerifyEmail, CookieToken,
    Logout
)


async def sign_up(
    data_in: SignUp,
    session: AsyncSession
) -> dict[str, str]:
    """
    Mendaftarkan akun baru ke antrean verifikasi.

    Alur:
    1. Cari akun dengan email yang sama.
    2. Jika ada dan sudah terverifikasi → tolak (email sudah dipakai).
    3. Jika ada tetapi belum terverifikasi → tolak (masih dalam antrean).
    4. Jika belum ada → hash password lalu simpan sebagai akun belum terverifikasi.

    Args:
        data_in (SignUp): Data pendaftaran (name, email, password).
        session (AsyncSession): Sesi database async.

    Returns:
        dict[str, str]: Pesan sukses pendaftaran.

    Raises:
        HTTPException: 400 jika email sudah terdaftar atau masih dalam antrean.
    """

    # 1. Cari user berdasarkan email
    result = await session.exec(select(Auth).where(Auth.email == data_in.email))
    existing_user = result.first()

    # 2. Logika Pengecekan
    if existing_user:
        if existing_user.is_verified:
            # Jika sudah verifikasi, baru kita larang (Email benar-benar terpakai)
            raise HTTPException(status_code=400, detail="Email sudah terdaftar. Silahkan menggunakan alamat email yang lain")
        else:
            raise HTTPException(status_code=400, detail="Email masih dalam antrian pendaftar. Silahkan tunggu beberapa saat lagi")

    else:
        # Jika benar-external baru, buat object baru
        db_user = Auth(
            name=data_in.name,
            email=data_in.email,
            hashed_password=get_password_hash(data_in.password),
            is_verified=False,
        )

    # 3. Eksekusi Perubahan
    await save_db(session, db_user)

    return {
        "status": "success",
        "message": "Pendaftaran berhasil, menunggu persetujuan admin.",
    }


async def token(
    user_id: uuid.UUID,
    durasi: int,
    response: Response,
    session: AsyncSession
) -> dict[str, str]:
    """
    Membuat JWT lalu menyimpannya di cookie HttpOnly.

    Keamanan cookie:
    - httponly=True : JavaScript tidak bisa membaca token (proteksi XSS).
    - samesite="lax": proteksi dasar terhadap CSRF.
    - secure        : mengikuti settings.https (True di HTTPS).
    - max_age       : sama dengan masa berlaku token.

    Args:
        user_id (uuid.UUID): ID pengguna yang menjadi isi `sub` token.
        durasi (int): Masa berlaku token dalam HARI.
        response (Response): Response FastAPI untuk memasang cookie.
        session (AsyncSession): Sesi database untuk mengambil data pengguna.

    Returns:
        dict[str, str]: Pesan "Login berhasil".

    Raises:
        HTTPException: 401 jika user tidak ditemukan.
    """
    
    user = await session.get(Auth, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User tidak ditemukan di database.")

    # Sinkronkan durasi JWT dan cookie (dalam satuan detik dan datetime)
    token_delta = timedelta(days=durasi)
    max_age_seconds = int(token_delta.total_seconds())
    expire_date = datetime.now(timezone.utc) + token_delta

    token_data: CookieToken = CookieToken(
        sub=str(user_id),  # Tetap gunakan ID sebagai acuan utama
        email=user.email,  # Sertakan email untuk kebutuhan instan di frontend
        name=user.name,  # Sertakan name untuk kebutuhan instan di frontend
        type="access",  # Penanda bahwa ini token login biasa, BUKAN token reset password
    )

    access_token = str(
        create_access_token(data=token_data, expires_delta=token_delta)
    )

    # Simpan token ke Cookie (HTTPOnly untuk keamanan)
    response.set_cookie(
        key="access_token_inventory",
        value=access_token,
        httponly=True,            # JavaScript tidak bisa mengakses cookie
        max_age=max_age_seconds,  # Integer dalam detik
        expires=expire_date,      # Datetime UTC
        samesite="lax",           # Proteksi dasar CSRF
        secure=settings.https,    # Ubah ke True jika sudah HTTPS
        domain=settings.domain,   # biarkan None, jangan diisi manual
        path="/"                 # ← wajib "/" agar berlaku di semua halaman
    )

    return {"status": "success", "message": "Login berhasil"}


async def sign_in(
    response: Response,
    request: SignIn,
    session: AsyncSession,
) -> dict[str, str]:
    """
    Memeriksa email dan password lalu memasang cookie login.

    Syarat masuk:
    1. Email terdaftar dan password cocok dengan hash di database.
    2. Akun sudah diverifikasi admin.
    3. Status kerja akun AKTIF.

    Lama sesi: settings.not_remember_token_expire (bawaan 1 hari), atau
    settings.remember_token_expire (bawaan 30 hari) jika request.remember True.

    Args:
        response (Response): Response FastAPI untuk memasang cookie token.
        request (SignIn): email, password, dan remember (body JSON).
        session (AsyncSession): Sesi database async.

    Returns:
        dict[str, str]: Pesan sukses; token ada di cookie, bukan di body.

    Raises:
        HTTPException: 401 jika email/password salah; 403 jika akun belum
            diverifikasi atau tidak aktif.
    """

    # Cari user berdasarkan email
    result = await session.exec(select(Auth).where(Auth.email == request.email))
    user_found = result.first()

    # Validasi user dan password
    if not user_found or not verify_password(
        request.password, user_found.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password anda salah",
        )

    # TAMBAHAN: Cek apakah user sudah verifikasi email
    if not user_found.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun Anda belum disetujui admin.",
        )

    if user_found.status != Status.AKTIF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun Anda sudah tidak aktif.",
        )

    if request.remember: 
        durasi = settings.remember_token_expire
    else:
        durasi = settings.not_remember_token_expire

    return await token(
        user_id=user_found.id,
        durasi=durasi,
        response=response,
        session=session
        )


async def show_not_verified(
    session: AsyncSession,
    user: Auth
) -> Sequence[Auth]:
    """
    (Admin) Mengambil daftar akun yang belum diverifikasi.

    Args:
        session (AsyncSession): Sesi database async.
        user (Auth): Pengguna yang memanggil; harus admin.

    Returns:
        dict[str, Any]: {"status": "success", "not_verified_users": [{"id", "email", "name"}, ...]}

    Raises:
        HTTPException: 403 jika pemanggil bukan admin.
    """

    if user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya admin yang dapat melihat akun yang belum diverifikasi.")
    
    result = await session.exec(select(Auth).where(Auth.is_verified == False))

    return result.all()


async def edit_auth(
    edit_in: EditProfile, 
    session: AsyncSession, 
    user: Auth
) -> dict[str, str]:
    """
    Mengubah nama dan/atau email milik pengguna yang sedang login.

    Hanya field yang tidak None pada `edit_in` yang diubah.

    Args:
        edit_in (EditProfile): name dan/atau email baru.
        session (AsyncSession): Sesi database async.
        user (Auth): Pengguna yang sedang login (objek yang diubah).

    Returns:
        None
    """

    auth = (await session.exec(
        select(
            Auth
        ).where(
            Auth.email == edit_in.email,
            Auth.id != user.id
        )
    )).first()

    if auth:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    # Update fields secara dinamis jika dikirimkan
    if edit_in.email is not None:
        user.email = edit_in.email
    if edit_in.name is not None:
        user.name = edit_in.name

    # Memastikan data hanya disimpan jika objek user berhasil ditemukan/dimodifikasi
    await save_db(session, user)
    return {"status": "success", "message": f"Data berhasil diganti"}


async def verify_email(
    data: VerifyEmail,
    session: AsyncSession,
    user: Auth
) -> dict[str, str]:
    """
    Mengubah nama dan/atau email milik pengguna yang sedang login.

    Hanya field yang tidak None pada `edit_in` yang diubah.

    Args:
        edit_in (EditProfile): name dan/atau email baru.
        session (AsyncSession): Sesi database async.
        user (Auth): Pengguna yang sedang login (objek yang diubah).

    Returns:
        None
    """

    if user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Akses ditolak. Hanya admin yang dapat melakukan verifikasi email.")
    
    # Cari user berdasarkan email
    result = await session.exec(select(Auth).where(Auth.email == data.email))
    user_found = result.first()

    if not user_found:
        raise HTTPException(status_code=404, detail="Email tidak ditemukan")

    # Tandai user sebagai terverifikasi
    user_found.is_verified = data.is_verified
    await save_db(session, user_found)

    return {"status": "success", "message": "Email berhasil diverifikasi"}


async def sign_out_account(
    response: Response,
    get_token: Logout,
    session: AsyncSession
) -> dict[str, str]:
    """
    Mengakhiri sesi pengguna.

    Proses:
    1. Menyimpan token ke tabel BlacklistToken agar tidak bisa dipakai lagi.
    2. Menghapus cookie "access_token_inventory" dari browser.

    Args:
        response (Response): Response FastAPI untuk menghapus cookie.
        get_token (Logout): Berisi token JWT yang sedang dipakai.
        session (AsyncSession): Sesi database async.

    Returns:
        dict[str, str]: Pesan konfirmasi logout.
    """

    # Tambahkan token ke blacklist
    new_blacklist = BlacklistToken(token=get_token.token)
    await save_db(session, new_blacklist)

    # Hapus cookie
    response.delete_cookie(
        key="access_token_inventory",
        httponly=True,
        samesite="lax",
        secure=settings.https,
        domain=settings.domain,
        path="/"
    )

    return {"status": "success", "message": "Berhasil logout"}


async def edit_status(
    user_target: EditStatus,
    user: Auth,
    session: AsyncSession
):
    """
    (Admin) Mengubah status kerja akun pengguna lain.

    Waktu perubahan dicatat di `riwayat_status_kerja`.

    Args:
        user_target (EditStatus): user_id akun yang diubah dan status barunya.
        user (Auth): Pengguna yang memanggil; harus admin.
        session (AsyncSession): Sesi database async.

    Returns:
        dict[str, str]: {"message": "Status akun berhasil diperbarui"}

    Raises:
        HTTPException: 403 jika pemanggil bukan admin; 404 jika user target tidak ada.
    """

    if user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Hanya admin yang dapat mengubah status akun pengguna")
    
    current_time = datetime.now(timezone.utc)
    user_to_edit = await session.get(Auth, user_target.user_id)  # Pastikan user target ada di database
    
    if user_to_edit is None:
        raise HTTPException(status_code=404, detail="User target tidak ditemukan")
    
    user_to_edit.status = user_target.status
    user_to_edit.riwayat_status_kerja = current_time
    
    await save_db(session, user_to_edit)
    return {"message": "Status akun berhasil diperbarui"}
