import streamlit as st
import pandas as pd
from datetime import date
from logic.supabase_utils import obtener_trabajadores, subir_trabajador, eliminar_trabajador
from logic.availability import calcular_semanas_disponibilidad
from logic.ai_utils import sugerir_metodologia_y_equipo

st.set_page_config(page_title="MyMatch", page_icon="assets/logo.png", layout="wide")
st.sidebar.image("assets/logo.png", width=150)
st.sidebar.title("MyMatch")
menu = st.sidebar.radio("Navegación", ["Dashboard", "Gestión Empleados", "Nuevo Proyecto"])

empleados_df = obtener_trabajadores()
if not empleados_df.empty:
    empleados_df = calcular_semanas_disponibilidad(empleados_df, date.today())

# === DASHBOARD ===
if menu == "Dashboard":
    st.header("📊 Panel de Control")

    if empleados_df.empty:
        st.warning("No hay empleados registrados.")
    else:
        st.subheader("Resumen de Empleados")
        st.dataframe(empleados_df, use_container_width=True)

        st.subheader("🔧 Horas asignadas por Proyecto")
        if "proyecto_actual" in empleados_df.columns:
            horas_por_proyecto = empleados_df.groupby("proyecto_actual")["horas_por_semana"].sum()
            st.bar_chart(horas_por_proyecto)

        st.subheader("📌 Profesionales Faltantes por Proyecto")
        proy = st.text_input("Nombre del proyecto para verificar faltantes")
        if proy:
            df_proy = empleados_df[empleados_df["proyecto_actual"] == proy]
            conteo = df_proy["cargo"].value_counts()
            faltan = conteo[conteo < 2]
            st.write(faltan if not faltan.empty else "✅ No faltan profesionales en este proyecto.")

        st.subheader("📉 Disponibilidad (semanas hasta desocupación)")
        st.bar_chart(empleados_df["semanas_disponible"])

        st.subheader("🔍 Filtro por rol, experiencia y disponibilidad")
        roles = st.multiselect("Cargo", empleados_df["cargo"].unique())
        min_exp = st.slider("Años de experiencia mínimos", 0, 30, 2)
        max_disp = st.slider("Máx semanas disponibles", 0, 12, 4)

        df_filtrado = empleados_df[
            ((empleados_df["cargo"].isin(roles)) if roles else True) &
            (empleados_df["años_experiencia"] >= min_exp) &
            (empleados_df["semanas_disponible"] <= max_disp)
        ]
        st.dataframe(df_filtrado, use_container_width=True)

# === GESTIÓN DE EMPLEADOS ===
elif menu == "Gestión Empleados":
    st.header("👥 Gestión de Empleados")
    st.dataframe(empleados_df, use_container_width=True)

    with st.expander("➕ Agregar Empleado"):
        with st.form("form_empleado"):
            nombre = st.text_input("Nombre")
            rut = st.text_input("RUT")
            correo = st.text_input("Correo")
            cargo = st.text_input("Cargo")
            area = st.text_input("Área")
            skills = st.text_input("Skills (separadas por coma)")
            proyecto_actual = st.text_input("Proyecto actual", value="")
            inicio_proyecto = st.date_input("Inicio proyecto", value=None)
            fin_proyecto = st.date_input("Fin proyecto", value=None)
            telefono = st.text_input("Teléfono")
            disponibilidad = st.text_input("Disponibilidad")
            años_experiencia = st.number_input("Años de experiencia", 0, 50)
            horas = st.number_input("Horas por semana", 0, 168, 40)
            estado = st.selectbox("Estado", ["Activo", "En proyecto", "Disponible", "Licencia"])
            cv_file = st.file_uploader("CV (PDF)", type=["pdf"])

            if st.form_submit_button("Agregar"):
                datos = {
                    "nombre": nombre, "rut": rut, "correo": correo, "cargo": cargo, "area": area,
                    "skills": [s.strip() for s in skills.split(",")], "proyecto_actual": proyecto_actual,
                    "inicio_proyecto": str(inicio_proyecto), "fin_proyecto": str(fin_proyecto),
                    "telefono": telefono, "disponibilidad": disponibilidad,
                    "años_experiencia": años_experiencia, "horas_por_semana": horas, "estado": estado
                }
                subir_trabajador(datos, cv_file)
                st.success("Empleado agregado.")

    with st.expander("🗑️ Eliminar Empleado"):
        id_borrar = st.number_input("ID del empleado a eliminar", min_value=1)
        if st.button("Eliminar"):
            eliminar_trabajador(id_borrar)
            st.success("Empleado eliminado.")

# === NUEVO PROYECTO CON IA ===
else:
    st.header("🧠 Generar Proyecto con IA")
    st.write("Describe un proyecto y deja que la IA sugiera una metodología y equipo ideal.")

    objetivo = st.text_input("Objetivo del proyecto")
    duracion = st.text_input("Duración estimada (ej: 6 semanas)")
    actividades = st.text_area("Actividades clave")
    ubicacion = st.text_input("Ubicación")
    presupuesto = st.number_input("Presupuesto (CLP)", 0)

    if st.button("Generar plan y equipo ideal"):
        descripcion = (
            f"Objetivo: {objetivo}\n"
            f"Duración: {duracion}\n"
            f"Actividades: {actividades}\n"
            f"Ubicación: {ubicacion}\n"
            f"Presupuesto: {presupuesto} CLP\n"
        )
        with st.spinner("Consultando IA..."):
            resultado = sugerir_metodologia_y_equipo(descripcion, ubicacion, presupuesto, empleados_df.to_dict("records"))
        st.subheader("🧠 Sugerencia generada")
        st.markdown(resultado)
