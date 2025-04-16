import streamlit as st
import requests
import pandas as pd
import json
import time

st.set_page_config(page_title="EduDetect - Riwayat Data", layout="wide")

# Sidebar
st.sidebar.header("Riwayat Data")
st.sidebar.write("Halaman ini menampilkan data historis.")

# Konten utama
st.title("Riwayat Data")
st.subheader("Data Historis")
st.write("Bagian ini menampilkan data historis yang telah terekam.")

placeholder = st.empty()

# Fungsi untuk mengambil data dari server
@st.cache_data(ttl=300)  # Cache data selama 5 menit
def fetch_data():
    try:
        response = requests.get("https://samsung.yogserver.web.id/data")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Terjadi kesalahan saat mengambil data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        return None

# Kontainer untuk menampilkan waktu refresh terakhir
refresh_info = st.container()
last_refresh = st.empty()

# Tombol refresh
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Muat Ulang Data"):
        # Hapus cache untuk mengambil data terbaru
        fetch_data.clear()
        # Perbarui waktu refresh terakhir
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        last_refresh.text(f"Terakhir dimuat ulang: {current_time}")

# Ambil dan tampilkan data
data = fetch_data()

if data:
    # Tampilkan data pada placeholder
    with placeholder.container():
        df = pd.DataFrame(data)
        st.dataframe(df)
else:
    with placeholder.container():
        st.warning("Data tidak tersedia. Silakan periksa koneksi server.")

# Dokumentasi:
# - Seluruh tampilan aplikasi telah diterjemahkan ke Bahasa Indonesia.
# - Komentar kode juga menggunakan Bahasa Indonesia untuk memudahkan pengembangan.
# - Fungsi utama: menampilkan data historis dari server.