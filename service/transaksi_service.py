import datetime
from storage.transaksi_storage import TransaksiStorage
from storage.buku_storage import BukuStorage
from storage.anggota_storage import AnggotaStorage
from storage.reservasi_storage import ReservasiStorage
from model.peminjaman import Peminjaman
from model.pengembalian import Pengembalian
from model.reservasi import Reservasi
from exceptions import (
    InvalidInputError,
    BookNotFoundError,
    MemberNotFoundError,
    OutOfStockError,
    BookAlreadyBorrowedError,
    BorrowLimitExceededError
)

class TransaksiService:
    def __init__(
        self,
        transaksi_storage: TransaksiStorage = None,
        buku_storage: BukuStorage = None,
        anggota_storage: AnggotaStorage = None,
        reservasi_storage: ReservasiStorage = None
    ):
        self._transaksi_storage = transaksi_storage if transaksi_storage is not None else TransaksiStorage()
        self._buku_storage = buku_storage if buku_storage is not None else BukuStorage()
        self._anggota_storage = anggota_storage if anggota_storage is not None else AnggotaStorage()
        self._reservasi_storage = reservasi_storage if reservasi_storage is not None else ReservasiStorage()

    def get_all_transactions(self) -> list:
        return self._transaksi_storage.get_all()

    def get_active_loans_by_member(self, id_anggota: str) -> list:
        txs = self.get_all_transactions()
        active_loans = []
        for tx in txs:
            if isinstance(tx, Peminjaman) and tx.id_anggota == id_anggota and tx.status in ["DIPINJAM", "TERLAMBAT"]:
                active_loans.append(tx)
        return active_loans

    def pinjam_buku(self, id_anggota: str, isbn: str) -> Peminjaman:
        # 1. Validasi Anggota
        anggota = self._anggota_storage.get_by_id(id_anggota)
        if not anggota:
            raise MemberNotFoundError(f"Anggota dengan ID '{id_anggota}' tidak ditemukan.")
        if anggota.role_name() != "Anggota":
            raise InvalidInputError("Hanya akun dengan peran 'Anggota' yang dapat meminjam buku.")

        # 2. Validasi Buku
        buku = self._buku_storage.get_by_id(isbn)
        if not buku:
            raise BookNotFoundError(f"Buku dengan ISBN '{isbn}' tidak ditemukan.")

        # 3. Validasi Batas Peminjaman
        active_loans = self.get_active_loans_by_member(id_anggota)
        if len(active_loans) >= anggota.maks_pinjam:
            raise BorrowLimitExceededError(
                f"Anggota telah mencapai batas peminjaman maksimum ({anggota.maks_pinjam} buku)."
            )

        # 4. Validasi Double Borrowing
        for loan in active_loans:
            if loan.isbn == isbn:
                raise BookAlreadyBorrowedError(f"Anda sedang meminjam buku dengan ISBN '{isbn}' ini.")

        # 5. Validasi Stok Buku
        if buku.stok <= 0:
            raise OutOfStockError(
                f"Stok buku '{buku.judul}' sedang kosong. Anda dapat melakukan reservasi."
            )

        # 6. Kurangi stok buku
        buku.stok -= 1
        self._buku_storage.update(isbn, buku)

        # 7. Generate ID Transaksi
        txs = self.get_all_transactions()
        tx_count = sum(1 for t in txs if isinstance(t, Peminjaman)) + 1
        id_transaksi = f"TX-{tx_count:04d}"
        
        # Cari ID yang unik jika bentrok
        while self._transaksi_storage.get_by_id(id_transaksi):
            tx_count += 1
            id_transaksi = f"TX-{tx_count:04d}"

        # 8. Hitung Tanggal Pinjam dan Jatuh Tempo (7 Hari)
        hari_ini = datetime.date.today()
        tanggal_pinjam = hari_ini.strftime("%Y-%m-%d")
        tanggal_jatuh_tempo = (hari_ini + datetime.timedelta(days=7)).strftime("%Y-%m-%d")

        # 9. Buat objek Peminjaman & Simpan
        peminjaman = Peminjaman(
            id_transaksi=id_transaksi,
            id_anggota=id_anggota,
            isbn=isbn,
            tanggal=tanggal_pinjam,
            tanggal_jatuh_tempo=tanggal_jatuh_tempo,
            status="DIPINJAM"
        )
        
        if self._transaksi_storage.create(peminjaman):
            # Jika anggota meminjam buku yang sebelumnya ia reservasi dengan status TERSEDIA, tandai reservasi selesai
            reservations = self._reservasi_storage.get_all()
            for res in reservations:
                if res.id_anggota == id_anggota and res.isbn == isbn and res.status in ["PENDING", "TERSEDIA"]:
                    res.status = "SELESAI"
                    self._reservasi_storage.update(res.id_reservasi, res)
                    break
            return peminjaman
            
        raise InvalidInputError("Gagal menyimpan transaksi peminjaman.")

    def kembalikan_buku(self, id_transaksi_pinjam: str) -> Pengembalian:
        # 1. Cari Peminjaman
        tx = self._transaksi_storage.get_by_id(id_transaksi_pinjam)
        if not tx or not isinstance(tx, Peminjaman):
            raise InvalidInputError(f"Transaksi peminjaman dengan ID '{id_transaksi_pinjam}' tidak ditemukan.")

        if tx.status == "DIKEMBALIKAN":
            raise InvalidInputError("Buku untuk transaksi ini sudah dikembalikan sebelumnya.")

        # 2. Hitung Denda Keterlambatan
        hari_ini = datetime.date.today()
        jatuh_tempo = datetime.datetime.strptime(tx.tanggal_jatuh_tempo, "%Y-%m-%d").date()
        
        denda = 0
        if hari_ini > jatuh_tempo:
            keterlambatan = (hari_ini - jatuh_tempo).days
            denda = keterlambatan * 2000  # Rp 2.000 per hari terlambat

        # 3. Update Status Peminjaman
        tx.status = "DIKEMBALIKAN"
        self._transaksi_storage.update(tx.id_transaksi, tx)

        # 4. Tambah Stok Buku
        buku = self._buku_storage.get_by_id(tx.isbn)
        if buku:
            buku.stok += 1
            self._buku_storage.update(tx.isbn, buku)

        # 5. Buat Pengembalian Transaksi
        txs = self.get_all_transactions()
        ret_count = sum(1 for t in txs if isinstance(t, Pengembalian)) + 1
        id_kembali = f"RT-{ret_count:04d}"
        
        while self._transaksi_storage.get_by_id(id_kembali):
            ret_count += 1
            id_kembali = f"RT-{ret_count:04d}"

        pengembalian = Pengembalian(
            id_transaksi=id_kembali,
            id_anggota=tx.id_anggota,
            isbn=tx.isbn,
            tanggal=hari_ini.strftime("%Y-%m-%d"),
            id_peminjaman=tx.id_transaksi,
            denda=denda
        )
        self._transaksi_storage.create(pengembalian)

        # 6. Alokasi Otomatis untuk Reservasi Antrean (FIFO)
        if buku:
            reservations = self._reservasi_storage.get_all()
            # Cari reservasi tertua (FIFO) untuk buku ini yang statusnya PENDING
            pending_res = [r for r in reservations if r.isbn == tx.isbn and r.status == "PENDING"]
            if pending_res:
                # Sort berdasarkan id_reservasi atau tanggal_reservasi (asumsi ID berurutan mewakili urutan pembuatan)
                pending_res.sort(key=lambda r: (r.tanggal_reservasi, r.id_reservasi))
                oldest_res = pending_res[0]
                oldest_res.status = "TERSEDIA"
                self._reservasi_storage.update(oldest_res.id_reservasi, oldest_res)

        return pengembalian

    def sinkronisasi_status_terlambat(self):
        """Memeriksa semua peminjaman aktif dan memperbarui status jika melewati batas jatuh tempo."""
        hari_ini = datetime.date.today()
        txs = self.get_all_transactions()
        for tx in txs:
            if isinstance(tx, Peminjaman) and tx.status == "DIPINJAM":
                jatuh_tempo = datetime.datetime.strptime(tx.tanggal_jatuh_tempo, "%Y-%m-%d").date()
                if hari_ini > jatuh_tempo:
                    tx.status = "TERLAMBAT"
                    self._transaksi_storage.update(tx.id_transaksi, tx)
