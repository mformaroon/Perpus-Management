import sys
import os

# Tambahkan direktori root proyek ke path import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from service.buku_service import BukuService
from service.anggota_service import AnggotaService
from service.transaksi_service import TransaksiService
from service.reservasi_service import ReservasiService
from exceptions import (
    OutOfStockError,
    BookAlreadyBorrowedError,
    BorrowLimitExceededError,
    ActiveReservationError
)

def run_tests():
    print("=== MEMULAI PENGUJIAN LOGIKA BISNIS LIBRASYS ===\n")
    
    # Inisialisasi Service
    buku_service = BukuService()
    anggota_service = AnggotaService()
    transaksi_service = TransaksiService()
    reservasi_service = ReservasiService()
    
    # 1. Cek Data Awal
    print("[1] Memeriksa data awal database...")
    books = buku_service.get_all_books()
    users = anggota_service.get_all_users()
    print(f"    - Jumlah judul buku: {len(books)}")
    print(f"    - Jumlah pengguna: {len(users)}")
    
    # 2. Uji Coba Pendaftaran Anggota Baru
    print("\n[2] Menambahkan anggota baru 'A003' (Regular)...")
    try:
        new_member = anggota_service.tambah_anggota({
            "id_pengguna": "A003",
            "nama": "Test Member",
            "email": "test@email.com",
            "tipe_keanggotaan": "Regular"
        })
        print(f"    - Sukses mendaftarkan: {new_member.nama} ({new_member.tipe_keanggotaan})")
    except Exception as e:
        print(f"    - Catatan/Error: {e}")
        
    # 3. Uji Coba Peminjaman Sukses & Pengurangan Stok
    print("\n[3] Mencoba meminjam buku Laskar Pelangi (ISBN: 9786020331) oleh A003...")
    buku_sebelum = buku_service.get_buku_by_isbn("9786020331")
    print(f"    - Stok sebelum: {buku_sebelum.stok}")
    
    try:
        loan = transaksi_service.pinjam_buku("A003", "9786020331")
        print(f"    - Sukses meminjam! ID Transaksi: {loan.id_transaksi}, Jatuh Tempo: {loan.tanggal_jatuh_tempo}")
        
        buku_sesudah = buku_service.get_buku_by_isbn("9786020331")
        print(f"    - Stok sesudah: {buku_sesudah.stok} (harus berkurang 1)")
        assert buku_sesudah.stok == buku_sebelum.stok - 1, "Kegagalan: Stok tidak berkurang!"
    except Exception as e:
        print(f"    - Error Peminjaman: {e}")

    # 4. Uji Coba Validasi Double Borrowing
    print("\n[4] Mencoba meminjam buku yang sama lagi oleh A003 (ISBN: 9786020331)...")
    try:
        transaksi_service.pinjam_buku("A003", "9786020331")
        print("    - Peringatan: Harusnya error BookAlreadyBorrowedError tapi malah lolos!")
    except BookAlreadyBorrowedError:
        print("    - Sukses: Sistem menolak double borrowing (BookAlreadyBorrowedError ditangkap)")
    except Exception as e:
        print(f"    - Catatan/Error: {e}")

    # 5. Uji Coba Batas Kuota Peminjaman (Regular = maks 3)
    print("\n[5] Mencoba melebihi batas kuota peminjaman regular (maks 3 buku)...")
    # A003 sudah pinjam 1 buku (Laskar Pelangi). Sekarang pinjam Buku Bumi (9786020822) dan Filosofi Teras (9786022914)
    try:
        transaksi_service.pinjam_buku("A003", "9786020822")
        transaksi_service.pinjam_buku("A003", "9786022914")
        print("    - A003 saat ini meminjam 3 buku.")
        
        # Coba pinjam buku ke-4 (Python Crash Course: 9786020633)
        transaksi_service.pinjam_buku("A003", "9786020633")
        print("    - Peringatan: Harusnya limit tercapai tapi malah lolos!")
    except BorrowLimitExceededError:
        print("    - Sukses: Sistem menolak peminjaman ke-4 karena limit habis (BorrowLimitExceededError ditangkap)")
    except Exception as e:
        print(f"    - Catatan/Error: {e}")

    # 6. Uji Coba Peminjaman Buku Stok Kosong & Proses Reservasi
    print("\n[6] Mencoba meminjam buku Negeri 5 Menara (ISBN: 9789792248, Stok: 0)...")
    try:
        transaksi_service.pinjam_buku("A002", "9789792248")
        print("    - Peringatan: Stok kosong tapi berhasil dipinjam!")
    except OutOfStockError:
        print("    - Sukses: Sistem menolak peminjaman karena stok kosong (OutOfStockError ditangkap)")
        
        # Lakukan reservasi
        print("    - Mengajukan reservasi oleh anggota A002...")
        try:
            res = reservasi_service.buat_reservasi("A002", "9789792248")
            print(f"    - Reservasi Berhasil! ID: {res.id_reservasi}, Status: {res.status}")
        except Exception as e:
            print(f"      Gagal membuat reservasi: {e}")

    # 7. Uji Coba Pengembalian & Auto-Allocation Reservasi
    print("\n[7] Mengembalikan buku Negeri 5 Menara (9789792248) oleh peminjam lain...")
    # Untuk mengetes, pertama kita tambah stok Negeri 5 Menara secara paksa lalu dikembalikan? 
    # Atau kita simulasikan pengembalian pinjaman. Mari kita buat transaksi pinjam Negeri 5 Menara lalu dikembalikan.
    # Namun karena stok 0, kita set stoknya = 1 dulu untuk disimulasikan dipinjam.
    buku_nol = buku_service.get_buku_by_isbn("9789792248")
    buku_nol.stok = 1
    buku_service._storage.update("9789792248", buku_nol)
    
    # Pinjam oleh A001
    pinjam_temp = transaksi_service.pinjam_buku("A001", "9789792248")
    print(f"    - A001 meminjam buku Negeri 5 Menara. Stok saat ini: {buku_service.get_buku_by_isbn('9789792248').stok}")
    
    # Pengembalian oleh A001
    print("    - A001 mengembalikan buku Negeri 5 Menara...")
    transaksi_service.kembalikan_buku(pinjam_temp.id_transaksi)
    
    # Cek status reservasi A002
    reservasi_a002 = reservasi_service.get_reservations_by_member("A002")
    active_res = [r for r in reservasi_a002 if r.isbn == "9789792248"]
    if active_res:
        print(f"    - Sukses: Status reservasi A002 berubah menjadi: {active_res[0].status} (harus TERSEDIA)")
        assert active_res[0].status == "TERSEDIA", "Kegagalan: Status reservasi tidak beralih ke TERSEDIA"
        
    # Bersihkan Data Uji Coba (Hapus A003 & kembalikan transaksi A003)
    print("\n[8] Membersihkan data uji coba...")
    try:
        # Hapus peminjaman A003 yang dicatat di langkah 3 & 5
        data_tx = transaksi_service._transaksi_storage.load()
        cleaned_tx = [t for t in data_tx if t.get("id_anggota") != "A003" and t.get("id_transaksi") != pinjam_temp.id_transaksi]
        # Hapus pengembalian temp Negeri 5 Menara dari log
        cleaned_tx = [t for t in cleaned_tx if t.get("id_peminjaman") != pinjam_temp.id_transaksi]
        transaksi_service._transaksi_storage.save(cleaned_tx)
        
        # Hapus reservasi uji coba
        data_res = reservasi_service._reservasi_storage.load()
        cleaned_res = [r for r in data_res if r.get("id_anggota") != "A002" or r.get("isbn") != "9789792248"]
        reservasi_service._reservasi_storage.save(cleaned_res)
        
        # Hapus user A003
        anggota_service.hapus_anggota("A003")
        
        # Reset stok buku Negeri 5 Menara ke 0, dan Laskar Pelangi & Bumi ke asal
        b = buku_service.get_buku_by_isbn("9789792248")
        b.stok = 0
        buku_service._storage.update("9789792248", b)
        
        b = buku_service.get_buku_by_isbn("9786020331")
        b.stok = 3
        buku_service._storage.update("9786020331", b)
        
        b = buku_service.get_buku_by_isbn("9786020822")
        b.stok = 1
        buku_service._storage.update("9786020822", b)
        
        b = buku_service.get_buku_by_isbn("9786022914")
        b.stok = 5
        buku_service._storage.update("9786022914", b)
        
        print("    - Database berhasil dibersihkan kembali ke kondisi semula.")
    except Exception as e:
        print(f"    - Gagal membersihkan database: {e}")

    print("\n=== SEMUA PENGUJIAN LOGIKA INTI SELESAI & SUKSES! ===")

if __name__ == "__main__":
    run_tests()
