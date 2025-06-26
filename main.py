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

    st.subheader("👥 Profesionales por rol")
    if "cargo" in df_empleados.columns:
        conteo_cargos = df_empleados["cargo"].value_counts()
        st.bar_chart(conteo_cargos.rename_axis("Cargo").rename("Cantidad"))

    st.subheader("⏳ Disponibilidad de profesionales (semanas restantes)")
    if "semanas_disponible" in df_empleados.columns:
        st.bar_chart(
            df_empleados.set_index("nombre")["semanas_disponible"].rename("Semanas disponibles")
        )

    st.subheader("🕓 Horas asignadas por proyecto")
    if "proyecto_actual" in df_empleados.columns:
        horas = (
            df_empleados.dropna(subset=["proyecto_actual"])
            .groupby("proyecto_actual")["horas_por_semana"]
            .sum()
            .rename("Horas por semana")
        )
        st.bar_chart(horas)

    st.subheader("📉 Cargos con menos de 2 profesionales")
    faltan = df_empleados["cargo"].value_counts()
    faltantes = faltan[faltan < 2]
    if not faltantes.empty:
        st.write(faltantes.rename("Cantidad"))
    else:
        st.success("No faltan profesionales por rol.")


# === GESTIÓN DE EMPLEADOS ===
elif seccion == "Gestión de empleados":
    st.title("👥 Gestión de Empleados")

    if not df_empleados.empty:
        st.dataframe(df_empleados, use_container_width=True)

        
    with st.expander("➕ Agregar nuevo empleado"):
        # Parte reactiva fuera del formulario
        estado_seleccionado = st.selectbox("Estado del Empleado", ["Disponible", "En proyecto", "No disponible"], key="estado_outside")
    
        # Si está en proyecto, pedir estos datos también fuera
        proyecto_actual = None
        inicio_proyecto = None
        fin_proyecto = None
    
        if estado_seleccionado == "En proyecto":
            proyecto_actual = st.text_input("Proyecto actual")
            inicio_proyecto = st.date_input("Fecha inicio del proyecto")
            fin_proyecto = st.date_input("Fecha fin del proyecto")
    
        with st.form("form_agregar"):
            nombre = st.text_input("Nombre completo")
            rut = st.text_input("RUT")
            correo = st.text_input("Correo institucional")
            cargo = st.text_input("Cargo")
            area = st.text_input("Área funcional")
            años = st.number_input("Años de experiencia", min_value=0, max_value=50)
            horas = st.number_input("Horas disponibles por semana", min_value=0, max_value=168)
            skills = st.text_input("Skills (separadas por comas)")
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


    with st.expander("✏️ Editar Empleado"):
        # Traer datos y seleccionar registro
        df_editar = obtener_trabajadores()
        id_edit = st.selectbox("Selecciona ID a editar", df_editar["id"], key="edit_id")
        emp = df_editar[df_editar["id"] == id_edit].iloc[0]

        estado_seleccionado = st.selectbox("Estado del Empleado", ["Disponible", "En proyecto", "No disponible"], key="estado_nuevo_empleado")

    
        # Si está en proyecto, pedir estos datos también fuera
        proyecto_actual = None
        inicio_proyecto = None
        fin_proyecto = None
    
        if estado_seleccionado == "En proyecto":
            proyecto_actual = st.text_input("Proyecto actual")
            inicio_proyecto = st.date_input("Fecha inicio del proyecto")
            fin_proyecto = st.date_input("Fecha fin del proyecto")
            
        with st.form("form_editar"):
            # Pre-llenar campos con los valores actuales
            nombre = st.text_input("Nombre completo", value=emp["nombre"])
            correo = st.text_input("Correo institucional", value=emp["correo"])
            cargo = st.text_input("Cargo", value=emp["cargo"])
            area = st.text_input("Área funcional", value=emp["area"])
            años = st.number_input("Años de experiencia", min_value=0, max_value=50, value=int(emp["años_experiencia"]))
            horas = st.number_input("Horas disponibles/semana", min_value=0, max_value=168, value=int(emp["horas_por_semana"]))
        
            submit_ed = st.form_submit_button("Guardar cambios")
            
            if submit_ed:
                datos_upd = {
                    "nombre": nombre,
                    "correo": correo,
                    "cargo": cargo,
                    "area": area,
                    "años_experiencia": años,
                    "horas_por_semana": horas,
                    "estado": estado,
                    "proyecto_actual": proyecto_actual if estado=="En proyecto" else None,
                    "inicio_proyecto": inicio_proyecto.isoformat() if inicio_proyecto else None,
                    "fin_proyecto":    fin_proyecto.isoformat()    if fin_proyecto    else None,
                }
                actualizar_trabajador(id_edit, datos_upd)
                st.success("Empleado actualizado correctamente.")

            
        
    with st.expander("🗑️ Eliminar empleado"):
        id_del = st.number_input("ID a eliminar", min_value=1, step=1)
        if st.button("Eliminar"):
            eliminar_trabajador(id_del)
            st.success(f"Empleado con ID {id_del} eliminado.")

# === PROYECTOS ===
elif seccion == "Proyectos":
    st.title("📁 Apoyo para proyectos entrantes")

    semanas_inicio = st.slider("¿En cuántas semanas planeas iniciar el proyecto?", 0, 52, 0)
    disponibles = df_empleados[
        (df_empleados["estado"] == "Disponible") |
        (df_empleados["semanas_disponible"] <= semanas_inicio)
    ]
    st.subheader("👥 Trabajadores disponibles en ese plazo")
    st.dataframe(disponibles, use_container_width=True)

    st.subheader("🧠 Sugerencia inteligente para ejecutar el proyecto")
    descripcion = st.text_area("Describe el proyecto, objetivos, desafíos o requerimientos")
    presupuesto = st.number_input("Presupuesto estimado (CLP)", 0)
    ubicacion = st.text_input("Ubicación")
    if st.button("Sugerir solución óptima"):
        with st.spinner("Consultando IA..."):
            sugerencia = sugerir_metodologia_y_equipo(
                descripcion, ubicacion, presupuesto,
                disponibles.to_dict(orient=\"records\")
            )
        st.markdown(sugerencia)

    st.subheader("📥 Agregar proyecto (solo visual)")
    with st.form(\"form_agregar_proyecto\"):
        nombre = st.text_input(\"Nombre del proyecto\")        
        objetivo = st.text_input(\"Objetivo general\")        
        if st.form_submit_button(\"Agregar proyecto\"):
            st.success(f\"Proyecto '{nombre}' agregado correctamente (sólo visual)\")
    
    st.subheader(\"✏️ Editar proyecto (simulado)\")
    st.info(\"Funcionalidad futura: permite editar proyectos guardados\")

    st.subheader(\"🗑️ Eliminar proyecto (simulado)\")
    st.info(\"Funcionalidad futura: permite eliminar proyectos guardados\")

    st.subheader(\"📂 Proyectos actuales en curso\")
    proyectos = df_empleados[\"proyecto_actual\"].dropna().unique()
    for p in proyectos:
        st.markdown(f\"### {p}\")
        dfp = df_empleados[df_empleados[\"proyecto_actual\"] == p]
        st.dataframe(dfp[[\"nombre\", \"cargo\", \"horas_por_semana\", \"semanas_disponible\"]], use_container_width=True)
