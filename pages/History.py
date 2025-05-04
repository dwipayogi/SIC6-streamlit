import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="EduDetect - Riwayat Data", layout="wide")

# Sidebar History
st.sidebar.header("History")
st.sidebar.write("Halaman ini menampilkan riwayat data sensor dan deteksi siswa.")

# Konten utama
st.title("EduDetect - Riwayat Data")

# Area filter di bagian atas
with st.container():
    st.markdown("### Filter Data")
    
    # Layout untuk filter dan refresh button
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Date picker untuk memilih hari
        today = datetime.now().date()
        selected_date = st.date_input("Pilih Tanggal", today)

# Placeholder untuk data
placeholder_sensor = st.empty()
placeholder_streamlit = st.empty()

# Fungsi untuk mengambil data dari server
@st.cache_data(ttl=300)  # Cache data selama 5 menit
def fetch_data_sensor():
    try:
        response = requests.get("https://samsung.yogserver.web.id/data/sensor")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Terjadi kesalahan saat mengambil data sensor: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengambil data sensor: {e}")
        return None
    
@st.cache_data(ttl=300)  # Cache data selama 5 menit
def fetch_data_streamlit():
    try:
        response = requests.get("https://samsung.yogserver.web.id/data/streamlit")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Terjadi kesalahan saat mengambil data streamlit: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengambil data streamlit: {e}")
        return None

# Garis pemisah
st.markdown("---")

# Fungsi untuk menampilkan dataframe dengan pemfilteran tanggal
def display_filtered_data(df, data_name):
    # Konversi kolom timestamp ke format datetime jika ada
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter data berdasarkan tanggal yang dipilih
        selected_date_str = selected_date.strftime('%Y-%m-%d')
        filtered_df = df[df['timestamp'].dt.strftime('%Y-%m-%d') == selected_date_str]
        
        st.subheader(f"{data_name}")
        if len(filtered_df) > 0:
            st.dataframe(filtered_df, use_container_width=True)
            st.caption(f"Menampilkan {len(filtered_df)} {data_name.lower()} pada tanggal {selected_date_str}")
        else:
            st.warning(f"Tidak ada {data_name.lower()} tersedia untuk tanggal {selected_date_str}")
    else:
        st.subheader(f"{data_name}")
        st.dataframe(df, use_container_width=True)
        st.caption(f"Kolom timestamp tidak ditemukan dalam {data_name.lower()}. Menampilkan semua data.")

# Tampilkan Data Sensor
data_sensor = fetch_data_sensor()
if data_sensor:
    df_sensor = pd.DataFrame(data_sensor)
    display_filtered_data(df_sensor, "Riwayat Data Sensor IoT")
else:
    st.subheader("Riwayat Data Sensor ioT")
    st.warning("Data sensor tidak tersedia. Silakan periksa koneksi server.")

# Garis pemisah
st.markdown("---")

# Tampilkan Data Streamlit
data_streamlit = fetch_data_streamlit()
if data_streamlit:
    df_streamlit = pd.DataFrame(data_streamlit)
    display_filtered_data(df_streamlit, "Riwayat Data Deteksi Siswa")
else:
    st.subheader("Riwayat Data Deteksi Siswa")
    st.warning("Data streamlit tidak tersedia. Silakan periksa koneksi server.")