from model.transaksi import Transaksi
from exceptions import InvalidInputError

# Hubungan: Inheritance (Generalization) - Pengembalian adalah turunan dari class Transaksi
# Hubungan: Association - Pengembalian terhubung dengan Peminjaman (via id_peminjaman)
class Pengembalian(Transaksi):
    def __init__(self, id_transaksi: str, id_anggota: str, isbn: str, tanggal: str, id_peminjaman: str, denda: int = 0):
        super().__init__(id_transaksi, id_anggota, isbn, tanggal)
        
        if not id_peminjaman or not id_peminjaman.strip():
            raise InvalidInputError("ID Peminjaman tidak boleh kosong.")
        if not isinstance(denda, int) or denda < 0:
            raise InvalidInputError("Denda tidak boleh negatif dan harus berupa bilangan bulat.")
            
        self._id_peminjaman = id_peminjaman.strip()
        self._denda = denda

    @property
    def id_peminjaman(self) -> str:
        return self._id_peminjaman

    @property
    def denda(self) -> int:
        return self._denda

    @denda.setter
    def denda(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise InvalidInputError("Denda tidak boleh negatif.")
        self._denda = value

    def info_transaksi(self) -> str:
        return f"Pengembalian {self._id_transaksi}: Anggota {self._id_anggota} mengembalikan buku {self._isbn} (Ref Peminjaman: {self._id_peminjaman}, Denda: Rp {self._denda})"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "id_peminjaman": self._id_peminjaman,
            "denda": self._denda
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_transaksi=data["id_transaksi"],
            id_anggota=data["id_anggota"],
            isbn=data["isbn"],
            tanggal=data["tanggal"],
            id_peminjaman=data["id_peminjaman"],
            denda=data.get("denda", 0)
        )
