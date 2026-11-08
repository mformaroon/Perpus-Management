from storage.json_storage import JsonStorage
from model.pengguna import Pengguna
from model.anggota import Anggota
from model.petugas import Petugas

class AnggotaStorage(JsonStorage):
    def __init__(self, file_path: str = "database/anggota.json"):
        super().__init__(file_path)

    def get_all(self) -> list:
        raw_data = self.load()
        users = []
        for item in raw_data:
            try:
                role = item.get("role")
                if role == "Petugas":
                    users.append(Petugas.from_dict(item))
                else:
                    users.append(Anggota.from_dict(item))
            except Exception as e:
                print(f"Error loading user record: {e}")
        return users

    def get_by_id(self, id_pengguna: str) -> Pengguna:
        users = self.get_all()
        for user in users:
            if user.id_pengguna == id_pengguna:
                return user
        return None

    def create(self, pengguna: Pengguna) -> bool:
        if self.get_by_id(pengguna.id_pengguna):
            return False  # Already exists
        data = self.load()
        data.append(pengguna.to_dict())
        self.save(data)
        return True

    def update(self, id_pengguna: str, pengguna: Pengguna) -> bool:
        data = self.load()
        updated = False
        for idx, item in enumerate(data):
            if item["id_pengguna"] == id_pengguna:
                data[idx] = pengguna.to_dict()
                updated = True
                break
        if updated:
            self.save(data)
        return updated

    def delete(self, id_pengguna: str) -> bool:
        data = self.load()
        initial_len = len(data)
        data = [item for item in data if item["id_pengguna"] != id_pengguna]
        if len(data) < initial_len:
            self.save(data)
            return True
        return False
