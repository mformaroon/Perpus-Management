from storage.buku_storage import BukuStorage
from model.buku import Buku
from exceptions import InvalidInputError, BookNotFoundError

class BukuService:
    def __init__(self, storage: BukuStorage = None):
        self._storage = storage if storage is not None else BukuStorage()

    def get_all_books(self) -> list:
        return self._storage.get_all()

    def get_buku_by_isbn(self, isbn: str) -> Buku:
        book = self._storage.get_by_id(isbn)
        if not book:
            raise BookNotFoundError(f"Buku dengan ISBN {isbn} tidak ditemukan.")
        return book

    def tambah_buku(self, data: dict) -> Buku:
        isbn = data.get("isbn")
        if not isbn:
            raise InvalidInputError("ISBN harus disediakan.")
            
        # Check if already exists
        if self._storage.get_by_id(isbn):
            raise InvalidInputError(f"Buku dengan ISBN {isbn} sudah terdaftar.")
            
        buku = Buku(
            isbn=isbn,
            judul=data.get("judul"),
            penulis=data.get("penulis"),
            kategori=data.get("kategori"),
            stok=int(data.get("stok", 0))
        )
        
        if self._storage.create(buku):
            return buku
        raise InvalidInputError("Gagal menambahkan buku ke penyimpanan.")

    def ubah_buku(self, isbn: str, data: dict) -> Buku:
        buku = self.get_buku_by_isbn(isbn)
        
        # Update fields if provided
        if "judul" in data:
            buku.judul = data["judul"]
        if "penulis" in data:
            buku.penulis = data["penulis"]
        if "kategori" in data:
            buku.kategori = data["kategori"]
        if "stok" in data:
            buku.stok = int(data["stok"])
            
        if self._storage.update(isbn, buku):
            return buku
        raise InvalidInputError("Gagal memperbarui buku di penyimpanan.")

    def hapus_buku(self, isbn: str) -> bool:
        # Check if book exists
        self.get_buku_by_isbn(isbn)
        return self._storage.delete(isbn)

    def cari_buku(self, query: str = "", kategori: str = "") -> list:
        books = self.get_all_books()
        filtered = []
        
        query = query.strip().lower() if query else ""
        kategori = kategori.strip().lower() if kategori else ""
        
        for book in books:
            match_query = True
            match_kat = True
            
            if query:
                match_query = (query in book.judul.lower() or 
                               query in book.penulis.lower() or 
                               query in book.isbn.lower())
                               
            if kategori:
                match_kat = (kategori == book.kategori.lower())
                
            if match_query and match_kat:
                filtered.append(book)
                
        return filtered
