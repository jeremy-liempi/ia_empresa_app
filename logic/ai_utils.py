import os
import openai
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

def sugerir_metodologia_y_equipo(descripcion, ubicacion, presupuesto, empleados):
    prompt = (
        f"Tengo el siguiente proyecto:\n\n{descripcion}\n\n"
        f"Ubicación: {ubicacion}\nPresupuesto: {presupuesto} CLP\n\n"
        f"Empleados disponibles:\n{empleados}\n\n"
        f"¿Qué metodología recomiendas y qué equipo ideal debería asignar? Justifica brevemente."
    )

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un consultor experto en proyectos."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error al consultar IA: {e}"
