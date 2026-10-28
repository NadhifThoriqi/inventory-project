"""
Module:
    core/enums.py
Deskripsi:
    Mendefinisikan enumerasi (enum) yang digunakan di seluruh aplikasi
    sebagai nilai konstan untuk kolom-kolom tertentu di database.
"""

from enum import StrEnum


class Role(StrEnum):
    """
    Peran pengguna dalam sistem.

    Values:
        ADMIN: Akses penuh. Satu-satunya yang boleh mengubah data barang,
            memverifikasi akun, dan mengubah status akun.
        STAFF: Pengguna biasa (bawaan saat mendaftar). Boleh melihat barang dan mencatat transaksi.
    """

    ADMIN = "admin"
    STAFF = "staff"


class Status(StrEnum):
    """
    Status kerja akun pengguna.

    Values:
        AKTIF: Masih bekerja; akun boleh dipakai (bawaan).
        Resign: Berhenti atas keinginan sendiri.
        PHK: Diberhentikan oleh perusahaan.
        PENSIUN: Berhenti karena memasuki masa pensiun.
    """

    AKTIF = "aktif"
    Resign = "resign"                       # Tindakan atau keputusan pribadi untuk berhenti bekerja dari suatu perusahaan.
    PHK = "phk"                             # Pemberhentian yang dilakukan oleh pihak perusahaan, bukan atas keinginan karyawan sendiri.
    PENSIUN = "pensiun"                     # Berhenti bekerja karena sudah memasuki usia lanjut atau masa akhir pengabdian.


class TypeMutasi(StrEnum):
    """
    Jenis mutasi stok pada transaksi.

    Values:
        IN: Barang masuk (stok bertambah).
        OUT: Barang keluar (stok berkurang, tidak boleh melebihi stok yang ada).
    """

    IN = "in"
    OUT = "out"
