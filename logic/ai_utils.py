# logic/ai_utils.py
import streamlit as st
from openai import OpenAI
import PyPDF2
import io

# Crear cliente OpenAI con API Key desde secretos
oai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else None)

def sugerir_metodologia_y_equipo(descripcion: str, ubicacion: str, presupuesto: int, empleados: list) -> str:
    """
    Recibe datos de un proyecto y devuelve un plan óptimo: metodologías, fases, equipo y ejecución.
    """
    prompt = (
        f"Somos una consultora de proyectos mineros. Lleva a cabo un plan óptimo para este proyecto:\n"
        f"Descripción: {descripcion}\n"
        f"Ubicación: {ubicacion}\n"
        f"Presupuesto: {presupuesto} CLP\n"
        f"Profesionales disponibles: {[e['nombre'] for e in empleados]}\n\n"
        "Resume la metodología, fases, equipo ideal y plan de ejecución de forma clara y profesional."
    )
    try:
        response = oai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto gestor de proyectos mineros."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        # Dependiendo de la versión, el contenido puede estar en .choices o directamente
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al consultar IA: {e}"

def extraer_datos_cv(cv_file) -> dict:
    # 1) Extrae texto del PDF
    reader = PyPDF2.PdfReader(io.BytesIO(cv_file.read()))
    texto = "\n".join(page.extract_text() for page in reader.pages)

    # 2) Envía prompt a la API de OpenAI para extraer campos
    prompt = f"""
    Extrae estos campos de este CV:
    - nombre completo
    - RUT
    - correo institucional
    - cargo
    - área funcional
    - años de experiencia (número)
    - horas disponibles por semana (número)
    - habilidades (lista breve)

    Devuélvelo en formato JSON sin texto adicional. CV:
    ```{texto}```
    """
    resp = openai.ChatCompletion.create(
        model="gpt-4o-turbo",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )
    content = resp.choices[0].message.content.strip()
    # 3) Parsea JSON
    try:
        return json.loads(content)
    except:
        # Si falla, devuélvelo en blanco para corrección manual
        return {
            "nombre": "",
            "rut": "",
            "correo": "",
            "cargo": "",
            "area": "",
            "años_experiencia": 0,
            "horas_por_semana": 0,
            "skills": []
        }
