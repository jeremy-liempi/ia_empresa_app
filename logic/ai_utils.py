# logic/ai_utils.py

import openai
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

def sugerir_metodologia_y_equipo(descripcion, ubicacion, presupuesto, empleados):
    prompt = f"""
Eres un experto en gestión de proyectos para empresas consultoras. Tu tarea es ayudar a planificar de forma óptima un nuevo proyecto que ha llegado a la empresa.

Detalles del proyecto:
- Descripción: {descripcion}
- Ubicación: {ubicacion}
- Presupuesto disponible: {presupuesto} CLP

Profesionales disponibles:
{empleados}

Con base en estos datos, responde con una sugerencia clara y profesional que incluya:
1. Una estrategia general para ejecutar el proyecto.
2. Métodos o tecnologías sugeridas si aplica.
3. Recomendación de equipo ideal (nombre, cargo).
4. Justificación del equipo elegido.

Sé conciso, claro y profesional.
"""
    respuesta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return respuesta.choices[0].message["content"]
