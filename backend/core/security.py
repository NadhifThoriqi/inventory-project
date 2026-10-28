"""
Module:
    core/security.py
Deskripsi:
    Menyediakan utilitas keamanan inti aplikasi, meliputi:
    - Hashing dan verifikasi password menggunakan bcrypt.
    - Pembuatan dan dekoding JWT access token.
    - Ekstraksi token dari request (cookie atau Authorization header).
    - Validasi pengguna aktif dari token JWT.
"""

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from .config import settings
from fastapi import HTTPException, status, Cookie, Header, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.auth import Auth, BlacklistToken
from ..db.sessions import get_session
from ..schemas.auth import CookieToken, Logout

ALGORITHM = settings.algorithm  # Algoritma JWT yang digunakan, misal "HS256"


def get_password_hash(
    password: str
) -> str:
    """
    Menghasilkan hash password dengan salt.

    Format penyimpanan:
    salt$hash

    Args:
        password (str): Password plaintext yang akan di-hash.

    Returns:
        str: String hash password yang aman untuk disimpan di database.
    """

    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verifikasi password saat login.

    Args:
        plain_password (str): Password plaintext yang dimasukkan pengguna.
        hashed_password (str): Hash password yang tersimpan di database.

    Returns:
        bool: True jika password cocok, False jika tidak cocok.
    """

    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    data: CookieToken, expires_delta: timedelta
) -> bytes:
    """
    Membuat JWT access token.

    Isi token berasal dari `data` ditambah klaim "exp" (waktu kedaluwarsa),
    lalu ditandatangani dengan SECRET_KEY memakai algoritma dari settings.

    Args:
        data (CookieToken): Isi token: sub (ID user), email, name, dan type ("access").
        expires_delta (timedelta): Lama token berlaku sejak dibuat.

    Returns:
        str: JWT yang sudah dienkode.
    """
    to_encode = data.model_dump()  # Mengambil data dari Pydantic model sebagai dict

    # Gunakan timezone-aware datetime agar lebih akurat dan aman
    expire = datetime.now(timezone.utc) + expires_delta

    # Payload JWT
    to_encode.update({"exp": expire, "jti": uuid.uuid4().hex})

    # Encode menggunakan PyJWT
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.secret_key,
        algorithm=ALGORITHM
    )
    return encoded_jwt


async def _get_cookie(
    session: AsyncSession, 
    return_user_object: bool,
    access_token_inventory: str | None = Cookie(None), 
    authorization: str | None = Header(None)
) -> CookieToken | Logout:
    """
    Mengambil token JWT dari request lalu memvalidasinya.

    Urutan pencarian: cookie "access_token_inventory" dulu; jika tidak ada,
    header "Authorization: Bearer <token>".

    Args:
        session (AsyncSession): Sesi database, dipakai untuk mengecek blacklist.
        access_token_inventory (str | None): Nilai cookie login.
        authorization (str | None): Isi header Authorization.
        return_user_object (bool | None): True = token di-decode dan dikembalikan sebagai
            CookieToken. False = token diverifikasi lalu dibungkus Logout (dipakai oleh logout).

    Returns:
        CookieToken | Logout: Isi token yang valid, atau token mentah.

    Raises:
        HTTPException: 401 jika token tidak ada, sudah di-blacklist, kedaluwarsa, atau rusak.
    """
    
    token = access_token_inventory or (authorization.split(" ")[1] 
        if authorization and authorization.startswith("Bearer ")
        else None
    )

    if not token:
        raise HTTPException(status_code=401, detail="Log in dulu yuk")
    
    if await session.get(BlacklistToken, token) is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sudah tidak berlaku (sudah logout)",
        )
    try:
        payload = jwt.decode(jwt=token, key=settings.secret_key, algorithms=[ALGORITHM])
        return CookieToken(**payload) if return_user_object else Logout(token=token)


    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token sudah kadaluwarsa, silakan login ulang"
        )
    
    except (jwt.InvalidTokenError, jwt.PyJWTError):
        raise HTTPException(
            status_code=401,
            detail="Token rusak atau tidak valid"
        )


def get_current_user(return_user_object: bool | None = True):
    """
    Membuat dependency FastAPI untuk mengambil pengguna yang sedang login.

    Ini fungsi "pabrik": dipanggil saat mendefinisikan endpoint, dan hasilnya
    (fungsi `dependency`) yang dijalankan FastAPI pada setiap request.

        user  = Depends(get_current_user())                           # objek Auth
        token = Depends(get_current_user(return_user_object=False))   # token mentah (logout)

    Args:
        return_user_object (bool | None): True (bawaan) = kembalikan objek Auth dari database.
            False = kembalikan token mentah tanpa mengambil user, khusus untuk logout.

    Returns:
        Callable: Fungsi dependency async yang mengembalikan Auth atau Logout.
    """

    async def dependency(
        session: AsyncSession = Depends(get_session), 
        access_token_inventory: str | None = Cookie(None), 
        authorization: str | None = Header(None),
    ) -> Auth | Logout:
        """
        Memvalidasi token pada request ini dan mengembalikan pemiliknya.

        Raises:
            HTTPException: 401 jika belum login, token tidak valid/kedaluwarsa/di-blacklist,
                tipe token bukan "access", atau user tidak ada di database.
        """

        return_object = True if return_user_object is None else return_user_object

        payload = await _get_cookie(session, return_object, access_token_inventory, authorization)
        # Pastikan tipe token adalah untuk login/access, bukan reset_password
        
        try:
            if isinstance(payload, Logout):
                return payload
            
            if payload.type != "access":
                raise HTTPException(
                    status_code=401, detail="Tipe token tidak valid untuk login"
                )

            token_id: uuid.UUID = uuid.UUID(payload.sub)
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Token tidak valid atau rusak")

        user = await session.get(Auth, token_id)
        if not user:
            raise HTTPException(status_code=401, detail="User tidak ditemukan")

        return user  # Mengembalikan objek Auth

    return dependency
