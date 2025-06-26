import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def sugerir_metodologia_y_equipo(descripcion, ubicacion, presupuesto, empleados):
    prompt = f"""Proyecto:
Descripción: {descripcion}
Ubicación: {ubicacion}
Presupuesto: {presupuesto}
Profesionales disponibles: {', '.join([e['nombre'] for e in empleados])}

Con base en esto, sugiere una forma óptima de llevarlo a cabo y un equipo ideal.
"""
    respuesta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return respuesta.choices[0].message.content
