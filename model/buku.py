from exceptions import InvalidInputError

class Buku:
    def __init__(self, isbn: str, judul: str, penulis: str, kategori: str, stok: int):
        if not self.validate_isbn(isbn):
            raise InvalidInputError(f"ISBN '{isbn}' tidak valid. Harus berupa angka dan panjang 10 atau 13 karakter.")
        if not judul or not judul.strip():
            raise InvalidInputError("Judul buku tidak boleh kosong.")
        if not penulis or not penulis.strip():
            raise InvalidInputError("Penulis buku tidak boleh kosong.")
        if not kategori or not kategori.strip():
            raise InvalidInputError("Kategori buku tidak boleh kosong.")
        if not isinstance(stok, int) or stok < 0:
            raise InvalidInputError("Stok buku tidak boleh negatif dan harus bilangan bulat.")

        self._isbn = isbn.strip()
        self._judul = judul.strip()
        self._penulis = penulis.strip()
        self._kategori = kategori.strip()
        self._stok = stok

    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def judul(self) -> str:
        return self._judul

    @judul.setter
    def judul(self, value: str):
        if not value or not value.strip():
            raise InvalidInputError("Judul buku tidak boleh kosong.")
        self._judul = value.strip()

    @property
    def penulis(self) -> str:
        return self._penulis

    @penulis.setter
    def penulis(self, value: str):
        if not value or not value.strip():
            raise InvalidInputError("Penulis buku tidak boleh kosong.")
        self._penulis = value.strip()

    @property
    def kategori(self) -> str:
        return self._kategori

    @kategori.setter
    def kategori(self, value: str):
        if not value or not value.strip():
            raise InvalidInputError("Kategori buku tidak boleh kosong.")
        self._kategori = value.strip()

    @property
    def stok(self) -> int:
        return self._stok

    @stok.setter
    def stok(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise InvalidInputError("Stok buku tidak boleh negatif dan harus bilangan bulat.")
        self._stok = value

    def to_dict(self) -> dict:
        return {
            "isbn": self._isbn,
            "judul": self._judul,
            "penulis": self._penulis,
            "kategori": self._kategori,
            "stok": self._stok
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            isbn=data["isbn"],
            judul=data["judul"],
            penulis=data["penulis"],
            kategori=data["kategori"],
            stok=data["stok"]
        )

    @staticmethod
    def validate_isbn(isbn: str) -> bool:
        """Memvalidasi ISBN (hanya angka dengan panjang 10 atau 13 digit)."""
        if not isbn:
            return False
        clean_isbn = isbn.replace("-", "").replace(" ", "")
        return clean_isbn.isdigit() and len(clean_isbn) in [10, 13]
