"""
Module:
    api/v1/auth.py
Deskripsi:
    Endpoint HTTP untuk autentikasi dan manajemen akun. Lapisan ini hanya
    menerima request dan memeriksa login lewat dependency, lalu meneruskan
    pekerjaan ke services/auth.py.

Endpoints (prefix /thorix-api/v1/auth):
    GET    /me                - Data pengguna yang sedang login.
    POST   /sign-up           - Daftar akun baru (menunggu persetujuan admin).
    POST   /sign-in           - Masuk; token JWT disimpan di cookie HttpOnly.
    DELETE /sign-out           - Keluar; token dimasukkan ke blacklist.
    PATCH  /edit-profile      - Ubah nama dan/atau email sendiri.
    POST   /show-not-verified - (Admin) Daftar akun yang belum diverifikasi.
    POST   /verify-email      - (Admin) Verifikasi akun berdasarkan email.
    PATCH  /edit-status       - (Admin) Ubah status kerja akun pengguna lain.
"""

from typing import Sequence
from fastapi import APIRouter, Depends, Response
from sqlmodel.ext.asyncio.session import AsyncSession

from ...core.security import get_current_user
from ...db.sessions import get_session
from ...models.auth import Auth
from ...schemas.auth import (ShowMe, SignIn,
                             SignUp, EditProfile,
                             VerifyEmail, EditStatus,
                             Logout)
from ...services.auth import edit_auth as ea
from ...services.auth import sign_out_account as soa
from ...services.auth import sign_in as si
from ...services.auth import sign_up as up
from ...services.auth import verify_email as ve
from ...services.auth import edit_status as es
from ...services.auth import show_not_verified as snv

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me", response_model=ShowMe)
async def read_users_me(
    user: Auth = Depends(get_current_user())
) -> Auth:
    """
    Mengambil data profil pengguna yang sedang login.

    Returns:
        Auth: Data pengguna, dibentuk sesuai skema ShowMe (id, email, name, role).

    Raises:
        HTTPException: 401 jika belum login, token kedaluwarsa, atau sudah logout.
    """
    return user


@router.post("/show-not-verified", response_model=Sequence[ShowMe])
async def show_not_verified(
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> Sequence[Auth]:
    """
    (Admin) Menampilkan akun yang belum diverifikasi.

    Berguna untuk melihat antrean pendaftar yang menunggu persetujuan.

    Returns:
        dict: {"status": "success",
               "not_verified_users": [{"id", "email", "name"}, ...]}

    Raises:
        HTTPException: 403 jika pemanggil bukan admin.
    """
    return await snv(session, user)


@router.post("/sign-up")
async def sign_up(
    data_in: SignUp,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """
    Mendaftarkan akun baru dengan peran staff.

    Akun baru belum terverifikasi dan masuk antrean; admin harus memverifikasinya
    lewat POST /auth/verify-email sebelum akun itu bisa masuk.

    Args:
        data_in (SignUp): name, email, dan password. Password minimal 8 karakter
            dan mengandung huruf besar, huruf kecil, angka, serta simbol.

    Returns:
        dict[str, str]: Pesan sukses pendaftaran.

    Raises:
        HTTPException: 400 jika email sudah terdaftar atau masih dalam antrean.
    """
    return await up(data_in, session)


@router.post("/sign-in")
async def sign_in(
    response: Response,
    request: SignIn,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """
    Masuk dengan email dan password.

    Jika berhasil, server menyimpan JWT di cookie HttpOnly "access_token_inventory".
    Frontend tidak perlu menyimpan token sendiri; browser mengirim cookie itu otomatis.

    Args:
        response (Response): Dipakai server untuk memasang cookie.
        request (SignIn): email, password, dan remember (True = sesi lebih lama).
            Catatan: ini adalah body JSON, bukan objek Request milik FastAPI.

    Returns:
        dict[str, str]: Pesan "Login berhasil".

    Raises:
        HTTPException: 401 jika email atau password salah.
            403 jika akun belum diverifikasi atau statusnya tidak aktif.
    """
    return await si(response, request, session)


@router.post("/verify-email")
async def verify_email(
    data: VerifyEmail,
    session: AsyncSession = Depends(get_session),
    user: Auth = Depends(get_current_user())
) -> dict[str, str]:
    """
    (Admin) Memverifikasi akun pendaftar berdasarkan email.

    Args:
        data (VerifyEmail): Email akun yang akan diverifikasi.

    Returns:
        dict[str, str]: Pesan sukses.

    Raises:
        HTTPException: 403 jika pemanggil bukan admin; 404 jika email tidak ditemukan.
    """
    return await ve(data, session, user)


@router.delete("/sign-out")
async def sign_out(
    response: Response,
    get_token: Logout = Depends(get_current_user(return_user_object=False)),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """
    Mengakhiri sesi pengguna (logout).

    Token yang sedang dipakai dimasukkan ke blacklist sehingga tidak bisa dipakai
    lagi walau belum kedaluwarsa, lalu cookie "access_token_inventory" dihapus dari browser.

    Returns:
        dict[str, str]: Pesan konfirmasi logout.

    Raises:
        HTTPException: 401 jika belum login atau token sudah tidak berlaku.
    """
    return await soa(response, get_token, session)


@router.patch("/edit-profile")
async def edit_profile(
    edit_in: EditProfile,
    user: Auth = Depends(get_current_user()),
    session: AsyncSession = Depends(get_session)
):
    """
    Mengubah nama dan/atau email milik pengguna yang sedang login.

    Hanya field yang dikirim yang diubah; field yang tidak dikirim dibiarkan.

    Args:
        edit_in (EditProfile): name dan/atau email baru (keduanya opsional).

    Returns:
        None: Respons berisi null jika berhasil.

    Raises:
        HTTPException: 401 jika belum login.
    """
    return await ea(edit_in, session, user)


@router.patch("/edit-status")
async def edit_status(
    user_target: EditStatus,
    user: Auth = Depends(get_current_user()),
    session: AsyncSession = Depends(get_session)
) -> dict[str, str]:
    """
    (Admin) Mengubah status kerja akun pengguna lain.

    Args:
        user_target (EditStatus): user_id akun yang diubah dan status barunya
            (aktif, resign, phk, atau pensiun).

    Returns:
        dict[str, str]: Pesan konfirmasi.

    Raises:
        HTTPException: 403 jika pemanggil bukan admin; 404 jika user target tidak ada.
    """
    return await es(user_target, user, session)