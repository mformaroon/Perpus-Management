from model.pengguna import Pengguna
from exceptions import InvalidInputError

# Hubungan: Inheritance (Generalization) - Petugas adalah turunan dari class Pengguna
class Petugas(Pengguna):
    def __init__(self, id_pengguna: str, nama: str, email: str, nip: str, password: str = "123456"):
        super().__init__(id_pengguna, nama, email, password)
        
        if not nip or not nip.strip():
            raise InvalidInputError("NIP Petugas tidak boleh kosong.")
            
        self._nip = nip.strip()

    @property
    def nip(self) -> str:
        return self._nip

    @nip.setter
    def nip(self, value: str):
        if not value or not value.strip():
            raise InvalidInputError("NIP Petugas tidak boleh kosong.")
        self._nip = value.strip()

    def role_name(self) -> str:
        return "Petugas"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "nip": self._nip
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_pengguna=data["id_pengguna"],
            nama=data["nama"],
            email=data["email"],
            nip=data["nip"],
            password=data.get("password", "123456")
        )

