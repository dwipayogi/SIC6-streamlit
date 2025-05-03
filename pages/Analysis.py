import streamlit as st
from script.langchain import analyze_data


st.set_page_config(page_title="EduDetect - Analisis", layout="wide")
st.title("Analisis Data oleh AI")

# Sidebar
st.sidebar.header("Analisis Data")
st.sidebar.write("EduDetect melakukan analisis data menggunakan AI untuk memberikan wawasan yang lebih dalam.")

if 'analysis_result' not in st.session_state:
    with st.spinner("Mengambil dan menganalisis data..."):
        st.session_state['analysis_result'] = analyze_data()

analysis = st.session_state['analysis_result']
st.success(analysis)