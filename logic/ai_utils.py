from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def sugerir_metodologia_y_equipo(descripcion, ubicacion, inversion, empleados):
    prompt_usuario = f"""
Descripción del proyecto:
{descripcion}

Ubicación: {ubicacion}
Presupuesto: {inversion}
Cantidad de trabajadores disponibles: {len(empleados)}

Sugiere metodología, equipo ideal y etapas recomendadas para este proyecto.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto en gestión de proyectos que sugiere metodologías y equipos ideales."},
            {"role": "user", "content": prompt_usuario}
        ]
    )

    return response.choices[0].message.content

def sugerir_roles_faltantes_por_proyecto(descripcion_proyecto, empleados):
    prompt_usuario = f"""
Este es un nuevo proyecto con la siguiente descripción:

{descripcion_proyecto}

A continuación, te entrego la lista de empleados actualmente disponibles con sus roles y semanas de disponibilidad:

{empleados[["nombre", "rol", "semanas_disponible"]].to_string(index=False)}

Con base en esto:
1. ¿Qué roles podrían hacer falta para ejecutar este proyecto correctamente?
2. Si es posible, menciona en cuántas semanas se desocupa alguien útil para ese rol.
3. Sé específico y breve.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un experto en formación de equipos para proyectos."},
            {"role": "user", "content": prompt_usuario}
        ]
    )

    return response.choices[0].message.content