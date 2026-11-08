from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import datetime
from service.buku_service import BukuService
from service.anggota_service import AnggotaService
from service.transaksi_service import TransaksiService
from service.reservasi_service import ReservasiService
from exceptions import LibraSysException, InvalidInputError
from model.anggota import Anggota
from model.peminjaman import Peminjaman

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inisialisasi Service (Singleton-like untuk lifecycle aplikasi)
buku_service = BukuService()
anggota_service = AnggotaService()
transaksi_service = TransaksiService()
reservasi_service = ReservasiService()



# Filter & Setup Session Sebelum Menangani Request
@app.before_request
def setup_session():
    # Sinkronisasi status keterlambatan peminjaman secara otomatis
    transaksi_service.sinkronisasi_status_terlambat()
    
    # Kecualikan rute publik dan static files dari pemaksaan login
    endpoint = request.endpoint
    if endpoint not in ['login', 'static', None] and 'user_id' not in session:
        return redirect(url_for('login'))

# Route: Login (GET & POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '').strip()
        
        try:
            user = anggota_service.get_user_by_id(user_id)
            if user.password == password:
                session['user_id'] = user.id_pengguna
                session['user_name'] = user.nama
                session['user_role'] = user.role_name()
                if isinstance(user, Anggota):
                    session['user_maks_pinjam'] = user.maks_pinjam
                else:
                    session.pop('user_maks_pinjam', None)
                flash(f"Selamat datang kembali, {user.nama}!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Kata sandi salah. Silakan coba lagi.", "error")
        except Exception:
            flash(f"ID Pengguna '{user_id}' tidak terdaftar.", "error")
            
    return render_template('login.html')



# Route: Logout (POST)
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("Anda berhasil keluar dari sistem.", "success")
    return redirect(url_for('login'))


# Route: Dashboard
@app.route('/')
@app.route('/dashboard')
def dashboard():
    all_books = buku_service.get_all_books()
    all_users = anggota_service.get_all_users()
    all_txs = transaksi_service.get_all_transactions()
    all_res = reservasi_service.get_all_reservations()
    
    # Hitung Statistik
    stats = {
        "total_books": sum(b.stok for b in all_books),
        "total_members": sum(1 for u in all_users if isinstance(u, Anggota)),
        "active_loans": sum(1 for t in all_txs if isinstance(t, Peminjaman) and t.status in ["DIPINJAM", "TERLAMBAT"]),
        "pending_reservations": sum(1 for r in all_res if r.status == "PENDING")
    }
    
    # Riwayat Peminjaman & Pengembalian terbaru (5 transaksi terakhir)
    recent_transactions = sorted(all_txs, key=lambda t: t.tanggal, reverse=True)[:5]
    
    return render_template(
        'dashboard.html',
        active_page='dashboard',
        stats=stats,
        recent_transactions=recent_transactions
    )

# Route: Books List & Search
@app.route('/books')
def books():
    query = request.args.get('query', '')
    kategori = request.args.get('kategori', '')
    
    # Cari buku berdasarkan filter
    filtered_books = buku_service.cari_buku(query=query, kategori=kategori)
    
    # Ambil semua daftar kategori unik untuk dropdown
    all_books = buku_service.get_all_books()
    categories = sorted(list(set(book.kategori for book in all_books)))
    
    return render_template(
        'books.html',
        active_page='books',
        books=filtered_books,
        categories=categories,
        search_query=query,
        selected_category=kategori
    )

