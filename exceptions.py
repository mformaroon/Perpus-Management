class LibraSysException(Exception):
    """Kelas dasar untuk semua exception di LibraSys."""
    pass

class BookNotFoundError(LibraSysException):
    """Pengecualian ketika buku tidak ditemukan."""
    pass

class MemberNotFoundError(LibraSysException):
    """Pengecualian ketika anggota tidak ditemukan."""
    pass

class OutOfStockError(LibraSysException):
    """Pengecualian ketika stok buku habis."""
    pass

class BookAlreadyBorrowedError(LibraSysException):
    """Pengecualian ketika buku sudah dipinjam oleh anggota yang sama."""
    pass

class InvalidInputError(LibraSysException):
    """Pengecualian untuk input yang tidak valid."""
    pass

class ActiveReservationError(LibraSysException):
    """Pengecualian untuk kesalahan reservasi aktif."""
    pass

class BorrowLimitExceededError(LibraSysException):
    """Pengecualian ketika anggota melebihi batas peminjaman buku."""
    pass
