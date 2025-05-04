import streamlit as st
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
import plotly.graph_objects as go
import threading
import requests
import altair as alt
import datetime
import urllib.request
import time

# Konfigurasi halaman
st.set_page_config(page_title="Smart Deteksi Kelas", layout="wide")
st.title("🎥 Smart Deteksi Siswa di Kelas")

# Sidebar
st.sidebar.header("Sistem Deteksi")
st.sidebar.write("EduDetect melakukan deteksi siswa di kelas menggunakan AI berbasis Computer Vision secara real-time.")

# Tambahkan pilihan sumber input
input_source = st.sidebar.radio(
    "Pilih Sumber Input:",
    ["ESP32-CAM Live Stream", "File Video"]
)

# Cache model
@st.cache_resource
def load_model():
    return YOLO("../my_model/my_model.pt")

model = load_model()

# Mapping label
label_short = {
    'memperhatikan': 'M',
    'tidak_memperhatikan': 'TM'
}

# Fungsi untuk mengambil data terbaru dari API
def fetch_latest_data():
    try:
        response = requests.get("https://samsung.yogserver.web.id/data/streamlit")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Terjadi kesalahan saat mengambil data: Kode status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {e}")
        return None
    
# Fungsi untuk logging data ke server secara paralel
def send_log(attentive_count, inattentive_count):
    try:
        requests.post(
            "https://samsung.yogserver.web.id/data/post/streamlit",
            json={
                "attentive_count": attentive_count,
                "inattentive_count": inattentive_count,
            },
            timeout=1
        )
    except Exception as e:
        print(f"Logging gagal: {e}")

