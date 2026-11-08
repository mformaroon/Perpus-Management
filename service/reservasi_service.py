import datetime
from storage.reservasi_storage import ReservasiStorage
from storage.buku_storage import BukuStorage
from storage.anggota_storage import AnggotaStorage
from storage.transaksi_storage import TransaksiStorage
from model.reservasi import Reservasi
from model.peminjaman import Peminjaman
from exceptions import InvalidInputError, BookNotFoundError, MemberNotFoundError, ActiveReservationError

class ReservasiService:
    def __init__(
        self,
        reservasi_storage: ReservasiStorage = None,
        buku_storage: BukuStorage = None,
        anggota_storage: AnggotaStorage = None,
        transaksi_storage: TransaksiStorage = None
    ):
        self._reservasi_storage = reservasi_storage if reservasi_storage is not None else ReservasiStorage()
        self._buku_storage = buku_storage if buku_storage is not None else BukuStorage()
        self._anggota_storage = anggota_storage if anggota_storage is not None else AnggotaStorage()
        self._transaksi_storage = transaksi_storage if transaksi_storage is not None else TransaksiStorage()

    def get_all_reservations(self) -> list:
        return self._reservasi_storage.get_all()

    def get_reservations_by_member(self, id_anggota: str) -> list:
        res_list = self.get_all_reservations()
        return [r for r in res_list if r.id_anggota == id_anggota]

    def buat_reservasi(self, id_anggota: str, isbn: str) -> Reservasi:
        # 1. Validasi Anggota
        anggota = self._anggota_storage.get_by_id(id_anggota)
        if not anggota:
            raise MemberNotFoundError(f"Anggota dengan ID '{id_anggota}' tidak ditemukan.")

        # 2. Validasi Buku
        buku = self._buku_storage.get_by_id(isbn)
        if not buku:
            raise BookNotFoundError(f"Buku dengan ISBN '{isbn}' tidak ditemukan.")

        # 3. Jika stok > 0, arahkan untuk meminjam langsung
        if buku.stok > 0:
            raise InvalidInputError("Stok buku masih tersedia. Silakan lakukan peminjaman secara langsung.")

        # 4. Cek apakah sedang meminjam buku ini
        txs = self._transaksi_storage.get_all()
        for tx in txs:
            if (isinstance(tx, Peminjaman) and 
                tx.id_anggota == id_anggota and 
                tx.isbn == isbn and 
                tx.status in ["DIPINJAM", "TERLAMBAT"]):
                raise InvalidInputError("Anda tidak dapat mereservasi buku yang sedang Anda pinjam.")

        # 5. Cek apakah sudah ada reservasi aktif (PENDING atau TERSEDIA)
        reservations = self.get_all_reservations()
        for res in reservations:
            if res.id_anggota == id_anggota and res.isbn == isbn and res.status in ["PENDING", "TERSEDIA"]:
                raise ActiveReservationError("Anda sudah memiliki reservasi aktif (Pending/Tersedia) untuk buku ini.")

        # 6. Generate ID Reservasi
        res_count = len(reservations) + 1
        id_reservasi = f"RS-{res_count:04d}"
        while self._reservasi_storage.get_by_id(id_reservasi):
            res_count += 1
            id_reservasi = f"RS-{res_count:04d}"

        # 7. Buat Objek Reservasi & Simpan
        hari_ini = datetime.date.today().strftime("%Y-%m-%d")
        reservasi = Reservasi(
            id_reservasi=id_reservasi,
            id_anggota=id_anggota,
            isbn=isbn,
            tanggal_reservasi=hari_ini,
            status="PENDING"
        )

        if self._reservasi_storage.create(reservasi):
            return reservasi
            
        raise InvalidInputError("Gagal menyimpan reservasi baru.")

    def batalkan_reservasi(self, id_reservasi: str) -> bool:
        res = self._reservasi_storage.get_by_id(id_reservasi)
        if not res:
            raise InvalidInputError(f"Reservasi dengan ID '{id_reservasi}' tidak ditemukan.")
            
        if res.status in ["SELESAI", "BATAL"]:
            raise InvalidInputError(f"Reservasi sudah dalam status {res.status} dan tidak dapat dibatalkan.")

        res.status = "BATAL"
        return self._reservasi_storage.update(id_reservasi, res)
