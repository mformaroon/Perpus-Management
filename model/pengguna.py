from abc import ABC, abstractmethod
import re
from exceptions import InvalidInputError

class Pengguna(ABC):
    def __init__(self, id_pengguna: str, nama: str, email: str, password: str = "123456"):
        if not id_pengguna or not id_pengguna.strip():
            raise InvalidInputError("ID Pengguna tidak boleh kosong.")
        if not nama or not nama.strip():
            raise InvalidInputError("Nama tidak boleh kosong.")
        if not self.validate_email(email):
            raise InvalidInputError(f"Email '{email}' tidak valid.")
        if not password or not password.strip():
            raise InvalidInputError("Password tidak boleh kosong.")
            
        self._id_pengguna = id_pengguna.strip()
        self._nama = nama.strip()
        self._email = email.strip()
        self._password = password.strip()

    @property
    def id_pengguna(self) -> str:
        return self._id_pengguna

    @property
    def nama(self) -> str:
        return self._nama

    @nama.setter
    def nama(self, value: str):
        if not value or not value.strip():
            raise InvalidInputError("Nama tidak boleh kosong.")
        self._nama = value.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if not self.validate_email(value):
            raise InvalidInputError(f"Email '{value}' tidak valid.")
        self._email = value.strip()

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str):
        if not value or not value.strip():
            raise InvalidInputError("Password tidak boleh kosong.")
        self._password = value.strip()

    @abstractmethod
    def role_name(self) -> str:
        """Mengembalikan nama peran (role) dari pengguna."""
        pass

    def to_dict(self) -> dict:
        return {
            "id_pengguna": self._id_pengguna,
            "nama": self._nama,
            "email": self._email,
            "password": self._password,
            "role": self.role_name()
        }

    @staticmethod
    def validate_email(email: str) -> bool:
        """Memvalidasi format email menggunakan regex."""
        if not email:
            return False
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

