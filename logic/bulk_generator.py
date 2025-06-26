from supabase import create_client
import streamlit as st
import random
import uuid

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

roles = ["Desarrollador", "Diseñador", "Tester", "Scrum Master", "Analista"]
areas = ["TI", "UX", "QA", "PMO", "Data"]
estados = ["Disponible", "En proyecto", "No disponible"]

def generar_empleados_genericos(n=15):
    for i in range(1, n + 1):
        nombre = f"Empleado{i}"
        datos = {
            "nombre": nombre,
            "rut": f"12345678-{i}",
            "correo": f"{nombre.lower()}@empresa.cl",
            "cargo": random.choice(roles),
            "area": random.choice(areas),
            "skills": "{Python,Trabajo en equipo}",
            "estado": random.choice(estados),
            "proyecto_actual": None,
            "inicio_proyecto": None,
            "fin_proyecto": None,
            "años_experiencia": random.randint(1, 10),
            "horas_por_semana": random.choice([20, 30, 40]),
            "cv_url": "",
        }
        supabase.table("trabajadores").insert(datos).execute()
