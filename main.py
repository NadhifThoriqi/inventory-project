"""
main.py — Entry point aplikasi Thorix API (Inventory Multi-Role System).

Merakit aplikasi FastAPI: siklus hidup startup/shutdown (menyiapkan tabel dan
akun admin pertama), CORS, file statis, router backend/frontend, serta
exception handler global yang membalas JSON untuk rute API dan halaman HTML
untuk rute lainnya.

Jalankan dari root proyek:  python main.py
"""


from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.routers import backend_router
from backend.core.config import settings
from backend.db import sessions, seed
from frontend.routers import frontend_router, templates

try:
    from debug_errors import debug_router
except ImportError:
    debug_router = None

# =============================================================================
# 1. KONFIGURASI DASAR
# =============================================================================
RESET = "\033[0m"
HIJAU = "\033[92m"
KUNING = "\033[93m"
CYAN = "\033[96m"
MERAH = "\033[91m"

APP_VERSION = "0.0.0 - 1.0.0"
APP_TITLE = settings.project_name

# Daftar origin frontend yang diizinkan mengakses API (CORS)
ORIGINS = [
    f"http://localhost:{settings.port}",
    f"http://127.0.0.1:{settings.port}",
    f"http://192.168.1.4:{settings.port}",
]

# Path direktori proyek & folder static frontend
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "frontend" / "static"


# =============================================================================
# 2. LIFECYCLE APLIKASI (STARTUP / SHUTDOWN)
# =============================================================================

@asynccontextmanager
async def lifespan(life_app: FastAPI):
    """
    Konteks manajer lifecycle aplikasi FastAPI.

    Dijalankan saat startup:
        - Mencetak nama aplikasi yang sedang berjalan.
        - Menginisialisasi database (membuat tabel jika belum ada).

    Dijalankan saat shutdown:
        - Mencetak pesan bahwa aplikasi sedang dimatikan.

    Args:
        life_app (FastAPI): Instance aplikasi FastAPI yang sedang berjalan.
    """
    # --- STARTUP ---
    print(f"{CYAN}INFO{RESET}:\t Aplikasi {life_app.title} sedang berjalan...")

    # ==========================================
    # LOGIKA STARTUP (dieksekusi saat server boot)
    # ==========================================
    print(f"{CYAN}INFO{RESET}:\t Memulai pemeriksaan database...")
    await sessions.create_engine()
    print(f"{CYAN}INFO{RESET}:\t Database siap digunakan.")

    await seed.check_database_is_empty()

    # Menyerahkan kontrol ke aplikasi FastAPI
    yield

    # ==========================================
    # LOGIKA SHUTDOWN (dieksekusi saat server mati)
    # ==========================================
    print("Menutup koneksi pool database...")
    # Tutup semua pool koneksi asyncpg agar tidak ada connection leak
    await sessions.close_engine()
    print("Koneksi database berhasil ditutup.")

# =============================================================================
# 3. INISIALISASI APLIKASI FASTAPI
# =============================================================================

# PENTING: root_path harus sinkron dengan konfigurasi reverse proxy Nginx (/ymu)
app = FastAPI(
    title=APP_TITLE,
    lifespan=lifespan,
    root_path="/thorix"
)


# =============================================================================
# 4. MIDDLEWARE
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "POST", "PUT", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# =============================================================================
# 5. STATIC FILES
# =============================================================================

