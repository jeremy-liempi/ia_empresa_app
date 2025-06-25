# main.py

import os
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(page_title="MyMatch", page_icon="assets/logo.png", layout="wide")

# Sidebar: logo y navegación
st.sidebar.image("assets/logo.png", width=150)
st.sidebar.title("MyMatch")
menu = st.sidebar.radio("Navegación", [
    "Dashboard",
    "Gestión Empleados",
    "Nuevo Proyecto",
    "Análisis IA"
])

# Importar utilidades
from logic.supabase_utils import obtener_trabajadores, subir_trabajador, eliminar_trabajador
from logic.ai_utils import sugerir_metodologia_y_equipo

# Cargar datos de empleados
empleados_df = obtener_trabajadores()

# === Dashboard ===
if menu == "Dashboard":
    st.header("📊 Panel de Control")

    if empleados_df.empty:
        st.info("No hay empleados registrados.")
    else:
        # 1) Tabla resumen
        st.subheader("Resumen de Empleados")
        st.dataframe(empleados_df, use_container_width=True)

        # 2) Gráfico: horas totales por cargo
        if "cargo" in empleados_df.columns and "horas_por_semana" in empleados_df.columns:
            horas_cargo = empleados_df.groupby("cargo")["horas_por_semana"].sum()
            fig1, ax1 = plt.subplots()
            ax1.bar(horas_cargo.index, horas_cargo.values)
            ax1.set_xlabel("Cargo")
            ax1.set_ylabel("Horas/Semana Totales")
            st.pyplot(fig1)
        else:
            st.warning("No hay datos suficientes para mostrar horas por cargo.")

        # 3) Gráfico: horas por proyecto
        if "proyecto_actual" in empleados_df.columns and "horas_por_semana" in empleados_df.columns:
            horas_proy = empleados_df.groupby("proyecto_actual")["horas_por_semana"].sum()
            fig2, ax2 = plt.subplots()
            ax2.barh(horas_proy.index, horas_proy.values)
            ax2.set_xlabel("Horas/Semana")
            ax2.set_ylabel("Proyecto")
            st.subheader("Horas asignadas por proyecto")
            st.pyplot(fig2)
        else:
            st.info("No hay información de proyectos para graficar.")

# === Gestión de Empleados ===
elif menu == "Gestión Empleados":
    st.header("👥 Gestión de Empleados")
    st.dataframe(empleados_df, use_container_width=True)

    with st.expander("➕ Agregar Nuevo Empleado"):
        with st.form("form_agregar"):
            nombre = st.text_input("Nombre completo")
            rut = st.text_input("RUT")
            correo = st.text_input("Correo institucional")
            cargo = st.text_input("Cargo")
            area = st.text_input("Área funcional")
            años = st.number_input("Años de experiencia", min_value=0, max_value=50)
            horas = st.number_input("Horas disponibles por semana", min_value=0, max_value=168)
            skills = st.text_input("Skills (separadas por comas)")
            estado = st.selectbox("Estado", ["Activo","En proyecto","Disponible","Licencia"])
            cv = st.file_uploader("Cargar CV (PDF)", type=["pdf"])
            if st.form_submit_button("Subir Empleado"):
                datos = {
                    "nombre": nombre,
                    "rut": rut,
                    "correo": correo,
                    "cargo": cargo,
                    "area": area,
                    "años_experiencia": años,
                    "horas_por_semana": horas,
                    "skills": [s.strip() for s in skills.split(",") if s.strip()],
                    "estado": estado,
                    "proyecto_actual": None,
                    "inicio_proyecto": None,
                    "fin_proyecto": None,
                }
                if cv:
                    subir_trabajador(datos, cv.read(), cv.name)
                st.success("Empleado agregado correctamente.")

    with st.expander("🗑️ Eliminar Empleado"):
        id_elim = st.number_input("ID del empleado a eliminar", min_value=1)
        if st.button("Eliminar Empleado"):
            eliminar_trabajador(id_elim)
            st.success(f"Empleado con ID={id_elim} eliminado.")

# === Nuevo Proyecto ===
elif menu == "Nuevo Proyecto":
    st.header("🆕 Nuevo Proyecto")
    objetivo = st.text_input("Objetivo principal del proyecto")
    duracion = st.text_input("Duración estimada (ej. 6 semanas)")
    actividades = st.text_area("Actividades a realizar (ej. desarrollo web, testing)")
    ubicacion = st.text_input("Ubicación del proyecto")
    presupuesto = st.number_input("Presupuesto disponible (CLP)", min_value=0)
    fecha_inicio = st.date_input("Fecha de inicio proyectada")

    if st.button("Generar plan y equipo ideal"):
        descripcion = (
            f"Objetivo: {objetivo}\n"
            f"Duración: {duracion}\n"
            f"Actividades: {actividades}\n"
            f"Ubicación: {ubicacion}\n"
            f"Presupuesto: {presupuesto} CLP\n"
        )
        with st.spinner("Generando sugerencias con IA..."):
            sugerencia = sugerir_metodologia_y_equipo(
                descripcion, ubicacion, presupuesto,
                empleados_df.to_dict(orient="records")
            )
        st.subheader("Plan y equipo sugerido por IA")
        st.markdown(sugerencia)

# === Análisis IA y Filtros ===
else:
    st.header("🤖 Insights y Filtros Avanzados")
    st.write("Esta sección la puedes volver a habilitar cuando tengas lista tu lógica de filtrado avanzado.")