# Route: Add Book (Petugas Only)
@app.route('/books/add', methods=['POST'])
def add_book():
    if session.get('user_role') != 'Petugas':
        flash("Akses ditolak: Hanya petugas yang dapat menambahkan buku.", "error")
        return redirect(url_for('books'))
        
    try:
        data = {
            "isbn": request.form.get('isbn'),
            "judul": request.form.get('judul'),
            "penulis": request.form.get('penulis'),
            "kategori": request.form.get('kategori'),
            "stok": int(request.form.get('stok', 0))
        }
        buku_service.tambah_buku(data)
        flash(f"Buku '{data['judul']}' berhasil ditambahkan ke koleksi.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('books'))

# Route: Edit Book (Petugas Only)
@app.route('/books/edit/<isbn>', methods=['POST'])
def edit_book(isbn):
    if session.get('user_role') != 'Petugas':
        flash("Akses ditolak: Hanya petugas yang dapat mengedit buku.", "error")
        return redirect(url_for('books'))
        
    try:
        data = {
            "judul": request.form.get('judul'),
            "penulis": request.form.get('penulis'),
            "kategori": request.form.get('kategori'),
            "stok": int(request.form.get('stok', 0))
        }
        buku_service.ubah_buku(isbn, data)
        flash(f"Buku dengan ISBN {isbn} berhasil diperbarui.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('books'))

# Route: Delete Book (Petugas Only)
@app.route('/books/delete/<isbn>', methods=['POST'])
def delete_book(isbn):
    if session.get('user_role') != 'Petugas':
        flash("Akses ditolak: Hanya petugas yang dapat menghapus buku.", "error")
        return redirect(url_for('books'))
        
    try:
        # Cek apakah buku sedang dipinjam
        active_loans = [tx for tx in transaksi_service.get_all_transactions()
                       if isinstance(tx, Peminjaman) and tx.isbn == isbn and tx.status in ["DIPINJAM", "TERLAMBAT"]]
        if active_loans:
            raise InvalidInputError("Buku tidak dapat dihapus karena sedang dipinjam oleh anggota.")
            
        buku_service.hapus_buku(isbn)
        flash(f"Buku dengan ISBN {isbn} berhasil dihapus dari koleksi.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('books'))

# Route: Members Management (Petugas Only)
@app.route('/members')
def members():
    if session.get('user_role') != 'Petugas':
        flash("Akses ditolak: Halaman anggota hanya untuk petugas.", "error")
        return redirect(url_for('dashboard'))
        
    users = anggota_service.get_all_users()
    return render_template(
        'members.html',
        active_page='members',
        users=users
    )

# Route: Add Member (Petugas Only)
@app.route('/members/add-member', methods=['POST'])
def add_member():
    if session.get('user_role') != 'Petugas':
        flash("Akses ditolak.", "error")
        return redirect(url_for('members'))
        
    try:
        data = {
            "id_pengguna": request.form.get('id_pengguna'),
            "nama": request.form.get('nama'),
            "email": request.form.get('email'),
            "tipe_keanggotaan": request.form.get('tipe_keanggotaan')
        }
        anggota_service.tambah_anggota(data)
        flash(f"Anggota '{data['nama']}' (ID: {data['id_pengguna']}) berhasil didaftarkan.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('members'))

# Route: Add Officer (Petugas Only)
@app.route('/members/add-officer', methods=['POST'])
def add_officer():
    if session.get('user_role') != 'Petugas':
        flash("Akses ditolak.", "error")
        return redirect(url_for('members'))
        
    try:
        data = {
            "id_pengguna": request.form.get('id_pengguna'),
            "nama": request.form.get('nama'),
            "email": request.form.get('email'),
            "nip": request.form.get('nip')
        }
        anggota_service.tambah_petugas(data)
        flash(f"Petugas '{data['nama']}' (NIP: {data['nip']}) berhasil didaftarkan.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('members'))

# Route: Edit User (Petugas Only)
@app.route('/members/edit/<user_id>', methods=['POST'])
def edit_member(user_id):
    if session.get('user_role') != 'Petugas':
        flash("Akses ditolak.", "error")
        return redirect(url_for('members'))
        
    try:
        user = anggota_service.get_user_by_id(user_id)
        data = {
            "nama": request.form.get('nama'),
            "email": request.form.get('email')
        }
        
        if user.role_name() == 'Anggota':
            data["tipe_keanggotaan"] = request.form.get('tipe_keanggotaan')
            anggota_service.ubah_anggota(user_id, data)
        else:
            data["nip"] = request.form.get('nip')
            anggota_service.ubah_petugas(user_id, data)
            
        flash(f"Data pengguna '{user_id}' berhasil diperbarui.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('members'))

# Route: Delete User (Petugas Only)
@app.route('/members/delete/<user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('user_role') != 'Petugas':
        flash("Akses ditolak.", "error")
        return redirect(url_for('members'))
        
    try:
        # Cek jika anggota masih memiliki pinjaman aktif
        active_loans = transaksi_service.get_active_loans_by_member(user_id)
        if active_loans:
            raise InvalidInputError("Pengguna tidak dapat dihapus karena masih meminjam buku.")
            
        anggota_service.hapus_anggota(user_id)
        flash(f"Pengguna dengan ID {user_id} berhasil dihapus dari sistem.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('members'))

# Route: Circulation (Peminjaman & Pengembalian)
@app.route('/transactions')
def transactions():
    # Ambil list transaksi
    all_txs = transaksi_service.get_all_transactions()
    
    # Filter Privasi: Jika Anggota yang login, hanya tampilkan transaksinya sendiri
    if session.get('user_role') == 'Anggota':
        all_txs = [tx for tx in all_txs if getattr(tx, 'id_anggota', None) == session.get('user_id')]

    # Kelompokkan: Pisahkan peminjaman aktif & seluruh riwayat
    active_loans = []
    for tx in all_txs:
        if isinstance(tx, Peminjaman) and tx.status in ["DIPINJAM", "TERLAMBAT"]:
            active_loans.append(tx)
            
    # Urutkan seluruh transaksi agar terbaru muncul di atas
    sorted_txs = sorted(all_txs, key=lambda t: t.tanggal, reverse=True)
    
    # Ambil data pembantu untuk display nama di tabel
    users = anggota_service.get_all_users()
    member_names = {u.id_pengguna: u.nama for u in users}
    
    books = buku_service.get_all_books()
    book_titles = {b.isbn: b.judul for b in books}
    
    # Data pembantu form sirkulasi (hanya untuk petugas)
    members_list = [u for u in users if isinstance(u, Anggota)]
    available_books = [b for b in books if b.stok > 0]
    
    # Hitung perkiraan denda untuk pinjaman aktif (yang berstatus DIPINJAM/TERLAMBAT)
    estimated_fines = {}
    hari_ini = datetime.date.today()
    for loan in active_loans:
        jatuh_tempo = datetime.datetime.strptime(loan.tanggal_jatuh_tempo, "%Y-%m-%d").date()
        if hari_ini > jatuh_tempo:
            estimated_fines[loan.id_transaksi] = (hari_ini - jatuh_tempo).days * 2000
        else:
            estimated_fines[loan.id_transaksi] = 0
            
    return render_template(
        'transactions.html',
        active_page='transactions',
        active_loans=active_loans,
        all_transactions=sorted_txs,
        member_names=member_names,
        book_titles=book_titles,
        members=members_list,
        available_books=available_books,
        estimated_fines=estimated_fines
    )

# Route: Process Borrowing
@app.route('/transactions/borrow', methods=['POST'])
def borrow_book():
    # Tentukan ID peminjam: Jika petugas, gunakan id_anggota dari form; jika anggota, gunakan session user_id
    is_petugas = (session.get('user_role') == 'Petugas')
    id_anggota = request.form.get('id_anggota') if is_petugas else session.get('user_id')
    isbn = request.form.get('isbn')
    
    if not id_anggota:
        flash("ID Anggota harus diisi.", "error")
        return redirect(url_for('transactions'))
        
    try:
        peminjaman = transaksi_service.pinjam_buku(id_anggota, isbn)
        flash(f"Peminjaman berhasil dicatat dengan ID: {peminjaman.id_transaksi}. Jatuh tempo pada {peminjaman.tanggal_jatuh_tempo}.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    if is_petugas:
        return redirect(url_for('transactions'))
    return redirect(url_for('books'))

# Route: Process Returning (Petugas Only)
@app.route('/transactions/return', methods=['POST'])
def return_book():
    if session.get('user_role') != 'Petugas':
        flash("Akses ditolak: Hanya petugas yang dapat mencatat pengembalian.", "error")
        return redirect(url_for('transactions'))
        
    id_transaksi = request.form.get('id_transaksi')
    try:
        pengembalian = transaksi_service.kembalikan_buku(id_transaksi)
        msg = f"Buku berhasil dikembalikan. Transaksi Pengembalian: {pengembalian.id_transaksi}."
        if pengembalian.denda > 0:
            msg += f" Denda keterlambatan: Rp {pengembalian.denda}."
        flash(msg, "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('transactions'))

# Route: Reservations List
@app.route('/reservations')
def reservations():
    # Ambil semua reservasi
    all_res = reservasi_service.get_all_reservations()
    
    # Jika anggota biasa, filter hanya reservasi miliknya sendiri
    if session.get('user_role') == 'Anggota':
        all_res = [r for r in all_res if r.id_anggota == session.get('user_id')]
        
    # Sort: pending/tersedia di atas, disusul tanggal reservasi terbaru
    all_res = sorted(all_res, key=lambda r: (r.status not in ["PENDING", "TERSEDIA"], r.tanggal_reservasi), reverse=True)
    
    # Ambil data pembantu nama & judul
    users = anggota_service.get_all_users()
    member_names = {u.id_pengguna: u.nama for u in users}
    
    books = buku_service.get_all_books()
    book_titles = {b.isbn: b.judul for b in books}
    
    return render_template(
        'reservations.html',
        active_page='reservations',
        reservations=all_res,
        member_names=member_names,
        book_titles=book_titles
    )

# Route: Process Reservation
@app.route('/reservations/create', methods=['POST'])
def reserve_book():
    id_anggota = session.get('user_id')
    isbn = request.form.get('isbn')
    
    if session.get('user_role') == 'Petugas':
        flash("Petugas tidak perlu melakukan reservasi buku.", "error")
        return redirect(url_for('books'))
        
    try:
        res = reservasi_service.buat_reservasi(id_anggota, isbn)
        flash(f"Reservasi berhasil diajukan dengan ID: {res.id_reservasi}. Anda berada dalam antrean buku ini.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('reservations'))

# Route: Cancel Reservation
@app.route('/reservations/cancel/<id_reservasi>', methods=['POST'])
def cancel_reservation(id_reservasi):
    try:
        # Pengecekan otorisasi ditangani di service layer
        reservasi_service.batalkan_reservasi(id_reservasi)
        flash(f"Reservasi '{id_reservasi}' berhasil dibatalkan.", "success")
    except LibraSysException as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Terjadi kesalahan: {e}", "error")
        
    return redirect(url_for('reservations'))

if __name__ == '__main__':
    # Pastikan database folder ada
    if not os.path.exists("database"):
        os.makedirs("database")
        
    app.run(debug=True, host="127.0.0.1", port=5000)
