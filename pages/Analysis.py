import streamlit as st
from script.langchain import analyze_data


st.set_page_config(page_title="EduDetect - Analisis", layout="wide")
st.title("Analisis Data oleh AI")

if st.button("Lakukan Analisis"):
    with st.spinner("Mengambil dan menganalisis data..."):
        analysis = analyze_data()
        st.success(analysis)