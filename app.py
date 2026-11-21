from datetime import date, timedelta
import streamlit as st
from logika import (
    DAFTAR_MATKUL,
    TugasIndividu,
    TugasKelompok,
    validasi_input_tugas,
    hitung_statistik_tugas,
    filter_tugas,
    hitung_tugas_selesai_rekursif,
)

st.set_page_config(
    page_title="TaskFlow - Sistem Pengelolaan Tugas & Deadline Mahasiswa",
    layout="centered",
)

# Inisialisasi data awal pada session_state (contoh tugas kuliah STT-NF)
if "daftar_tugas" not in st.session_state:
    hari_ini = date.today()
    st.session_state.daftar_tugas = [
        TugasKelompok(
            judul="Proyek Akhir Aplikasi Python Streamlit",
            matkul="Dasar-Dasar Pemrograman",
            tanggal_deadline=hari_ini + timedelta(days=2),
            anggota_tim="Rafi, Anggota 2, Anggota 3, Anggota 4",
            tingkat_kesulitan="Sulit",
        ),
        TugasIndividu(
            judul="Tugas 10: Penulisan Bab I Pendahuluan",
            matkul="Bahasa Indonesia",
            tanggal_deadline=hari_ini + timedelta(days=4),
            tingkat_kesulitan="Sedang",
        ),
        TugasIndividu(
            judul="Perancangan Wireframe Low-Fidelity",
            matkul="Desain UI/UX",
            tanggal_deadline=hari_ini + timedelta(days=6),
            tingkat_kesulitan="Sedang",
        ),
        TugasIndividu(
            judul="Latihan Konversi Bilangan & Gerbang Logika",
            matkul="Organisasi dan Arsitektur Komputer",
            tanggal_deadline=hari_ini + timedelta(days=1),
            tingkat_kesulitan="Mudah",
        ),
        TugasIndividu(
            judul="Instalasi & Perintah Dasar Linux",
            matkul="Sistem Operasi",
            tanggal_deadline=hari_ini - timedelta(days=2),
            tingkat_kesulitan="Mudah",
        ),
    ]
    # Tandai tugas Sistem Operasi sebagai contoh yang sudah dikumpulkan
    st.session_state.daftar_tugas[4].tandai_selesai()

st.title("TaskFlow")
st.write("Sistem Pengelolaan Tugas & Deadline Mahasiswa")

# Panduan singkat cara pakai (bisa dibuka/tutup dengan st.expander)
with st.expander("Cara Menggunakan Aplikasi TaskFlow"):
    st.write(
        """
        1. **Pantau Ringkasan:** Lihat jumlah tugas aktif, tugas mendesak, dan persentase progres pada kartu metrik di atas.
        2. **Tambah Tugas Baru:** Pilih kategori (*Individu* atau *Kelompok*), pilih mata kuliah, isi judul tugas sesuai Elena NF, tentukan deadline, lalu klik **Simpan Tugas**.
        3. **Filter Daftar Tugas:** Gunakan menu filter di bagian bawah untuk melihat tugas berdasarkan mata kuliah atau status tertentu.
        4. **Update Status Selesai:** Jika tugas sudah dikumpulkan, pilih tugas pada menu **Tandai Tugas Sudah Selesai** dan klik tombol konfirmasi.
        """
    )

# --- BAGIAN 1: RINGKASAN STATISTIK ---
stats = hitung_statistik_tugas(st.session_state.daftar_tugas)
total_selesai_rekursif = hitung_tugas_selesai_rekursif(st.session_state.daftar_tugas)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Tugas", stats["total"])
col2.metric("Tugas Aktif", stats["aktif"])
col3.metric("Mendesak (<=2 Hari)", stats["mendesak"])
col4.metric("Progres Selesai", f"{stats['persen_selesai']}% ({total_selesai_rekursif})")

st.divider()

# --- BAGIAN 2: FORM TAMBAH TUGAS BARU ---
st.subheader("1. Tambah Tugas Kuliah")

kategori_pilih = st.selectbox("Kategori Tugas:", ["Individu", "Kelompok"])

with st.form("form_tambah_tugas", clear_on_submit=True):
    judul_input = st.text_input("Judul Tugas (sesuai tugas di Elena NF)")
    matkul_input = st.selectbox("Mata Kuliah", DAFTAR_MATKUL)
    deadline_input = st.date_input("Tanggal Deadline", value=date.today() + timedelta(days=3))
    kesulitan_input = st.selectbox("Tingkat Kesulitan", ["Mudah", "Sedang", "Sulit"])

    anggota_input = ""
    if kategori_pilih == "Kelompok":
        anggota_input = st.text_input("Anggota Kelompok (pisahkan dengan koma)")

    submit_btn = st.form_submit_button("Simpan Tugas")

    if submit_btn:
        valid, pesan = validasi_input_tugas(
            judul_input, matkul_input, kategori_pilih, anggota_input
        )
        if not valid:
            st.error(pesan)
        else:
            if kategori_pilih == "Individu":
                tugas_baru = TugasIndividu(
                    judul_input, matkul_input, deadline_input, kesulitan_input
                )
            else:
                tugas_baru = TugasKelompok(
                    judul_input, matkul_input, deadline_input, anggota_input, kesulitan_input
                )

            st.session_state.daftar_tugas.append(tugas_baru)
            st.success(f"Tugas '{judul_input}' ({matkul_input}) berhasil ditambahkan!")
            st.rerun()

st.divider()

# --- BAGIAN 3: DAFTAR TUGAS, FILTER, & UPDATE STATUS ---
st.subheader("2. Daftar & Status Deadline Tugas")

opsi_filter_matkul = ["Semua"] + list(DAFTAR_MATKUL)

col_f1, col_f2 = st.columns(2)
with col_f1:
    pilih_matkul = st.selectbox("Filter Mata Kuliah:", opsi_filter_matkul)
with col_f2:
    pilih_status = st.selectbox("Filter Status:", ["Semua", "Belum Selesai", "Selesai"])

tugas_tersaring = filter_tugas(st.session_state.daftar_tugas, pilih_matkul, pilih_status)

if not tugas_tersaring:
    st.info("Tidak ada tugas yang sesuai dengan filter saat ini.")
else:
    tabel_tampil = []
    for t in tugas_tersaring:
        label_urgensi, _ = t.cek_urgensi()
        tabel_tampil.append({
            "Mata Kuliah": t.matkul,
            "Judul Tugas": t.judul,
            "Kategori": t.info_kategori(),
            "Deadline": str(t.tanggal_deadline),
            "Kesulitan": t.tingkat_kesulitan,
            "Status / Urgensi": label_urgensi,
        })

    st.dataframe(tabel_tampil, use_container_width=True)

    # Form aksi cepat untuk menandai tugas selesai
    tugas_belum_selesai = [
        t for t in st.session_state.daftar_tugas if t.status == "Belum Selesai"
    ]
    if tugas_belum_selesai:
        st.write("**Tandai Tugas Sudah Selesai:**")
        opsi_judul = [f"{t.matkul} - {t.judul}" for t in tugas_belum_selesai]
        pilihan_selesai = st.selectbox("Pilih tugas yang sudah dikumpulkan:", opsi_judul)

        if st.button("Tandai Selesai"):
            indeks_terpilih = opsi_judul.index(pilihan_selesai)
            tugas_belum_selesai[indeks_terpilih].tandai_selesai()
            st.success("Status tugas diperbarui menjadi Selesai!")
            st.rerun()