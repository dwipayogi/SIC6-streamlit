import streamlit as st
import urllib.request
import numpy as np
import cv2
import os
from PIL import Image
import time

st.set_page_config(page_title="EduDetect - Deteksi", layout="wide")

# Inisialisasi Streamlit session state
if 'run' not in st.session_state:
    st.session_state.run = False

# URL ESP32-CAM
ESP32_URL = "http://192.168.186.73/capture"

# Load Haarcascade untuk deteksi wajah
cascPath = os.path.join("src", "haarcascade_frontalface_default.xml")  # Pastikan ini path ke model wajah
faceCascade = cv2.CascadeClassifier(cascPath)

if faceCascade.empty():
    st.error("Kesalahan: Haarcascade tidak ditemukan.")
    st.stop()

st.title("Deteksi Wajah dari ESP32-CAM")

# Tombol kontrol kamera
col1, col2 = st.columns(2)
with col1:
    if st.button("Mulai"):
        st.session_state.run = True
with col2:
    if st.button("Berhenti"):
        st.session_state.run = False

# Placeholder untuk video & teks
frame_placeholder = st.empty()
text_placeholder = st.empty()

def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    return frame, len(faces)

# Jalankan stream dari ESP32 jika "run" aktif
if st.session_state.run:
    while True:
        try:
            resp = urllib.request.urlopen(ESP32_URL, timeout=5)
            image_array = np.array(bytearray(resp.read()), dtype=np.uint8)
            frame = cv2.imdecode(image_array, -1)

            if frame is None:
                text_placeholder.warning("Frame kosong dari ESP32.")
                continue

            frame, face_count = detect_faces(frame)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)

            frame_placeholder.image(img, caption="Streaming dari ESP32-CAM", use_column_width=True)

            # Output jumlah wajah
            if face_count == 0:
                text_placeholder.info("Tidak ada orang terdeteksi.")
            elif face_count == 1:
                text_placeholder.success("Satu orang terdeteksi.")
            elif face_count == 2:
                text_placeholder.success("Dua orang terdeteksi.")
            else:
                text_placeholder.success(f"{face_count} orang terdeteksi.")
                
            time.sleep(0.1)

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
            break
else:
    st.info("Klik 'Mulai' untuk mulai membaca dari ESP32-CAM.")

# Dokumentasi:
# - Seluruh tampilan aplikasi telah diterjemahkan ke Bahasa Indonesia.
# - Komentar kode juga menggunakan Bahasa Indonesia untuk memudahkan pengembangan.
# - Fungsi utama: deteksi wajah secara real-time dari kamera ESP32-CAM.