import streamlit as st
from openai import OpenAI
import PyPDF2
import os
import io
import pandas as pd

# Configuración API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ID de tu asistente en OpenAI (cámbialo por el real de GenAI-Prove)
ASSISTANT_ID = "asst_xxxxxxxxxxxxx"

# --- Funciones auxiliares ---
def extract_text_from_pdf(uploaded_file):
    """Extrae texto de un PDF subido"""
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def create_word(content):
    """Genera un Word descargable"""
    from docx import Document
    doc = Document()
    doc.add_paragraph(content)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def create_excel(data):
    """Genera un Excel descargable desde DataFrame"""
    buffer = io.BytesIO()
    data.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

# --- Interfaz ---
st.set_page_config(page_title="GenAI-Prove", page_icon="📑", layout="wide")

col1, col2 = st.columns([1,5])
with col1:
    st.image("Logo.png", width=120)
with col2:
    st.title("GenAI-Prove")
    st.subheader("Asistente de contratación hospitalaria (SAS)")
    st.write("Optimiza pliegos, memorias y valoraciones con IA generativa aplicada a contratación sanitaria.")

# Carga de documentos
uploaded_file = st.file_uploader("📂 Sube un PDF (pliego, memoria, oferta)", type=["pdf"])
task = st.selectbox("Selecciona el tipo de tarea", ["Crear pliego", "Analizar documento", "Valorar ofertas", "Justificar contratación"])
user_input = st.text_area("Escribe tu consulta o instrucción", "")

if st.button("Ejecutar"):
    text = ""
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)

    # Crear thread con el asistente
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Tarea: {task}\n\nConsulta: {user_input}\n\nContenido del PDF:\n{text[:6000]}"
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    # Obtener respuesta
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    response = ""
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            response = msg.content[0].text.value
            break

    st.subheader("📌 Respuesta del asistente")
    st.write(response)

    # Descarga en Word
    word_file = create_word(response)
    st.download_button(
        label="⬇️ Descargar en Word",
        data=word_file,
        file_name="GenAIProve_respuesta.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # Descarga en Excel (si es tabla)
    if "criterio" in response.lower() or "puntuación" in response.lower():
        df = pd.DataFrame([{"Respuesta": response}])
        excel_file = create_excel(df)
        st.download_button(
            label="⬇️ Descargar en Excel",
            data=excel_file,
            file_name="GenAIProve_respuesta.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
