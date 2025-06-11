# main.py

#######################
# 1. Importar librerías
#######################

import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
st.set_page_config(page_title="MyMatch", page_icon="💡", layout="centered")

from sqlalchemy import create_engine

DB_URI = st.secrets["DB_URI"]
engine = create_engine(DB_URI)

import pandas as pd
from datetime import date

# 1.1. Funciones propias
from db.db_connector import get_engine, get_session
from logic.ai_utils import sugerir_metodologia_y_equipo, sugerir_roles_faltantes_por_proyecto
from logic.availability import calcular_semanas_disponibilidad, filtrar_por_semanas

# 1.2. Modelos (solo si usas ORM para la sección de asignación)
from models.proyecto import Proyecto

# 1.3 Logo
from PIL import Image
image = Image.open("assets/logo.png")
st.image(image, width=200)  # Ajusta el tamaño a gusto

# 1.4 Base de datos
from logic.data_utils import cargar_trabajadores

# 1.5 apikey 
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


# Carga la base de datos de trabajadores
empleados = cargar_trabajadores()


###########################
# 2. Configurar la página
###########################



st.title("MyMatch – Arma tu mejor proyecto")
st.markdown("""
Esta aplicación permite:
1. Ver la lista de trabajadores con su información actual.
2. Sugerir plan de ejecución y equipo ideal para un nuevo proyecto con IA.
3. Calcular la disponibilidad de los trabajadores en semanas.
4. Guardar proyecto sugerido por IA.
""")


#############################################
# 3. SECCIÓN 1: Mostrar lista de usuarios
#############################################

st.subheader("1. Trabajadores de la Empresa")


df_trab = cargar_trabajadores()

with st.expander("Ver tabla de trabajadores"):
    st.dataframe(
        df_trab,
        use_container_width=True,
        height=300  # altura fija para scroll interno
    )


################################################
# 4. SECCIÓN 2: Clasificar proyectos con IA
################################################

st.subheader("2. Describe Tu Proyecto y Sugerir Keywords")

# 4.1. Caja de texto para la descripción del proyecto
st.subheader("Completa los siguientes campos para que la IA te sugiera cómo llevar a cabo tu proyecto:")
st.info("Puedes dejar los campos vacíos si aún no tienes toda la información.")

objetivo = st.text_input("¿Cuál es el objetivo principal del proyecto?")
duracion_estim = st.text_input("¿Cuánto tiempo estimas que durará?")
tipo_actividades = st.text_area("¿Qué tipo de actividades se deben realizar? (Ej: desarrollo de software, diseño gráfico, investigación, etc.)")
recursos_disponibles = st.text_area("¿Qué recursos tienes actualmente? (personas, materiales, software, etc.)")
restricciones = st.text_area("¿Existen restricciones o condiciones especiales? (Ej: plazos fijos, trabajo remoto, etc.)")
ubicacion_proyecto = st.text_input("Ubicación del proyecto")
inversion_proyecto = st.text_input("Presupuesto disponible (en CLP)")

# Recolectar todo como una sola descripción estructurada
descripcion_proyecto = f"""
Objetivo: {objetivo}
Duración estimada: {duracion_estim}
Actividades previstas: {tipo_actividades}
Recursos disponibles: {recursos_disponibles}
Restricciones: {restricciones}
Ubicación: {ubicacion_proyecto}
Presupuesto: {inversion_proyecto} CLP
"""


# 4.2. Botón para enviar a la IA
if st.button("Sugerir plan de ejecución y equipo ideal"):
    # 4.2.1 Validar que no esté vacío
    if descripcion_proyecto.strip() == "":
        st.warning("Por favor, ingresa primero la descripción del proyecto.")
    else:
        # 4.2.2 Llamar a la función de IA y mostrar un spinner
        with st.spinner("Consultando a OpenAI..."):
           resultado_ia = sugerir_metodologia_y_equipo(descripcion_proyecto, ubicacion_proyecto, inversion_proyecto, empleados)
        st.success("✅ Resultado de la IA:")
        st.code(resultado_ia, language="text")


###############################################################
# 5. SECCIÓN 3: Calcular disponibilidad y filtrar usuarios
###############################################################

st.subheader("3. Filtrar Trabajadores por Disponibilidad")

# 5.1. Fecha actual (automática)
hoy = date.today()  # Asegúrate de que tu Mac esté en zona 'America/Santiago'

# 5.2. Agregar columnas al DataFrame con la función de lógica

df_con_semanas = calcular_semanas_disponibilidad(df_trab, hoy)

# 5.3. Mostrar la tabla con la columna 'semanas_disponible'
st.write("Trabajadores con semanas de disponibilidad calculadas:")
st.dataframe(
    df_con_semanas,
    use_container_width=True
)

# 5.4. Slider para elegir rango de semanas
semanas_para_empezar = st.slider(
    "¿En cuántas semanas planeas iniciar el proyecto?",
    min_value=0, max_value=12, value=1, step=1
)

# 5.5. Filtrar DataFrame según el slider
df_usuarios_disponibles = filtrar_por_semanas(df_con_semanas, semanas_para_empezar)

st.write(f"Trabajadores disponibles en ≤ {semanas_para_empezar} semana(s):")
st.dataframe(
    df_usuarios_disponibles[["id", "nombre", "rol", "semanas_disponible"]],
    use_container_width=True
)

# 5.6. Sugerencia de la IA basada en el tipo de proyecto (si hay descripción)
if descripcion_proyecto.strip():
    with st.spinner("Consultando a la IA para reforzar el equipo..."):
        from logic.ai_utils import sugerir_roles_faltantes_por_proyecto
        sugerencia_roles = sugerir_roles_faltantes_por_proyecto(
            descripcion_proyecto=descripcion_proyecto,
            empleados=df_usuarios_disponibles
        )
    st.info("📋 Sugerencia de refuerzos para el equipo:")
    st.markdown(sugerencia_roles)
else:
    st.info("ℹ️ Ingresa una descripción del proyecto arriba para recibir sugerencias de refuerzos.")


#######################################################################
# 6. SECCIÓN 4: Obtener equipo recomendado con IA para el proyecto
#######################################################################

st.subheader("4. Guardar Proyecto sugerido por IA")

# — Formulario para crear proyecto —
with st.form("form_nuevo_proyecto", clear_on_submit=True):
    nombre_proyecto = st.text_input("Nombre del proyecto", key="nombre_proy")
    fecha_inicio_proyecto = st.date_input("Fecha de inicio", key="fecha_inicio_proy")
    descripcion_proyecto = st.text_area("Descripción breve (opcional)", height=100)
    # Botón para enviar el formulario
    guardar = st.form_submit_button("Guardar proyecto")

if guardar:
    if not nombre_proyecto or not fecha_inicio_proyecto:
        st.warning("Debe completar nombre y fecha de inicio.")
    else:
        # 1) Guardar en la base de datos
        session = get_session()
        nuevo = Proyecto(
            nombre=nombre_proyecto,
            fecha_inicio=fecha_inicio_proyecto,
            descripcion=descripcion_proyecto,
            metodologia_ia=""  # o lo que quieras guardar
        )
        session.add(nuevo)
        session.commit()
        st.success(f"Proyecto «{nombre_proyecto}» guardado correctamente.")

        # 2) (Opcional) Mostrar la lista actualizada de proyectos
        proyectos = session.query(Proyecto).all()
        df_proy = pd.DataFrame([
            {"id": p.id, "nombre": p.nombre, "fecha_inicio": p.fecha_inicio}
            for p in proyectos
        ])
        st.write("### Proyectos en la base de datos")
        st.dataframe(df_proy, use_container_width=True)
