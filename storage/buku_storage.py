from storage.json_storage import JsonStorage
from model.buku import Buku

class BukuStorage(JsonStorage):
    def __init__(self, file_path: str = "database/buku.json"):
        super().__init__(file_path)

    def get_all(self) -> list:
        raw_data = self.load()
        books = []
        for item in raw_data:
            try:
                books.append(Buku.from_dict(item))
            except Exception as e:
                print(f"Error loading book record: {e}")
        return books

    def get_by_id(self, isbn: str) -> Buku:
        books = self.get_all()
        for book in books:
            if book.isbn == isbn:
                return book
        return None

    def create(self, buku: Buku) -> bool:
        if self.get_by_id(buku.isbn):
            return False  # Already exists
        data = self.load()
        data.append(buku.to_dict())
        self.save(data)
        return True

    def update(self, isbn: str, buku: Buku) -> bool:
        data = self.load()
        updated = False
        for idx, item in enumerate(data):
            if item["isbn"] == isbn:
                data[idx] = buku.to_dict()
                updated = True
                break
        if updated:
            self.save(data)
        return updated

    def delete(self, isbn: str) -> bool:
        data = self.load()
        initial_len = len(data)
        data = [item for item in data if item["isbn"] != isbn]
        if len(data) < initial_len:
            self.save(data)
            return True
        return False
