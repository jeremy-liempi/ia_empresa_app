# logic/bulk_generator.py

from datetime import date, timedelta
import random
from logic.supabase_utils import subir_trabajador, guardar_proyecto, obtener_trabajadores

# Listas de ejemplo más realistas
nombres = [
    "Ana Gómez", "Carlos Torres", "Lucía Rojas", "Pedro Vidal", "Sofía Herrera",
    "Javier Castro", "Camila Fuentes", "Diego Sánchez", "Valentina Bravo", "Tomás Espinoza",
    "María Pérez", "Fernando Díaz", "Paula Muñoz", "Andrés León", "Isabel Cruz",
    "Mateo Silva", "Natalia Vargas", "Sebastián Reyes", "Zoe Contreras", "Gabriel Soto",
    "Camila Rojas", "Ignacio Molina", "Martina Gutiérrez", "Vicente Paredes", "Renata Aguirre",
    "Diego Herrera", "Fernanda Castillo", "Alejandro Navarro", "Antonia Salas", "Ricardo López"
]
roles = ["Ingeniero Civil", "Analista Financiero", "Administrador de Proyectos",
         "Técnico Mecánico", "Diseñador Gráfico"]
areas = ["Ingeniería", "Finanzas", "Operaciones", "Marketing", "Recursos Humanos"]
estudios_lista = ["Ingeniería Civil", "Ingeniería Comercial", "Técnico en Mecánica",
                  "Diseño Gráfico", "Licenciatura en Economía"]
skills_pool = ["Python", "Excel", "AutoCAD", "Gestión de Proyectos", "SQL", "Power BI"]

def generar_empleados_aleatorios():
    for nombre in nombres:
        datos = {
            "nombre": nombre,
            "rut": f"{random.randint(10_000_000, 25_000_000)}-{random.randint(0,9)}",
            "correo": f"{nombre.lower().replace(' ','.')}@empresa.com",
            "cargo": random.choice(roles),
            "area": random.choice(areas),
            "años_experiencia": random.randint(1, 20),
            "horas_por_semana": random.choice([20, 30, 40]),
            "skills": random.sample(skills_pool, k=3),
            "estado": "Disponible",
            "proyecto_actual": None,
            "inicio_proyecto": None,
            "fin_proyecto": None,
            "estudios": random.choice(estudios_lista)
        }
        subir_trabajador(datos, None)

def generar_proyectos_aleatorios():
    # Nombres y datos de 3 proyectos
    proyectos_info = [
        {
            "nombre": "Optimización Planta Norte",
            "descripcion": "Mejora de procesos y reducción de costos en Planta Norte.",
            "objetivo": "Reducir un 15% los tiempos de producción.",
            "duracion": "12 semanas",
            "ubicacion": "Antofagasta",
            "presupuesto": random.randint(100_000, 300_000),  # USD
            "fecha_inicio": date(2025,7,1).isoformat()
        },
        {
            "nombre": "Digitalización Bodega Central",
            "descripcion": "Implementación de sistema ERP y BI en bodega.",
            "objetivo": "Automatizar inventario y reportes.",
            "duracion": "8 semanas",
            "ubicacion": "Santiago",
            "presupuesto": random.randint(50_000, 120_000),
            "fecha_inicio": date(2025,8,1).isoformat()
        },
        {
            "nombre": "Lanzamiento Nuevo Producto",
            "descripcion": "Campaña de marketing y logística para nuevo producto.",
            "objetivo": "Alcanzar 10.000 unidades vendidas en primer mes.",
            "duracion": "10 semanas",
            "ubicacion": "Concepción",
            "presupuesto": random.randint(80_000, 200_000),
            "fecha_inicio": date(2025,9,1).isoformat()
        }
    ]

    # Obtener lista de empleados actuales
    df = obtener_trabajadores()
    nombres_disp = df[df["estado"]=="Disponible"]["nombre"].tolist()

    for p in proyectos_info:
        # Asignar entre 5 y 10 empleados aleatorios disponibles
        participantes = random.sample(nombres_disp, k=random.randint(5,10))
        guardar_proyecto(
            p["nombre"], p["descripcion"], p["objetivo"],
            p["duracion"], p["ubicacion"], p["presupuesto"],
            p["fecha_inicio"], participantes
        )
