# agent.py
import os
import pandas as pd
from pymongo import MongoClient
import google.generativeai as genai

# === Konfigurasi API ===
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
MONGO_URI = os.environ.get("MONGO_URI")
genai.configure(api_key=GOOGLE_API_KEY)

# === MongoDB Setup ===
client = MongoClient(MONGO_URI)
db = client['samsung']
collection = db['sensor']

# === Fungsi ambil dan analisis data sensor ===
def analyze_summary():
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        return "Data sensor tidak ditemukan."

    df = pd.DataFrame(data)

    # Statistik ringkas
    summary = {
        "Jumlah data": len(df),
        "Rata-rata suhu": round(df["temperature"].mean(), 2),
        "Suhu maksimum": df["temperature"].max(),
        "Suhu minimum": df["temperature"].min(),
        "Rata-rata kelembaban": round(df["humidity"].mean(), 2),
    }

    # Format ke dalam string untuk prompt
    summary_text = "\n".join([f"- {key}: {value}" for key, value in summary.items()])
    prompt = f"""
Berikut adalah ringkasan statistik:

{summary_text}

Tolong buatkan informasi deskriptif seperti penjelasan manusia, dalam bahasa Indonesia. Hubungkan dengan kondisi lingkungan dan perilaku ketika pembelajaran, Jelaskan secara singkat maksimal 2 paragraf.
"""

    # Kirim ke Gemini
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def analyze_data():
    data = list(collection.find({}, {"_id": 0}))
    if not data:
        return "Data sensor tidak ditemukan."

    df = pd.DataFrame(data)

    # Statistik ringkas
    summary = {
        "Jumlah data": len(df),
        "Rata-rata suhu": round(df["temperature"].mean(), 2),
        "Suhu maksimum": df["temperature"].max(),
        "Suhu minimum": df["temperature"].min(),
        "Rata-rata kelembaban": round(df["humidity"].mean(), 2),
    }

    # Format ke dalam string untuk prompt
    summary_text = "\n".join([f"- {key}: {value}" for key, value in summary.items()])
    prompt = f"""
Berikut adalah ringkasan statistik:

{summary_text}

Tolong buatkan analisis deskriptif seperti penjelasan manusia, dalam bahasa Indonesia. Hubungkan dengan kondisi lingkungan dan perilaku ketika pembelajaran, Buat analisis yang mendalam dan informasi yang berguna untuk tindak lanjut.
"""

    # Kirim ke Gemini
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text