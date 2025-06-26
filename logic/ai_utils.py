# logic/ai_utils.py
import streamlit as st
from openai import OpenAI

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
