from storage.json_storage import JsonStorage
from model.transaksi import Transaksi
from model.peminjaman import Peminjaman
from model.pengembalian import Pengembalian

class TransaksiStorage(JsonStorage):
    def __init__(self, file_path: str = "database/transaksi.json"):
        super().__init__(file_path)

    def get_all(self) -> list:
        raw_data = self.load()
        transactions = []
        for item in raw_data:
            try:
                tipe = item.get("tipe_transaksi")
                if tipe == "Peminjaman":
                    transactions.append(Peminjaman.from_dict(item))
                elif tipe == "Pengembalian":
                    transactions.append(Pengembalian.from_dict(item))
            except Exception as e:
                print(f"Error loading transaction record: {e}")
        return transactions

    def get_by_id(self, id_transaksi: str) -> Transaksi:
        txs = self.get_all()
        for tx in txs:
            if tx.id_transaksi == id_transaksi:
                return tx
        return None

    def create(self, transaksi: Transaksi) -> bool:
        if self.get_by_id(transaksi.id_transaksi):
            return False  # Already exists
        data = self.load()
        data.append(transaksi.to_dict())
        self.save(data)
        return True

    def update(self, id_transaksi: str, transaksi: Transaksi) -> bool:
        data = self.load()
        updated = False
        for idx, item in enumerate(data):
            if item["id_transaksi"] == id_transaksi:
                data[idx] = transaksi.to_dict()
                updated = True
                break
        if updated:
            self.save(data)
        return updated

    def delete(self, id_transaksi: str) -> bool:
        data = self.load()
        initial_len = len(data)
        data = [item for item in data if item["id_transaksi"] != id_transaksi]
        if len(data) < initial_len:
            self.save(data)
            return True
        return False

