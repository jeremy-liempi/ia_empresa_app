# main.py

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
from PIL import Image
from dotenv import load_dotenv

# Cargar variables de entorno si es necesario
load_dotenv()

# Importaciones locales
from logic.supabase_utils import obtener_trabajadores, subir_trabajador, eliminar_trabajador
from logic.availability import calcular_semanas_disponibilidad
from logic.ai_utils import sugerir_metodologia_y_equipo

# Configuración de la app
st.set_page_config(page_title="MyMatch", layout="wide", page_icon="assets/logo.png")
st.sidebar.image("assets/logo.png", width=150)
seccion = st.sidebar.radio("Navegación", ["Dashboard", "Gestión de empleados", "Proyectos"])

# Obtener empleados
df_empleados = obtener_trabajadores()

# Calcular disponibilidad
if not df_empleados.empty:
    df_empleados = calcular_semanas_disponibilidad(df_empleados, date.today())

# === DASHBOARD ===
if seccion == "Dashboard":
    st.title("📊 Panel de Control")

    if df_empleados.empty:
        st.warning("No hay empleados cargados aún.")
        st.stop()

    st.subheader("Horas por proyecto")
    if "proyecto_actual" in df_empleados.columns:
        horas = df_empleados.groupby("proyecto_actual")["horas_por_semana"].sum()
        st.bar_chart(horas)

    st.subheader("Profesionales por rol")
    if "cargo" in df_empleados.columns:
        st.bar_chart(df_empleados["cargo"].value_counts())

    st.subheader("Disponibilidad en semanas")
    st.bar_chart(df_empleados["semanas_disponible"])

    st.subheader("Profesionales con menos de 2 por rol")
    faltan = df_empleados["cargo"].value_counts()
    st.write(faltan[faltan < 2])

# === GESTIÓN DE EMPLEADOS ===
elif seccion == "Gestión de empleados":
    st.title("👥 Gestión de Empleados")

    if not df_empleados.empty:
        st.dataframe(df_empleados, use_container_width=True)

    with st.expander("➕ Agregar nuevo empleado"):
        # Parte reactiva fuera del formulario
    
        with st.form("form_agregar"):
            nombre = st.text_input("Nombre completo")
            rut = st.text_input("RUT")
            correo = st.text_input("Correo institucional")
            cargo = st.text_input("Cargo")
            area = st.text_input("Área funcional")
            años = st.number_input("Años de experiencia", min_value=0, max_value=50)
            horas = st.number_input("Horas disponibles por semana", min_value=0, max_value=168)
            skills = st.text_input("Skills (separadas por comas)")
            estado_seleccionado = st.selectbox("Estado", ["Disponible", "En proyecto", "No disponible"], key="estado_outside")
    
        # Si está en proyecto, pedir estos datos también fuera
        proyecto_actual = None
        inicio_proyecto = None
        fin_proyecto = None
            
        if estado_seleccionado == "En proyecto":
            proyecto_actual = st.text_input("Proyecto actual")
            inicio_proyecto = st.date_input("Fecha inicio del proyecto")
            fin_proyecto = st.date_input("Fecha fin del proyecto")
                
            cv = st.file_uploader("Cargar CV (PDF)", type=["pdf"])
    
            submit = st.form_submit_button("Subir Empleado")
    
            if submit:
                datos = {
                    "nombre": nombre,
                    "rut": rut,
                    "correo": correo,
                    "cargo": cargo,
                    "area": area,
                    "años_experiencia": años,
                    "horas_por_semana": horas,
                    "skills": [s.strip() for s in skills.split(",") if s.strip()],
                    "estado": estado_seleccionado,
                    "proyecto_actual": proyecto_actual if estado_seleccionado == "En proyecto" else None,
                    "inicio_proyecto": inicio_proyecto.isoformat() if inicio_proyecto else None,
                    "fin_proyecto": fin_proyecto.isoformat() if fin_proyecto else None,
                }
    
                subir_trabajador(datos, cv if cv else None)
                st.success("Empleado agregado correctamente.")


    with st.expander("🗑️ Eliminar empleado"):
        id_del = st.number_input("ID a eliminar", min_value=1, step=1)
        if st.button("Eliminar"):
            eliminar_trabajador(id_del)
            st.success(f"Empleado con ID {id_del} eliminado.")

# === PROYECTOS ===
elif seccion == "Proyectos":
    st.title("📁 Gestión de Proyectos")

    st.subheader("📌 Crear nuevo proyecto con IA")
    objetivo = st.text_input("Objetivo del proyecto")
    duracion = st.text_input("Duración estimada (ej. 4 semanas)")
    actividades = st.text_area("Actividades a realizar")
    ubicacion = st.text_input("Ubicación")
    presupuesto = st.number_input("Presupuesto disponible", min_value=0)
    fecha_inicio = st.date_input("Fecha de inicio")

    if st.button("Generar proyecto con IA"):
        descripcion = (
            f"Objetivo: {objetivo}\n"
            f"Duración: {duracion}\n"
            f"Actividades: {actividades}\n"
            f"Ubicación: {ubicacion}\n"
            f"Presupuesto: {presupuesto} CLP"
        )
        with st.spinner("Generando sugerencia de proyecto..."):
            sugerencia = sugerir_metodologia_y_equipo(
                descripcion, ubicacion, presupuesto, df_empleados.to_dict(orient="records")
            )
        st.subheader("🔧 Proyecto generado por IA")
        st.markdown(sugerencia)

    st.subheader("📂 Proyectos actuales")
    proyectos = df_empleados["proyecto_actual"].dropna().unique()
    for p in proyectos:
        st.markdown(f"### {p}")
        dfp = df_empleados[df_empleados["proyecto_actual"] == p]
        st.dataframe(dfp[["nombre", "cargo", "horas_por_semana", "semanas_disponible"]], use_container_width=True)
