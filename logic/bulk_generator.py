from supabase import create_client
from datetime import date, timedelta
from .supabase_utils import subir_trabajador
import streamlit as st
import random
import uuid

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

roles = ["Desarrollador", "Diseñador", "Tester", "Scrum Master", "Analista"]
areas = ["TI", "UX", "QA", "PMO", "Data"]
estados = ["Disponible", "En proyecto", "No disponible"]

def generar_empleados_en_proyecto():
    roles = ["Ingeniero", "Diseñador", "Analista", "Líder de proyecto", "Tester"]
    areas = ["TI", "Diseño", "Finanzas", "Operaciones", "RRHH"]
    proyectos = ["Proyecto A", "Proyecto B", "Proyecto C"]

    for i in range(1, 16):
        nombre = f"EmpleadoP{i}"
        rut = f"12.345.{i:03d}-K"
        correo = f"empleadoP{i}@empresa.com"
        cargo = random.choice(roles)
        area = random.choice(areas)
        skills = ["Python", "Excel", "Comunicación"]
        estado = "En proyecto"
        proyecto_actual = random.choice(proyectos)
        inicio_proyecto = date.today() - timedelta(weeks=random.randint(1, 4))
        fin_proyecto = date.today() + timedelta(weeks=random.randint(1, 6))
        horas = random.randint(20, 40)

        datos = {
            "nombre": nombre,
            "rut": rut,
            "correo": correo,
            "cargo": cargo,
            "area": area,
            "años_experiencia": random.randint(1, 10),
            "horas_por_semana": horas,
            "skills": skills,
            "estado": estado,
            "proyecto_actual": proyecto_actual,
            "inicio_proyecto": inicio_proyecto.isoformat(),
            "fin_proyecto": fin_proyecto.isoformat(),
        }

        subir_trabajador(datos, cv_file=None)
