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
from logic.availability import calcular_semanas_disponibilidad, filtrar_por_semanas

# Cargar datos de empleados
empleados_df = obtener_trabajadores()

def recalc_disponibilidad(df):
    df2 = calcular_semanas_disponibilidad(df, date.today())
    df["semanas_disponible"] = df2["semanas_disponible"]
    return df

# === Dashboard ===
if menu == "Dashboard":
    st.header("📊 Panel de Control")
    df = empleados_df.copy()
    df = recalc_disponibilidad(df)

    # 1) Gráfico: horas totales por rol
    horas_rol = df.groupby("rol")["horas_por_semana"].sum()
    fig1, ax1 = plt.subplots()
    ax1.bar(horas_rol.index, horas_rol.values)
    ax1.set_xlabel("Rol")
    ax1.set_ylabel("Horas/Semana Totales")
    st.pyplot(fig1)

    # 2) Horas por proyecto
    if "proyecto_actual" in df.columns:
        horas_proy = df.groupby("proyecto_actual")["horas_por_semana"].sum()
        fig2, ax2 = plt.subplots()
        ax2.barh(horas_proy.index, horas_proy.values)
        ax2.set_xlabel("Horas/Semana")
        ax2.set_ylabel("Proyecto")
        st.subheader("Horas asignadas por proyecto")
        st.pyplot(fig2)

    # 3) Roles con pocos profesionales
    conteo = df["rol"].value_counts()
    faltan = conteo[conteo < 2]
    st.subheader("Roles con pocos profesionales (menos de 2)")
    st.write(faltan)

    # 4) Tabla resumen
    st.subheader("Resumen de Empleados")
    cols = [col for col in ["id","nombre","rol","anios_experiencia","horas_por_semana","proyecto_actual","semanas_disponible"] if col in df.columns]
    st.dataframe(df[cols], use_container_width=True)

# === Gestión de Empleados ===
elif menu == "Gestión Empleados":
    st.header("👥 Gestión de Empleados")
    st.dataframe(empleados_df, use_container_width=True)

    with st.expander("➕ Agregar Nuevo Empleado"):
        with st.form("form_agregar"):
            nombre = st.text_input("Nombre completo")
            correo = st.text_input("Correo institucional")
            rol = st.text_input("Rol/Profesión")
            anios = st.number_input("Años de experiencia", min_value=0, max_value=50)
            horas = st.number_input("Horas disponibles por semana", min_value=0, max_value=168)
            cv = st.file_uploader("Cargar CV (PDF)", type=["pdf"])
            if st.form_submit_button("Subir Empleado"):
                datos = {
                    "nombre": nombre,
                    "correo": correo,
                    "rol": rol,
                    "anios_experiencia": anios,
                    "horas_por_semana": horas,
                    "proyecto_actual": None,
                    "fecha_fin_proyecto": None,
                    "semanas_disponible": None
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
    df = empleados_df.copy()
    df = recalc_disponibilidad(df)

    st.subheader("Filtros")
    roles = st.multiselect("Filtrar por rol", df["rol"].unique())
    anios_min = st.slider("Mínimo años de experiencia", 0, 50, 2)
    dispo_max = st.slider("Máx. semanas disponibles", 0, 12, 4)

    df_filt = df[
        (df["rol"].isin(roles) if roles else True) &
        (df["anios_experiencia"] >= anios_min) &
        (df["semanas_disponible"] <= dispo_max)
    ]
    st.dataframe(df_filt, use_container_width=True)

    st.subheader("Horas totales por rol (filtrado)")
    horas_fil = df_filt.groupby("rol")["horas_por_semana"].sum()
    fig3, ax3 = plt.subplots()
    ax3.bar(horas_fil.index, horas_fil.values)
    st.pyplot(fig3)

    # Profesionales faltantes para proyecto específico
    st.subheader("Profesionales faltantes para proyecto")
    proy = st.text_input("Proyecto de interés para análisis de roles")
    if proy:
        # roles en proyecto
        df_proy = df[df["proyecto_actual"] == proy]
        conteo_proy = df_proy["rol"].value_counts()
        faltan_proy = conteo_proy[conteo_proy < 2]
        st.write(faltan_proy if not faltan_proy.empty else "No faltan profesionales para este proyecto.")

    # Histograma de disponibilidad
    st.subheader("Distribución de disponibilidad (semanas)")
    st.bar_chart(df["semanas_disponible"])
