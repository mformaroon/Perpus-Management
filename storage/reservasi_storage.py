from storage.json_storage import JsonStorage
from model.reservasi import Reservasi

class ReservasiStorage(JsonStorage):
    def __init__(self, file_path: str = "database/reservasi.json"):
        super().__init__(file_path)

    def get_all(self) -> list:
        raw_data = self.load()
        reservations = []
        for item in raw_data:
            try:
                reservations.append(Reservasi.from_dict(item))
            except Exception as e:
                print(f"Error loading reservation record: {e}")
        return reservations

    def get_by_id(self, id_reservasi: str) -> Reservasi:
        res_list = self.get_all()
        for res in res_list:
            if res.id_reservasi == id_reservasi:
                return res
        return None

    def create(self, reservasi: Reservasi) -> bool:
        if self.get_by_id(reservasi.id_reservasi):
            return False  # Already exists
        data = self.load()
        data.append(reservasi.to_dict())
        self.save(data)
        return True

    def update(self, id_reservasi: str, reservasi: Reservasi) -> bool:
        data = self.load()
        updated = False
        for idx, item in enumerate(data):
            if item["id_reservasi"] == id_reservasi:
                data[idx] = reservasi.to_dict()
                updated = True
                break
        if updated:
            self.save(data)
        return updated

    def delete(self, id_reservasi: str) -> bool:
        data = self.load()
        initial_len = len(data)
        data = [item for item in data if item["id_reservasi"] != id_reservasi]
        if len(data) < initial_len:
            self.save(data)
            return True
        return False
