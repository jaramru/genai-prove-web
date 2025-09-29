import streamlit as st
from openai import OpenAI
import PyPDF2
import os

# Configuración de API Key (desde variable de entorno)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ID de tu asistente en OpenAI (lo copias de la consola Assistants)
ASSISTANT_ID = "asst_xxxxxxxxxxxxx"

# Función para extraer texto de un PDF
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Interfaz de la aplicación
st.set_page_config(page_title="GenAI-Prove", page_icon="📑", layout="wide")
st.title("📑 GenAI-Prove")
st.write("Asistente de contratación hospitalaria del SAS")

# Subida de archivo
uploaded_file = st.file_uploader("Sube un pliego o memoria en PDF", type=["pdf"])
user_input = st.text_area("Escribe tu consulta o instrucción", "")

if st.button("Analizar"):
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
        # Crear un hilo para el asistente
        thread = client.beta.threads.create()
        
        # Enviar mensaje al asistente
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"{user_input}\n\nContenido del PDF:\n{text[:5000]}" # límite por seguridad
        )
        
        # Ejecutar asistente
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        
        # Obtener respuesta
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                st.subheader("📌 Respuesta del asistente")
                st.write(msg.content[0].text.value)
                break
    else:
        st.warning("Por favor, sube un archivo PDF primero.")
