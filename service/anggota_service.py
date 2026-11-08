from storage.anggota_storage import AnggotaStorage
from model.anggota import Anggota
from model.petugas import Petugas
from model.pengguna import Pengguna
from exceptions import InvalidInputError, MemberNotFoundError

class AnggotaService:
    # Hubungan: Aggregation - AnggotaService menggunakan objek AnggotaStorage
    def __init__(self, storage: AnggotaStorage = None):
        self._storage = storage if storage is not None else AnggotaStorage()

    def get_all_users(self) -> list:
        return self._storage.get_all()

    # Hubungan: Dependency - Method ini bergantung pada model Anggota
    def get_all_members(self) -> list:
        return [u for u in self.get_all_users() if isinstance(u, Anggota)]

    def get_all_officers(self) -> list:
        return [u for u in self.get_all_users() if isinstance(u, Petugas)]

    def get_user_by_id(self, id_pengguna: str) -> Pengguna:
        user = self._storage.get_by_id(id_pengguna)
        if not user:
            raise MemberNotFoundError(f"Pengguna dengan ID {id_pengguna} tidak ditemukan.")
        return user

    def tambah_anggota(self, data: dict) -> Anggota:
        id_pengguna = data.get("id_pengguna")
        if not id_pengguna:
            raise InvalidInputError("ID Pengguna harus disediakan.")
            
        if self._storage.get_by_id(id_pengguna):
            raise InvalidInputError(f"ID Pengguna '{id_pengguna}' sudah digunakan.")
            
        anggota = Anggota(
            id_pengguna=id_pengguna,
            nama=data.get("nama"),
            email=data.get("email"),
            tipe_keanggotaan=data.get("tipe_keanggotaan", "Regular"),
            password=data.get("password", "123456")
        )
        
        if self._storage.create(anggota):
            return anggota
        raise InvalidInputError("Gagal mendaftarkan anggota baru.")

    def ubah_anggota(self, id_anggota: str, data: dict) -> Anggota:
        user = self.get_user_by_id(id_anggota)
        if not isinstance(user, Anggota):
            raise InvalidInputError("ID yang diberikan bukan tipe Anggota.")
            
        if "nama" in data:
            user.nama = data["nama"]
        if "email" in data:
            user.email = data["email"]
        if "tipe_keanggotaan" in data:
            user.tipe_keanggotaan = data["tipe_keanggotaan"]
            
        if self._storage.update(id_anggota, user):
            return user
        raise InvalidInputError("Gagal memperbarui data anggota.")

    def hapus_anggota(self, id_anggota: str) -> bool:
        # Check if exists
        self.get_user_by_id(id_anggota)
        return self._storage.delete(id_anggota)

    def tambah_petugas(self, data: dict) -> Petugas:
        id_pengguna = data.get("id_pengguna")
        if not id_pengguna:
            raise InvalidInputError("ID Pengguna harus disediakan.")
            
        if self._storage.get_by_id(id_pengguna):
            raise InvalidInputError(f"ID Pengguna '{id_pengguna}' sudah digunakan.")
            
        petugas = Petugas(
            id_pengguna=id_pengguna,
            nama=data.get("nama"),
            email=data.get("email"),
            nip=data.get("nip"),
            password=data.get("password", "123456")
        )
        
        if self._storage.create(petugas):
            return petugas
        raise InvalidInputError("Gagal mendaftarkan petugas baru.")

    def ubah_petugas(self, id_petugas: str, data: dict) -> Petugas:
        user = self.get_user_by_id(id_petugas)
        if not isinstance(user, Petugas):
            raise InvalidInputError("ID yang diberikan bukan tipe Petugas.")
            
        if "nama" in data:
            user.nama = data["nama"]
        if "email" in data:
            user.email = data["email"]
        if "nip" in data:
            user.nip = data["nip"]
            
        if self._storage.update(id_petugas, user):
            return user
        raise InvalidInputError("Gagal memperbarui data petugas.")
