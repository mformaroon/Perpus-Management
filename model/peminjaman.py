from model.transaksi import Transaksi
from exceptions import InvalidInputError

# Hubungan: Inheritance (Generalization) - Peminjaman adalah turunan dari class Transaksi
class Peminjaman(Transaksi):
    def __init__(self, id_transaksi: str, id_anggota: str, isbn: str, tanggal: str, tanggal_jatuh_tempo: str, status: str = "DIPINJAM"):
        super().__init__(id_transaksi, id_anggota, isbn, tanggal)
        
        if not tanggal_jatuh_tempo or not tanggal_jatuh_tempo.strip():
            raise InvalidInputError("Tanggal jatuh tempo tidak boleh kosong.")
        if status not in ["DIPINJAM", "DIKEMBALIKAN", "TERLAMBAT"]:
            raise InvalidInputError("Status peminjaman tidak valid.")
            
        self._tanggal_jatuh_tempo = tanggal_jatuh_tempo.strip()
        self._status = status

    @property
    def tanggal_jatuh_tempo(self) -> str:
        return self._tanggal_jatuh_tempo

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        if value not in ["DIPINJAM", "DIKEMBALIKAN", "TERLAMBAT"]:
            raise InvalidInputError("Status peminjaman tidak valid.")
        self._status = value

    def info_transaksi(self) -> str:
        return f"Peminjaman {self._id_transaksi}: Anggota {self._id_anggota} meminjam buku {self._isbn} hingga {self._tanggal_jatuh_tempo} (Status: {self._status})"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "tanggal_jatuh_tempo": self._tanggal_jatuh_tempo,
            "status": self._status
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_transaksi=data["id_transaksi"],
            id_anggota=data["id_anggota"],
            isbn=data["isbn"],
            tanggal=data["tanggal"],
            tanggal_jatuh_tempo=data["tanggal_jatuh_tempo"],
            status=data.get("status", "DIPINJAM")
        )
