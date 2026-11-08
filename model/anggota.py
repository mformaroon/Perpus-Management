from model.pengguna import Pengguna
from exceptions import InvalidInputError

# Hubungan: Inheritance (Generalization) - Anggota adalah turunan dari class Pengguna
class Anggota(Pengguna):
    def __init__(self, id_pengguna: str, nama: str, email: str, tipe_keanggotaan: str = "Regular", password: str = "123456"):
        super().__init__(id_pengguna, nama, email, password)
        
        if tipe_keanggotaan not in ["Regular", "Premium"]:
            raise InvalidInputError("Tipe keanggotaan harus 'Regular' atau 'Premium'.")
            
        self._tipe_keanggotaan = tipe_keanggotaan
        self._maks_pinjam = 3 if tipe_keanggotaan == "Regular" else 7

    @property
    def tipe_keanggotaan(self) -> str:
        return self._tipe_keanggotaan

    @tipe_keanggotaan.setter
    def tipe_keanggotaan(self, value: str):
        if value not in ["Regular", "Premium"]:
            raise InvalidInputError("Tipe keanggotaan harus 'Regular' atau 'Premium'.")
        self._tipe_keanggotaan = value
        self._maks_pinjam = 3 if value == "Regular" else 7

    @property
    def maks_pinjam(self) -> int:
        return self._maks_pinjam

    def role_name(self) -> str:
        return "Anggota"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "tipe_keanggotaan": self._tipe_keanggotaan,
            "maks_pinjam": self._maks_pinjam
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_pengguna=data["id_pengguna"],
            nama=data["nama"],
            email=data["email"],
            tipe_keanggotaan=data.get("tipe_keanggotaan", "Regular"),
            password=data.get("password", "123456")
        )

