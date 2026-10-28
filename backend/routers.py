"""
routers.py — Router induk API.

Menggabungkan router tiap fitur (auth, items, transactions) di bawah prefix
"/thorix-api/v1" lalu dipasang ke aplikasi oleh main.py. Menambah fitur baru =
membuat router di api/v1/ lalu mendaftarkannya di sini.
"""

from fastapi import APIRouter

from .api.v1 import auth, items, transactions

backend_router = APIRouter(prefix="/thorix-api")

backend_router.include_router(auth.router, prefix="/v1")
backend_router.include_router(items.router, prefix="/v1")
backend_router.include_router(transactions.router, prefix="/v1")