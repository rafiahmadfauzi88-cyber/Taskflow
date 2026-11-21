from datetime import date

# Tuple daftar mata kuliah tetap (memenuhi ketentuan tipe data koleksi: list, dict, tuple, set)
DAFTAR_MATKUL = (
    "Bahasa Indonesia",
    "Sistem Operasi",
    "Dasar-Dasar Pemrograman",
    "Desain UI/UX",
    "Literasi Digital",
    "Pembentukan Karakter",
    "Matematika Komputer",
    "Organisasi dan Arsitektur Komputer",
)


class Tugas:
    """Class induk yang merepresentasikan entitas Tugas Kuliah."""

    def __init__(self, judul, matkul, tanggal_deadline, tingkat_kesulitan="Sedang"):
        self.judul = judul.strip()
        self.matkul = matkul.strip()
        self.tanggal_deadline = tanggal_deadline  # bertipe datetime.date
        self.tingkat_kesulitan = tingkat_kesulitan
        self.status = "Belum Selesai"

    def hitung_sisa_hari(self):
        """Menghitung selisih hari dari hari ini menuju deadline."""
        selisih = (self.tanggal_deadline - date.today()).days
        return selisih

    def cek_urgensi(self):
        """Menentukan kategori urgensi berdasarkan sisa hari (Percabangan)."""
        if self.status == "Selesai":
            return "Selesai", "success"

        sisa = self.hitung_sisa_hari()
        if sisa < 0:
            return f"Terlambat ({abs(sisa)} hari)", "error"
        elif sisa == 0:
            return "Hari Ini!", "error"
        elif sisa <= 2:
            return f"Mendesak ({sisa} hari lagi)", "warning"
        elif sisa <= 5:
            return f"Segera Kerjakan ({sisa} hari lagi)", "info"
        else:
            return f"Aman ({sisa} hari lagi)", "success"

    def tandai_selesai(self):
        """Mengubah status tugas menjadi Selesai."""
        self.status = "Selesai"

    def info_kategori(self):
        """Method dasar yang akan di-override oleh class turunan."""
        return "Tugas Umum"


class TugasIndividu(Tugas):
    """Class turunan (Inheritance) untuk tugas yang dikerjakan mandiri."""

    def __init__(self, judul, matkul, tanggal_deadline, tingkat_kesulitan="Sedang"):
        super().__init__(judul, matkul, tanggal_deadline, tingkat_kesulitan)
        self.kategori = "Individu"

    def info_kategori(self):
        return "Mandiri (Individu)"


class TugasKelompok(Tugas):
    """Class turunan (Inheritance) dengan atribut tambahan anggota tim."""

    def __init__(self, judul, matkul, tanggal_deadline, anggota_tim, tingkat_kesulitan="Sedang"):
        super().__init__(judul, matkul, tanggal_deadline, tingkat_kesulitan)
        self.kategori = "Kelompok"
        self.anggota_tim = anggota_tim.strip() if anggota_tim.strip() else "-"

    def info_kategori(self):
        return f"Kelompok ({self.anggota_tim})"


def validasi_input_tugas(judul, matkul, kategori, anggota_tim):
    """Memvalidasi input form agar tidak ada data kosong yang masuk."""
    if not judul.strip():
        return False, "Judul tugas tidak boleh kosong."
    if matkul not in DAFTAR_MATKUL:
        return False, "Mata kuliah tidak valid."
    if kategori == "Kelompok" and not anggota_tim.strip():
        return False, "Untuk tugas kelompok, isi minimal satu nama anggota tim."
    return True, "Valid"


def hitung_statistik_tugas(daftar_tugas):
    """Menghitung ringkasan jumlah tugas menggunakan perulangan dan dictionary."""
    bobot_skor = {"Mudah": 1, "Sedang": 2, "Sulit": 3}
    rekap = {
        "total": len(daftar_tugas),
        "selesai": 0,
        "aktif": 0,
        "mendesak": 0,
        "total_beban_skor": 0,
    }

    for tugas in daftar_tugas:
        if tugas.status == "Selesai":
            rekap["selesai"] += 1
        else:
            rekap["aktif"] += 1
            rekap["total_beban_skor"] += bobot_skor.get(tugas.tingkat_kesulitan, 1)
            if tugas.hitung_sisa_hari() <= 2:
                rekap["mendesak"] += 1

    if rekap["total"] > 0:
        rekap["persen_selesai"] = round((rekap["selesai"] / rekap["total"]) * 100, 1)
    else:
        rekap["persen_selesai"] = 0.0

    return rekap


def filter_tugas(daftar_tugas, filter_matkul="Semua", filter_status="Semua"):
    """Memfilter list objek tugas berdasarkan mata kuliah dan status pengerjaan."""
    hasil = []
    for tugas in daftar_tugas:
        cocok_matkul = (filter_matkul == "Semua") or (tugas.matkul == filter_matkul)
        cocok_status = (filter_status == "Semua") or (tugas.status == filter_status)
        if cocok_matkul and cocok_status:
            hasil.append(tugas)
    return hasil


def hitung_tugas_selesai_rekursif(daftar_tugas, indeks=0):
    """Fungsi rekursif (Nilai Tambah) untuk menghitung jumlah tugas berstatus Selesai."""
    if indeks >= len(daftar_tugas):
        return 0
    hitung_sekarang = 1 if daftar_tugas[indeks].status == "Selesai" else 0
    return hitung_sekarang + hitung_tugas_selesai_rekursif(daftar_tugas, indeks + 1)