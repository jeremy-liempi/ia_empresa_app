from datetime import date, timedelta
import random
from logic.supabase_utils import subir_trabajador

def generar_empleados_aleatorios(cantidad, desde=51):
    nombres = [f"Empleado{desde + i}" for i in range(cantidad)]
    roles = ["Analista", "Desarrollador", "Diseñador", "PM", "QA"]
    areas = ["TI", "Marketing", "Finanzas", "Recursos Humanos", "Operaciones"]

    for nombre in nombres:
        datos = {
            "nombre": nombre,
            "rut": f"1{random.randint(1000000, 9999999)}-{random.randint(0,9)}",
            "correo": f"{nombre.lower()}@empresa.com",
            "cargo": random.choice(roles),
            "area": random.choice(areas),
            "años_experiencia": random.randint(1, 15),
            "horas_por_semana": random.choice([20, 30, 40]),
            "skills": ["Python", "Liderazgo", "SQL"],
            "estado": "Disponible",
            "proyecto_actual": None,
            "inicio_proyecto": None,
            "fin_proyecto": None
        }

        subir_trabajador(datos, None)

def guardar_proyectos_desde_trabajadores():
    df = obtener_trabajadores()
    proyectos = df["proyecto_actual"].dropna().unique()
    for p in proyectos:
        participantes = df[df["proyecto_actual"] == p]["nombre"].tolist()
        proyecto = {
            "nombre": p,
            "descripcion": f"Proyecto generado automáticamente para {p}",
            "objetivo": "Objetivo automático",
            "duracion": "Indefinida",
            "ubicacion": "No especificada",
            "presupuesto": 0,
            "fecha_inicio": "2025-01-01",
            "participantes": participantes,
        }
        guardar_proyecto(**proyecto)
