"""
frontend/routers.py — Router untuk halaman HTML (bukan API).

Berisi:
    - `templates`       : mesin Jinja2, dipakai juga oleh main.py untuk halaman error.
    - `frontend_router` : rute halaman. Saat ini hanya halaman login/profil di "/".

Catatan: parameter ?expired=true & ?next=... dibaca langsung oleh JavaScript
di html/index.html (lewat URLSearchParams), jadi server tidak perlu
meneruskannya ke template.
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

FRONTEND_DIR = Path(__file__).resolve().parent

frontend_router = APIRouter()
templates = Jinja2Templates(directory=str(FRONTEND_DIR))


@frontend_router.get("/")
async def login_page(request: Request):
    """Halaman masuk/daftar; berubah jadi tampilan profil kalau sesi masih aktif."""
    return templates.TemplateResponse(request=request, name="/html/index.html")