# Fungsi ambil gambar dari ESP32
def get_capture_frame(url):
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        image_array = np.asarray(bytearray(resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        st.error(f"Gagal mengambil gambar dari ESP32-CAM: {e}")
        return None

# Fungsi untuk memproses frame
def process_frame(frame, frame_no):
    results = model.predict(source=frame, conf=0.3, stream=True)
    
    attentive_count = 0
    inattentive_count = 0
    
    for r in results:
        img = r.orig_img.copy()
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            short_label = label_short.get(label, label)

            if short_label == 'M':
                color = (0, 255, 0)
                attentive_count += 1
            elif short_label == 'TM':
                color = (0, 0, 255)
                inattentive_count += 1
            else:
                color = (255, 255, 0)

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, short_label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Return processed image and counts
    return img, attentive_count, inattentive_count

# Fungsi untuk mengupdate visualisasi
def update_visualizations(img, attentive_count, inattentive_count, video_placeholder, chart_placeholder, text_placeholder, frame_no):
    total = attentive_count + inattentive_count
    percent = int((attentive_count / total) * 100) if total > 0 else 0

    # Tampilkan frame
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    video_placeholder.image(img_rgb, channels="RGB", use_container_width=True)

    # Pie chart
    fig = go.Figure(data=[go.Pie(
        labels=["Memperhatikan", "Tidak"],
        values=[attentive_count, inattentive_count],
        hole=0.6,
        marker_colors=["lightgreen", "red"],
        textinfo='none',
        sort=False,
        direction='clockwise'
    )])

    fig.update_layout(
        showlegend=False,
        annotations=[dict(text=f"{percent}%", x=0.5, y=0.5, font_size=24, showarrow=False)],
        margin=dict(t=10, b=10, l=10, r=10),
        height=300
    )

    chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{frame_no}")
    text_placeholder.markdown(
        "<h5 style='text-align: center;'>Siswa Memperhatikan</h5>",
        unsafe_allow_html=True
    )

# Fungsi untuk menampilkan data historis 
def display_historical_data():
    data = fetch_latest_data()
    if data:
        st.subheader("Data Historis Perhatian Siswa")
        chart_data = pd.DataFrame(data)
        if 'timestamp' in chart_data.columns:
            chart_data['timestamp'] = pd.to_datetime(chart_data['timestamp'])

            # Ubah nama kolom untuk label Indonesia
            renamed_data = chart_data.rename(columns={
                'attentive_count': 'Memperhatikan',
                'inattentive_count': 'Tidak Memperhatikan'
            })

            # Ubah format untuk Altair
            melted_data = renamed_data.melt(
                id_vars=['timestamp'],
                value_vars=['Memperhatikan', 'Tidak Memperhatikan'],
                var_name='Kategori',
                value_name='Jumlah'
            )

            # Chart dengan label dan tooltip Bahasa Indonesia
            chart = alt.Chart(melted_data).mark_line(point=True).encode(
                x=alt.X('timestamp:T', title='Waktu', axis=alt.Axis(format='%H:%M:%S')),
                y=alt.Y('Jumlah:Q', title='Jumlah Siswa'),
                color=alt.Color('Kategori:N', title='Kategori', scale=alt.Scale(domain=['Memperhatikan', 'Tidak Memperhatikan'], range=['green', 'red'])),
                tooltip=[
                    alt.Tooltip('timestamp:T', title='Waktu', format='%Y-%m-%d %H:%M:%S'),
                    alt.Tooltip('Kategori:N', title='Kategori'),
                    alt.Tooltip('Jumlah:Q', title='Jumlah Siswa')
                ]
            ).properties(
                width='container',
                height=300
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.line_chart(chart_data[['Memperhatikan', 'Tidak Memperhatikan']], use_container_width=True)

# Tampilkan antarmuka berdasarkan pilihan sumber input
if input_source == "File Video":
    # Upload video
    video_file = st.file_uploader("Upload Video MP4", type=["mp4"])
    
    if video_file is not None:
        tfile = open("temp_video.mp4", 'wb')
        tfile.write(video_file.read())
        video_path = "temp_video.mp4"

        cap = cv2.VideoCapture(video_path)
        frame_no = 0

        col1, col2 = st.columns([2, 1])
        video_placeholder = col1.empty()
        chart_placeholder = col2.empty()
        text_placeholder = col2.empty()
        line_chart_placeholder = st.empty()

        process_every_n_frames = 2
        log_every_n_frames = 15
        
        # Data untuk real-time line chart
        detection_history = {
            'timestamp': [],
            'Memperhatikan': [],
            'Tidak Memperhatikan': []
        }

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 360))

            if frame_no % process_every_n_frames == 0:
                img, attentive_count, inattentive_count = process_frame(frame, frame_no)
                
                # Kirim log tiap N frame di background
                if frame_no % log_every_n_frames == 0:
                    threading.Thread(
                        target=send_log,
                        args=(attentive_count, inattentive_count),
                        daemon=True
                    ).start()
                    
                    # Tambahkan data ke history untuk line chart
                    current_time = datetime.datetime.now()
                    detection_history['timestamp'].append(current_time)
                    detection_history['Memperhatikan'].append(attentive_count)
                    detection_history['Tidak Memperhatikan'].append(inattentive_count)
                    
                    # Batasi jumlah data yang ditampilkan (tampilkan 30 titik terakhir)
                    if len(detection_history['timestamp']) > 30:
                        detection_history['timestamp'] = detection_history['timestamp'][-30:]
                        detection_history['Memperhatikan'] = detection_history['Memperhatikan'][-30:]
                        detection_history['Tidak Memperhatikan'] = detection_history['Tidak Memperhatikan'][-30:]
                    
                    # Update real-time line chart jika ada data
                    if len(detection_history['timestamp']) > 1:
                        history_df = pd.DataFrame(detection_history)
                        
                        # Ubah format untuk Altair
                        melted_history = history_df.melt(
                            id_vars=['timestamp'],
                            value_vars=['Memperhatikan', 'Tidak Memperhatikan'],
                            var_name='Kategori',
                            value_name='Jumlah'
                        )
                        
                        # Buat line chart real-time
                        real_time_chart = alt.Chart(melted_history).mark_line(point=True).encode(
                            x=alt.X('timestamp:T', title='Waktu', axis=alt.Axis(format='%H:%M:%S')),
                            y=alt.Y('Jumlah:Q', title='Jumlah Siswa'),
                            color=alt.Color('Kategori:N', title='Kategori', scale=alt.Scale(domain=['Memperhatikan', 'Tidak Memperhatikan'], range=['green', 'red'])),
                            tooltip=[
                                alt.Tooltip('timestamp:T', title='Waktu', format='%Y-%m-%d %H:%M:%S'),
                                alt.Tooltip('Kategori:N', title='Kategori'),
                                alt.Tooltip('Jumlah:Q', title='Jumlah Siswa')
                            ]
                        ).properties(
                            width='container',
                            height=300,
                            title="Tren Perhatian Siswa Secara Real-time"
                        ).interactive()
                        
                        line_chart_placeholder.altair_chart(real_time_chart, use_container_width=True)

                update_visualizations(img, attentive_count, inattentive_count, video_placeholder, chart_placeholder, text_placeholder, frame_no)

            frame_no += 1
            cv2.waitKey(1)

        cap.release()
        st.success("Pemrosesan video selesai!")

    # Tampilkan data historis
    display_historical_data()

else:  # ESP32-CAM Live Stream
    # Input URL ESP32-CAM
    esp_url = st.text_input("Masukkan URL ESP32-CAM", value="http://192.168.100.168/capture")
    
    # Tombol mulai
    run_stream = st.button("Mulai Deteksi Live")
    
    if run_stream and esp_url:
        # Layout
        col1, col2 = st.columns([2, 1])
        video_placeholder = col1.empty()
        chart_placeholder = col2.empty()
        text_placeholder = col2.empty()
        line_chart_placeholder = st.empty()
        
        frame_no = 0
        streaming_active = True
        
        # Data untuk real-time line chart
        detection_history = {
            'timestamp': [],
            'Memperhatikan': [],
            'Tidak Memperhatikan': []
        }
        
        # Buat tombol Stop di luar loop untuk menghindari pembuatan berulang
        stop_button_col = st.columns(3)[1]  # Menempatkan tombol di tengah
        stop_button = stop_button_col.button("Stop Deteksi")
        
        while streaming_active and not stop_button:
            frame = get_capture_frame(esp_url)
            if frame is None:
                st.warning("Tidak dapat terhubung ke ESP32-CAM. Coba lagi dalam 3 detik...")
                time.sleep(3)
                continue
                
            img, attentive_count, inattentive_count = process_frame(frame, frame_no)
            
            # Update visualisasi
            update_visualizations(img, attentive_count, inattentive_count, video_placeholder, chart_placeholder, text_placeholder, frame_no)
            
            # Log dan update chart setiap 5 frame
            if frame_no % 5 == 0:
                # Kirim log
                threading.Thread(
                    target=send_log,
                    args=(attentive_count, inattentive_count),
                    daemon=True
                ).start()
                
                # Update line chart
                current_time = datetime.datetime.now()
                detection_history['timestamp'].append(current_time)
                detection_history['Memperhatikan'].append(attentive_count)
                detection_history['Tidak Memperhatikan'].append(inattentive_count)
                
                # Batasi jumlah data
                if len(detection_history['timestamp']) > 30:
                    detection_history['timestamp'] = detection_history['timestamp'][-30:]
                    detection_history['Memperhatikan'] = detection_history['Memperhatikan'][-30:]
                    detection_history['Tidak Memperhatikan'] = detection_history['Tidak Memperhatikan'][-30:]
                
                # Update real-time line chart
                if len(detection_history['timestamp']) > 1:
                    history_df = pd.DataFrame(detection_history)
                    
                    # Ubah format untuk Altair
                    melted_history = history_df.melt(
                        id_vars=['timestamp'],
                        value_vars=['Memperhatikan', 'Tidak Memperhatikan'],
                        var_name='Kategori',
                        value_name='Jumlah'
                    )
                    
                    # Buat line chart real-time
                    real_time_chart = alt.Chart(melted_history).mark_line(point=True).encode(
                        x=alt.X('timestamp:T', title='Waktu', axis=alt.Axis(format='%H:%M:%S')),
                        y=alt.Y('Jumlah:Q', title='Jumlah Siswa'),
                        color=alt.Color('Kategori:N', title='Kategori', scale=alt.Scale(domain=['Memperhatikan', 'Tidak Memperhatikan'], range=['green', 'red'])),
                        tooltip=[
                            alt.Tooltip('timestamp:T', title='Waktu', format='%Y-%m-%d %H:%M:%S'),
                            alt.Tooltip('Kategori:N', title='Kategori'),
                            alt.Tooltip('Jumlah:Q', title='Jumlah Siswa')
                        ]
                    ).properties(
                        width='container',
                        height=300,
                        title="Tren Perhatian Siswa Secara Real-time"
                    ).interactive()
                    
                    line_chart_placeholder.altair_chart(real_time_chart, use_container_width=True)
            
            frame_no += 1
            time.sleep(0.2)  # 5 fps
            
            # Check if stop button is pressed using Streamlit's experimental get_query_params
            stop_button = stop_button_col.button("Stop Deteksi", key=f"stop_btn_{frame_no}")
            if stop_button:
                streaming_active = False
                break
        
        st.success("Deteksi live stream dihentikan")
        
        # Tampilkan data historis setelah streaming dihentikan
        display_historical_data()
    else:
        # Tampilkan data historis jika belum memulai streaming
        display_historical_data()