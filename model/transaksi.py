from abc import ABC, abstractmethod
from exceptions import InvalidInputError

# Hubungan: Association - Transaksi memiliki referensi ke entitas Pengguna (id_anggota) dan Buku (isbn)
class Transaksi(ABC):
    def __init__(self, id_transaksi: str, id_anggota: str, isbn: str, tanggal: str):
        if not id_transaksi or not id_transaksi.strip():
            raise InvalidInputError("ID Transaksi tidak boleh kosong.")
        if not id_anggota or not id_anggota.strip():
            raise InvalidInputError("ID Anggota tidak boleh kosong.")
        if not isbn or not isbn.strip():
            raise InvalidInputError("ISBN Buku tidak boleh kosong.")
        if not tanggal or not tanggal.strip():
            raise InvalidInputError("Tanggal transaksi tidak boleh kosong.")

        self._id_transaksi = id_transaksi.strip()
        self._id_anggota = id_anggota.strip()
        self._isbn = isbn.strip()
        self._tanggal = tanggal.strip()

    @property
    def id_transaksi(self) -> str:
        return self._id_transaksi

    @property
    def id_anggota(self) -> str:
        return self._id_anggota

    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def tanggal(self) -> str:
        return self._tanggal

    @abstractmethod
    def info_transaksi(self) -> str:
        """Mengembalikan deskripsi ringkas tentang transaksi ini."""
        pass

    def to_dict(self) -> dict:
        return {
            "id_transaksi": self._id_transaksi,
            "id_anggota": self._id_anggota,
            "isbn": self._isbn,
            "tanggal": self._tanggal,
            "tipe_transaksi": self.__class__.__name__
        }
