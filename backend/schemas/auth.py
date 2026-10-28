"""
Module:
    schemas/auth.py
Deskripsi:
    Mendefinisikan skema Pydantic (DTO - Data Transfer Object) untuk
    validasi dan serialisasi data request/response pada fitur autentikasi.
    Skema ini digunakan sebagai kontrak data antara client dan API.
"""

import uuid
import re
from typing import Annotated

from pydantic import BaseModel, EmailStr, AfterValidator

from ..core.enums import Status


def validate_password_strength(v: str) -> str:
    """
    Memeriksa kekuatan password saat pendaftaran.

    Aturan: minimal 8 karakter; mengandung huruf besar, huruf kecil, angka,
    dan satu simbol (karakter apa pun selain huruf dan angka).

    Args:
        v (str): Password yang diperiksa.

    Returns:
        str: Password yang sama jika lolos.

    Raises:
        ValueError: Berisi aturan yang dilanggar. Pydantic mengubahnya menjadi
            respons 422 dengan pesan "Value error, <pesan>".
    """

    if len(v) < 8:
        raise ValueError("Password minimal harus 8 karakter.")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Password harus mengandung setidaknya satu huruf besar.")
    if not re.search(r"[a-z]", v):
        raise ValueError("Password harus mengandung setidaknya satu huruf kecil.")
    if not re.search(r"\d", v):
        raise ValueError("Password harus mengandung setidaknya satu angka.")
    if not re.search(r"[^A-Za-z0-9]", v):
        raise ValueError("Password harus mengandung setidaknya satu simbol khusus.")
    return v

class SignUp(BaseModel):
    """
    Body request pendaftaran akun baru.

    Attributes:
        name (str): Nama lengkap.
        email (EmailStr): Alamat email (format divalidasi otomatis).
        password (str): Password; harus lolos validate_password_strength.
    """

    name: str
    email: EmailStr
    password: Annotated[
        str, 
        AfterValidator(validate_password_strength)
    ]
        

class SignIn(BaseModel):
    """
    Body request login.

    Attributes:
        email (EmailStr): Alamat email akun.
        password (str): Password asli (plaintext); dibandingkan dengan hash di database.
        remember (bool): True = sesi lebih lama ("ingat saya"). Bawaan False.
    """

    email: EmailStr
    password: str
    remember: bool = False


class EditProfile(BaseModel):
    """
    Body request ubah profil. Hanya field yang dikirim yang diubah.

    Attributes:
        email (EmailStr | None): Email baru, atau None untuk tidak mengubah.
        name (str | None): Nama baru, atau None untuk tidak mengubah.
    """

    email: EmailStr|None = None
    name: str|None = None


class ShowMe(BaseModel):
    """
    Respons data profil pengguna yang sedang login (GET /auth/me).

    Attributes:
        id (uuid.UUID): ID unik pengguna.
        email (EmailStr): Alamat email.
        name (str): Nama pengguna.
        role (str): Peran pengguna (admin/staff).
    """

    id: uuid.UUID
    email: EmailStr
    name: str
    role: str


class VerifyEmail(BaseModel):
    """
    Body request verifikasi akun oleh admin.

    Attributes:
        email (EmailStr): Email akun yang akan diverifikasi.
        is_verified (bool): Saat ini tidak berpengaruh; service selalu mengisi True.
    """

    email: EmailStr
    is_verified: bool


class EditStatus(BaseModel):
    """
    Body request ubah status kerja akun (khusus admin).

    Attributes:
        user_id (uuid.UUID): ID akun yang diubah.
        status (Status): Status baru: aktif, resign, phk, atau pensiun.
    """

    user_id: uuid.UUID
    status: Status


class CookieToken(BaseModel):
    """
    Isi (payload) JWT login yang disimpan di cookie.

    Attributes:
        sub (str): ID pengguna (UUID dalam bentuk string); acuan utama identitas.
        email (EmailStr): Email pengguna saat token dibuat.
        name (str): Nama pengguna saat token dibuat.
        type (str): Jenis token; harus "access" untuk login biasa.
    """

    sub: str
    email: EmailStr
    name: str
    type: str


class Logout(BaseModel):
    """
    Skema untuk request logout pengguna.

    Attributes:
        token (str): JWT access token yang akan di-blacklist.
    """
    token: str