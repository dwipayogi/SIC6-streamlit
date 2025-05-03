import streamlit as st
import pandas as pd
import requests
import time
from script.langchain import analyze_summary

st.set_page_config(page_title="EduDetect", layout="wide")

# Fungsi untuk mengambil data terbaru dari API
def fetch_latest_data():
    try:
        response = requests.get("https://samsung.yogserver.web.id/data/latest")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Terjadi kesalahan saat mengambil data: Kode status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {e}")
        return None

# Fungsi untuk mengambil data historis (10 data terbaru)
def fetch_historical_data():
    try:
        response = requests.get("https://samsung.yogserver.web.id/data/sensor")
        if response.status_code == 200:
            data = response.json()
            recent_data = data[-10:] if len(data) > 10 else data
            return recent_data
        else:
            st.error(f"Terjadi kesalahan saat mengambil data historis: Kode status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengambil data historis: {e}")
        return None

# Sidebar
st.sidebar.header("Tentang EduDetect")
st.sidebar.write("EduDetect adalah sistem monitoring yang memantau kondisi lingkungan di ruang pendidikan.")

# Konten utama
st.title("EduDetect")
st.subheader("Dasbor Monitoring Lingkungan")

# Ambil dan tampilkan data terbaru (sekali saja, di luar loop)
latest_data = fetch_latest_data()

a, b, c = st.columns(3)

if latest_data:
    temp_value = f"{latest_data['temperature']}°C"
    humidity_value = f"{latest_data['humidity']}%"
    motion_value = "Aktif" if latest_data['motion'] == 1 else "Tidak Aktif"
    timestamp = latest_data['timestamp']
    st.caption(f"Terakhir diperbarui: {timestamp}")
else:
    temp_value = "30°C"
    humidity_value = "77%"
    motion_value = "Aktif"

a.metric("Suhu", temp_value, border=True)
b.metric("Kelembaban", humidity_value, border=True)
c.metric("Sensor Gerak", motion_value, border=True)

# Analisis satu kali saja
analysis = analyze_summary()
st.success(analysis)

# Tombol untuk memulai/berhenti refresh chart
run_charts = st.checkbox("Aktifkan Refresh Grafik Real-time", value=True)

# Placeholder untuk grafik real-time
temp_chart_placeholder = st.empty()
humidity_chart_placeholder = st.empty()

# Loop hanya untuk chart
while run_charts:
    historical_data = fetch_historical_data()

    if historical_data:
        df = pd.DataFrame(historical_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        temp_df = df[['timestamp', 'temperature']].rename(columns={'timestamp': 'Waktu', 'temperature': 'Suhu'})
        humidity_df = df[['timestamp', 'humidity']].rename(columns={'timestamp': 'Waktu', 'humidity': 'Kelembaban'})

        with temp_chart_placeholder.container():
            st.subheader("Data Suhu (Real-time)")
            st.line_chart(temp_df, x='Waktu', y='Suhu', use_container_width=True)

        with humidity_chart_placeholder.container():
            st.subheader("Data Kelembaban (Real-time)")
            st.line_chart(humidity_df, x='Waktu', y='Kelembaban', use_container_width=True)

    time.sleep(2)
