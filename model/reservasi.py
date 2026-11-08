from exceptions import InvalidInputError

# Hubungan: Association - Reservasi terkait dengan entitas Pengguna (id_anggota) dan Buku (isbn)
class Reservasi:
    def __init__(self, id_reservasi: str, id_anggota: str, isbn: str, tanggal_reservasi: str, status: str = "PENDING"):
        if not id_reservasi or not id_reservasi.strip():
            raise InvalidInputError("ID Reservasi tidak boleh kosong.")
        if not id_anggota or not id_anggota.strip():
            raise InvalidInputError("ID Anggota tidak boleh kosong.")
        if not isbn or not isbn.strip():
            raise InvalidInputError("ISBN Buku tidak boleh kosong.")
        if not tanggal_reservasi or not tanggal_reservasi.strip():
            raise InvalidInputError("Tanggal reservasi tidak boleh kosong.")
        if status not in ["PENDING", "TERSEDIA", "SELESAI", "BATAL"]:
            raise InvalidInputError("Status reservasi tidak valid.")

        self._id_reservasi = id_reservasi.strip()
        self._id_anggota = id_anggota.strip()
        self._isbn = isbn.strip()
        self._tanggal_reservasi = tanggal_reservasi.strip()
        self._status = status

    @property
    def id_reservasi(self) -> str:
        return self._id_reservasi

    @property
    def id_anggota(self) -> str:
        return self._id_anggota

    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def tanggal_reservasi(self) -> str:
        return self._tanggal_reservasi

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        if value not in ["PENDING", "TERSEDIA", "SELESAI", "BATAL"]:
            raise InvalidInputError("Status reservasi tidak valid.")
        self._status = value

    def to_dict(self) -> dict:
        return {
            "id_reservasi": self._id_reservasi,
            "id_anggota": self._id_anggota,
            "isbn": self._isbn,
            "tanggal_reservasi": self._tanggal_reservasi,
            "status": self._status
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id_reservasi=data["id_reservasi"],
            id_anggota=data["id_anggota"],
            isbn=data["isbn"],
            tanggal_reservasi=data["tanggal_reservasi"],
            status=data.get("status", "PENDING")
        )
