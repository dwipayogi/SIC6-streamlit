import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Memuat variabel lingkungan
load_dotenv()
client = Groq()

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="EduDetect - Chatbot", layout="wide")

# Sidebar Chatbot
st.sidebar.header("Chatbot")
st.sidebar.write("Chatbot AI EduDetect")

# Judul utama halaman
st.title("Chatbot AI")

# Inisialisasi session state untuk pesan jika belum ada
if "messages" not in st.session_state:
    st.session_state.messages = []

# Menampilkan riwayat chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input chat
if prompt := st.chat_input("Apa yang ingin Anda tanyakan?"):
    # Menambahkan pesan pengguna ke riwayat chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Menampilkan pesan pengguna
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Menampilkan respons asisten dalam kontainer chat
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Membuat permintaan ke API Groq
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ],
            temperature=0.7,
            max_completion_tokens=4096,
            stream=True,
        )
        
        # Menampilkan respons secara streaming
        for chunk in chat_completion:
            content = chunk.choices[0].delta.content or ""
            full_response += content
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    # Menambahkan respons asisten ke riwayat chat
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Dokumentasi:
# - Seluruh tampilan dan pesan pada aplikasi ini telah diterjemahkan ke dalam Bahasa Indonesia.
# - Komentar kode juga menggunakan Bahasa Indonesia untuk memudahkan pemahaman pengembang lokal.
# - Fungsi utama: menampilkan chat interaktif antara pengguna dan AI dengan riwayat percakapan.