app.mount(
    "/thorix-static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


# =============================================================================
# 6. ROUTES
# =============================================================================

@app.get(
    "/thorix-api/health",
    tags=["Status Sistem"],
    summary="Cek Status Server",
)
async def health_check():
    """
    Endpoint sederhana untuk mengecek ketersediaan server Thorix API.
    """
    return {
        "status": "online",
        "app": APP_TITLE,
        "version": APP_VERSION,
    }

if debug_router is not None:
    app.include_router(debug_router)
app.include_router(backend_router)
app.include_router(frontend_router)


# =============================================================================
# 7. EXCEPTION HANDLERS
# =============================================================================
 
# Peta kode status HTTP -> halaman HTML khusus di html/exceptions/.
# Kode yang TIDAK ada di peta ini (mis. 400, 402, 409, dll.) akan jatuh
# ke template umum "/html/exceptions/error.html".
STATUS_TEMPLATE_MAP = {
    status.HTTP_400_BAD_REQUEST: "/html/exceptions/400.html",
    status.HTTP_403_FORBIDDEN: "/html/exceptions/403.html",
    status.HTTP_404_NOT_FOUND: "/html/exceptions/404.html",
    status.HTTP_405_METHOD_NOT_ALLOWED: "/html/exceptions/405.html",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "/html/exceptions/422.html",
    status.HTTP_429_TOO_MANY_REQUESTS: "/html/exceptions/429.html",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "/html/exceptions/500.html",
    status.HTTP_502_BAD_GATEWAY: "/html/exceptions/502.html",
    status.HTTP_503_SERVICE_UNAVAILABLE: "/html/exceptions/503.html",
    status.HTTP_504_GATEWAY_TIMEOUT: "/html/exceptions/504.html",
}
 
# Pesan default per kode status, dipakai kalau exc.detail kosong/generik.
DEFAULT_DETAIL_MAP = {
    status.HTTP_400_BAD_REQUEST: "Permintaan yang dikirim tidak valid.",
    status.HTTP_403_FORBIDDEN: "Anda tidak memiliki izin untuk mengakses halaman ini.",
    status.HTTP_404_NOT_FOUND: "Halaman atau data yang dicari tidak ditemukan.",
    status.HTTP_405_METHOD_NOT_ALLOWED: "Metode permintaan tidak diizinkan untuk rute ini.",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "Data yang dikirim tidak lolos validasi.",
    status.HTTP_429_TOO_MANY_REQUESTS: "Terlalu banyak permintaan, silakan coba lagi nanti.",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Terjadi kesalahan internal pada server.",
    status.HTTP_502_BAD_GATEWAY: "Server menerima balasan tidak valid dari layanan lain.",
    status.HTTP_503_SERVICE_UNAVAILABLE: "Layanan sedang tidak tersedia, silakan coba lagi nanti.",
    status.HTTP_504_GATEWAY_TIMEOUT: "Server tidak menerima balasan tepat waktu.",
}
 
 
def _is_api_route(request: Request) -> bool:
    """Deteksi apakah permintaan berasal dari klien API (bukan browser HTML)."""
    return (
        request.url.path.startswith("/thorix-api/")
        or "application/json" in request.headers.get("accept", "")
    )
 
 
def _render_error_page(request: Request, status_code: int, detail: str | None, path: str | None = None):
    """Render halaman HTML sesuai kode status, jatuh ke error.html kalau tak dipetakan."""
    template_name = STATUS_TEMPLATE_MAP.get(status_code, "/html/exceptions/error.html")
    context: dict[str, Any] = {
        "status_code": status_code,
        "detail": detail or DEFAULT_DETAIL_MAP.get(status_code),
    }
    if path is not None:
        context["path"] = path
 
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context,
        status_code=status_code,
    )
 
 
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    """Handler terpusat untuk semua HTTPException (400, 401, 403, 404, dll)."""
 
    is_api_route = _is_api_route(request)
 
    # 1. Tangani 401 Unauthorized (Sesi Habis/Belum Login) — kasus khusus,
    #    diarahkan (redirect) ke halaman login, bukan ditampilkan sebagai halaman error.
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        if is_api_route:
            return JSONResponse(
                content={"detail": exc.detail or "Sesi Anda telah kedaluwarsa"},
                status_code=401,
            )
 
        # Simpan halaman asal agar bisa diredirect kembali setelah login
        redirect_url = f"/thorix/?expired=true&next={request.url.path}"
        return RedirectResponse(
            url=redirect_url,
            status_code=status.HTTP_303_SEE_OTHER,
        )
 
    # 2. Rute API -> selalu balas JSON, bukan halaman HTML.
    if is_api_route:
        return JSONResponse(
            content={"detail": exc.detail or DEFAULT_DETAIL_MAP.get(exc.status_code, "Terjadi kesalahan")},
            status_code=exc.status_code,
        )
 
    # 3. Rute halaman (browser) -> render template HTML sesuai kode status.
    #    400, 403, 404, 405, 422, 429, 500, 502, 503, 504 punya halaman
    #    masing-masing; kode lain otomatis jatuh ke error.html.
    path = request.url.path if exc.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND) else None
    return _render_error_page(request, exc.status_code, exc.detail, path=path)
 

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handler untuk 422 Unprocessable Entity yang dilempar FastAPI saat
    body/query/path parameter gagal validasi Pydantic (bukan HTTPException).
    """
    is_api_route = _is_api_route(request)
 
    if is_api_route:
        return JSONResponse(
            content={
                "detail": "Data yang dikirim tidak valid.",
                "errors": jsonable_encoder(exc.errors()),
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )

    return _render_error_page(
        request,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Data yang dikirim tidak lolos validasi. Periksa kembali isian Anda.",
    )

 
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Menangkap error tak terduga (bukan HTTPException) agar tidak
    membocorkan stack trace mentah ke client dan tetap konsisten
    dengan format response API/HTML di atas.
    """
    print(f"[UNHANDLED ERROR] {request.method} {request.url.path} -> {exc!r}")
 
    if _is_api_route(request):
        return JSONResponse(
            content={"detail": "Terjadi kesalahan internal pada server"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
 
    return _render_error_page(
        request,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Terjadi kesalahan internal pada server",
    )
 

# =============================================================================
# 8. ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=settings.debug)  # nosec