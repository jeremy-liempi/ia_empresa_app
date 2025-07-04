# logic/ai_utils.py
import streamlit as st
from openai import OpenAI
import io
import json
from PyPDF2 import PdfReader

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
        f"Presupuesto: {presupuesto} USD\n"
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
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al consultar IA: {e}"


def extraer_datos_cv(cv_file) -> dict:
    """
    Extrae texto de un PDF y pide a la IA que devuelva
    nombre, RUT, correo, cargo, área, años de experiencia,
    horas disponibles, skills y estudios en JSON.
    """
    # 1) Leer todo el texto del PDF
    cv_bytes = cv_file.read()
    reader = PdfReader(io.BytesIO(cv_bytes))
    texto = "\n".join([
        page.extract_text() or ""
        for page in reader.pages
    ])

    # 2) Crear prompt para OpenAI con el campo "estudios" añadido
    prompt = (
        "Analiza el siguiente currículum vitae y extrae los datos del trabajador en formato JSON. "
        "Asegúrate de inferir los valores aunque no estén explícitos. Si algo no se menciona, usa valores razonables.\n\n"
        "Formato esperado:\n"
        "{\n"
        '  "nombre": "Nombre completo",\n'
        '  "rut": "RUT",\n'
        '  "correo": "Correo electrónico",\n'
        '  "cargo": "Título o cargo principal",\n'
        '  "area": "Área funcional (ej. Ingeniería, Administración, etc.)",\n'
        '  "años_experiencia": número,\n'
        '  "horas_por_semana": número (si no se menciona, usar 40),\n'
        '  "skills": ["Lista", "de", "habilidades"],\n'
        '  "estudios": ["Lista", "de", "estudios", "o", "títulos"]\n'
        "}\n\n"
        f"Texto del CV:\n```{texto[:4000]}```"
    )
    
    try:
        resp = oai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente que convierte CVs a datos estructurados."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0
        )
        content = resp.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        st.error(f"IA no pudo extraer datos: {e}")
        return {
            "nombre": "",
            "rut": "",
            "correo": "",
            "cargo": "",
            "area": "",
            "años_experiencia": 0,
            "horas_por_semana": 0,
            "skills": [],
            "estudios": []
        }
