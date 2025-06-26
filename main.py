    # main.py

import os
import sys
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from datetime import date
from datetime import timedelta
import matplotlib.pyplot as plt
from PIL import Image
from dotenv import load_dotenv

# Cargar variables de entorno si es necesario
load_dotenv()

# Importaciones locales
# main.py, arriba de todo

from logic.supabase_utils import (
    obtener_trabajadores,
    subir_trabajador,
    eliminar_trabajador,
    actualizar_trabajador,
    guardar_proyecto,
    obtener_proyectos,
    eliminar_proyecto,
    obtener_proyecto_por_id,      
    actualizar_proyecto        
)

from logic.availability import calcular_semanas_disponibilidad
from logic.ai_utils import sugerir_metodologia_y_equipo

# Configuración de la app
st.set_page_config(page_title="MyMatch", layout="wide", page_icon="assets/logo.png")
st.sidebar.image("assets/logo.png", width=150)
seccion = st.sidebar.selectbox("Navegación", ["Dashboard", "Gestión de empleados", "Proyectos"])

# Obtener empleados
df_empleados = obtener_trabajadores()

# Calcular disponibilidad
if not df_empleados.empty:
    df_empleados = calcular_semanas_disponibilidad(df_empleados, date.today())

# === CLAVE DE ACCESO ===

# Solicitar clave de acceso
PASSWORD = st.secrets["APP_PASSWORD"]

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.image("assets/logo.png", width=200)
    st.title("Bienvenido a MyMatch")

    st.markdown("""
    Esta app permite organizar, visualizar y gestionar los recursos humanos de tu empresa de forma inteligente.
    Carga currículums, analiza disponibilidad, sugiere equipos y mucho más.
    """)

    clave = st.text_input("🔐 Ingrese la clave de acceso:", type="password")
    if st.button("Ingresar"):
        if clave == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Clave incorrecta.")
    st.stop()

# === DASHBOARD ===

if seccion == "Dashboard":
    
    if seccion == "Dashboard":
        submenu_dash = st.sidebar.radio("Submenú Dashboard", ["Profesionales por rol", "Horas por proyecto", "Disponibilidad y faltantes"])

    st.title(f"📊 {submenu_dash}")

    if df_empleados.empty:
        st.warning("No hay empleados cargados aún.")
        st.stop()

    if submenu_dash == "Profesionales por rol":
        st.subheader("👥 Profesionales por rol")
        if "cargo" in df_empleados.columns:
            conteo_cargos = df_empleados["cargo"].value_counts()
            st.bar_chart(conteo_cargos.rename_axis("Cargo").rename("Cantidad"))

    elif submenu_dash == "Horas por proyecto":
        st.subheader("🕓 Horas asignadas por proyecto")
        if "proyecto_actual" in df_empleados.columns:
            horas = (
                df_empleados.dropna(subset=["proyecto_actual"])
                .groupby("proyecto_actual")["horas_por_semana"]
                .sum()
                .rename("Horas por semana")
            )
            st.bar_chart(horas)

    elif submenu_dash == "Disponibilidad y faltantes":
        st.subheader("⏳ Disponibilidad de profesionales (semanas restantes)")
        if "semanas_disponible" in df_empleados.columns:
            st.bar_chart(
                df_empleados.set_index("nombre")["semanas_disponible"].rename("Semanas disponibles")
            )

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
        st.dataframe(df_empleados, use_container_width=True, height=270)
    
    with st.expander("➕ Agregar nuevo empleado"):
        # Parte reactiva fuera del formulario
        estado_seleccionado = st.selectbox("Estado del Empleado", ["Disponible", "En proyecto", "No disponible"], key="estado_outside")
    
        # Si está en proyecto, pedir estos datos también fuera
        proyecto_actual = None
        inicio_proyecto = None
        fin_proyecto = None
    
        if estado_seleccionado == "En proyecto":
            proyectos = obtener_proyectos()
            nombres_proyectos = [p["nombre"] for p in proyectos]
            proyecto_actual = st.selectbox("Proyecto actual", nombres_proyectos)
            
            # Obtener fechas del proyecto seleccionado
            proyecto_info = next((p for p in proyectos if p["nombre"] == proyecto_actual), None)
            if proyecto_info:
                inicio_proyecto = proyecto_info.get("fecha_inicio")
                fin_proyecto = proyecto_info.get("fecha_fin")
            else:
                inicio_proyecto = None
                fin_proyecto = None

    
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


    with st.expander("✏️ Editar informacion de Empleado"):
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
            proyectos = obtener_proyectos()
            nombres_proyectos = [p["nombre"] for p in proyectos]
            proyecto_actual = st.selectbox("Proyecto actual", nombres_proyectos)
            
            # Obtener fechas del proyecto seleccionado
            proyecto_info = next((p for p in proyectos if p["nombre"] == proyecto_actual), None)
            if proyecto_info:
                inicio_proyecto = proyecto_info.get("fecha_inicio")
                fin_proyecto = proyecto_info.get("fecha_fin")
            else:
                inicio_proyecto = None
                fin_proyecto = None

            
        with st.form("form_editar"):
            # Pre-llenar campos con los valores actuales
            nombre = st.text_input("Nombre completo", value=emp["nombre"])
            correo = st.text_input("Correo institucional", value=emp["correo"])
            cargo = st.text_input("Cargo", value=emp["cargo"])
            area = st.text_input("Área funcional", value=emp["area"])
            años = st.number_input("Años de experiencia", min_value=0, max_value=50, value=int(emp["años_experiencia"]))
            horas = st.number_input("Horas disponibles/semana", min_value=0, max_value=168, value=int(emp["horas_por_semana"]))
            cv_label = "Actualizar CV (reemplaza el anterior)" if emp.get("cv_url") else "Subir CV"
            cv_nuevo = st.file_uploader(cv_label, type=["pdf"])
            
            submit_ed = st.form_submit_button("Guardar cambios")
            
            if submit_ed:
                datos_upd = {
                    "nombre": nombre,
                    "correo": correo,
                    "cargo": cargo,
                    "area": area,
                    "años_experiencia": años,
                    "horas_por_semana": horas,
                    "estado": estado_seleccionado,
                    "proyecto_actual": proyecto_actual if estado_seleccionado == "En proyecto" else None,
                    "inicio_proyecto": inicio_proyecto.isoformat() if inicio_proyecto else None,
                    "fin_proyecto": fin_proyecto.isoformat() if fin_proyecto else None,
                }
            
                # Si subió un nuevo CV, reemplazar el anterior
                if cv_nuevo:
                    # Reutilizamos la lógica de subida de nuevo CV
                    unique_filename = f"{uuid.uuid4()}.pdf"
                    path_on_bucket = f"cvs/{unique_filename}"
            
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(cv_nuevo.read())
                        tmp_path = tmp.name
            
                    supabase.storage.from_("cvs").upload(path_on_bucket, tmp_path)
                    public_url = supabase.storage.from_("cvs").get_public_url(path_on_bucket)
                    os.remove(tmp_path)
            
                    datos_upd["cv_url"] = public_url
            
                actualizar_trabajador(id_edit, datos_upd)
                st.success("Empleado actualizado correctamente.")


            
        
    with st.expander("🗑️ Eliminar empleado"):
        id_del = st.number_input("ID a eliminar", min_value=1, step=1)
        if st.button("Eliminar"):
            eliminar_trabajador(id_del)
            st.success(f"Empleado con ID {id_del} eliminado.")

    with st.expander("📥 Descargar CV de un Empleado"):
        empleados_df = obtener_trabajadores()
        id_descarga = st.number_input("🔎 Ingresa el ID del empleado", min_value=1, step=1)
    
        if st.button("Descargar CV"):
            empleado = empleados_df[empleados_df["id"] == id_descarga]
            if not empleado.empty and "cv_url" in empleado.columns:
                cv_url = empleado.iloc[0]["cv_url"]
                try:
                    import requests
                    response = requests.get(cv_url)
                    if response.status_code == 200:
                        st.download_button(
                            label="📄 Descargar CV",
                            data=response.content,
                            file_name=f"cv_{empleado.iloc[0]['nombre'].replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("⚠️ No se pudo descargar el archivo. Verifica que la URL sea pública.")
                except Exception as e:
                    st.error(f"❌ Error al descargar el archivo: {e}")
            else:
                st.warning("⚠️ No se encontró un empleado con ese ID o no tiene CV.")


# === PROYECTOS ===
elif seccion == "Proyectos":
    sub_proy = st.sidebar.radio("Submenú Proyectos", [
        "Apoyo para Proyectos Entrantes",
        "Agregar nuevo proyecto",
        "Editar proyecto",
        "Eliminar proyecto",
        "Proyectos actuales asignados"
    ])

    # === SELECCIÓN DE SEMANAS ===
    if sub_proy == "Apoyo para Proyectos Entrantes":
        st.header("🤝Apoyo para Proyectos Entrantes")
        semanas_inicio = st.slider("¿En cuántas semanas se planea iniciar el proyecto?", 0, 52, 0)

        # === TRABAJADORES DISPONIBLES ===
        disponibles = df_empleados[
            (df_empleados["estado"] == "Disponible") |
            (df_empleados["semanas_disponible"] <= semanas_inicio)
        ]
        st.subheader("👥 Profesionales disponibles en ese plazo")
        st.dataframe(disponibles, use_container_width=True, height=270)

        # === SUGERENCIA IA ===
        st.subheader("🧠 Ayuda inteligente para llevar a cabo el proyecto")
        descripcion = st.text_area("Describe el proyecto, objetivos, desafíos, requisitos, etc.")
        presupuesto = st.number_input("Presupuesto estimado (CLP)", 0)
        ubicacion = st.text_input("Ubicación (ciudad o región)")

        if st.button("Sugerir solución óptima"):
            if descripcion.strip() == "":
                st.warning("Por favor escribe una descripción del proyecto.")
            else:
                with st.spinner("Consultando inteligencia artificial..."):
                    sugerencia = sugerir_metodologia_y_equipo(
                        descripcion=descripcion,
                        ubicacion=ubicacion,
                        presupuesto=presupuesto,
                        empleados=disponibles.to_dict(orient="records")
                    )
                st.markdown(sugerencia)


    if sub_proy == "Agregar nuevo proyecto":
        st.header("➕Agregar nuevo proyecto")
        with st.form("form_agregar_proyecto"):
            nombre = st.text_input("Nombre del proyecto")
            descripcion = st.text_area("Descripción detallada")
            objetivo = st.text_input("Objetivo")
            ubicacion = st.text_input("Ubicación")
            presupuesto = st.number_input("Presupuesto", 0)
            fecha_inicio = st.date_input("Fecha de inicio")
            duracion_semanas = st.number_input("Duración estimada (semanas)", min_value=1, max_value=104, value=4)
            fecha_fin = fecha_inicio + timedelta(weeks=duracion_semanas)
            participantes = st.multiselect(
                "Selecciona trabajadores para este proyecto",
                options=df_empleados[df_empleados["estado"] == "Disponible"]["nombre"].tolist()
            )
           
            if st.form_submit_button("Agregar proyecto"):
                response = guardar_proyecto(
                    nombre, descripcion, objetivo, f"{duracion_semanas} semanas",
                    ubicacion, presupuesto, fecha_inicio,
                    fecha_fin, participantes
                )
                if response.status_code == 201:
                    st.success(f"Proyecto '{nombre}' agregado correctamente con {len(participantes)} personas asignadas.")
                else:
                    st.error("Error al guardar el proyecto.")


    # === EDITAR PROYECTO ===
    if sub_proy == "Editar proyecto":
        st.header("✏️Editar proyecto")
        proyectos = obtener_proyectos()  # Asegúrate que esta función devuelve lista de dicts con al menos 'id' y 'nombre'
        opciones = {p["nombre"]: p["id"] for p in proyectos}

        proyectos = obtener_proyectos()
        if not proyectos:
            st.info("No hay proyectos para editar.")
        else:
            opciones = {p["nombre"]: p["id"] for p in proyectos}
            nombre_sel = st.selectbox("Selecciona proyecto a editar", list(opciones.keys()))
            proyecto_id = opciones[nombre_sel]
            proyecto_data = obtener_proyecto_por_id(proyecto_id)
            duracion_inicial = (
                (pd.to_datetime(proyecto_data["fecha_fin"]) - pd.to_datetime(proyecto_data["fecha_inicio"])).days // 7
            )  
            with st.form("form_editar_proyecto"):
                nombre = st.text_input("Nombre del proyecto", value=proyecto_data["nombre"])
                descripcion = st.text_area("Descripción detallada", value=proyecto_data["descripcion"])
                objetivo = st.text_input("Objetivo", value=proyecto_data["objetivo"])
                ubicacion = st.text_input("Ubicación", value=proyecto_data["ubicacion"])
                presupuesto = st.number_input("Presupuesto", min_value=0, value=int(proyecto_data["presupuesto"]))
                fecha_inicio = st.date_input("Fecha de inicio", value=pd.to_datetime(proyecto_data["fecha_inicio"]))
                duracion_semanas = st.number_input("Duración estimada (semanas)", min_value=1, value=duracion_inicial)
                fecha_fin = fecha_inicio + timedelta(weeks=duracion_semanas)
        
                participantes = st.multiselect(
                    "Selecciona trabajadores asignados",
                    options=df_empleados["nombre"].tolist(),
                    default=proyecto_data.get("participantes", [])
                )
        
                submit_editar = st.form_submit_button("Guardar cambios")
        
                if submit_editar:
                    datos_actualizados = {
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "objetivo": objetivo,
                        "duracion": f"{duracion_semanas} semanas",
                        "ubicacion": ubicacion,
                        "presupuesto": presupuesto,
                        "fecha_inicio": fecha_inicio.isoformat(),
                        "fecha_fin": fecha_fin.isoformat(),
                        "participantes": participantes,
                    }
        
                    actualizar_proyecto(proyecto_id, datos_actualizados)
        
                    # 👉 ACTUALIZAR trabajadores vinculados
                    for trabajador in df_empleados.itertuples():
                        if trabajador.nombre in participantes:
                            actualizar_trabajador(trabajador.id, {
                                "proyecto_actual": nombre,
                                "inicio_proyecto": fecha_inicio.isoformat(),
                                "fin_proyecto": fecha_fin.isoformat(),
                                "estado": "En proyecto"
                            })
                        elif trabajador.proyecto_actual == nombre and trabajador.nombre not in participantes:
                            actualizar_trabajador(trabajador.id, {
                                "proyecto_actual": None,
                                "inicio_proyecto": None,
                                "fin_proyecto": None,
                                "estado": "Disponible"
                            })
        
                    st.success("Proyecto y asignaciones de trabajadores actualizados correctamente.")



    # === ELIMINAR PROYECTO ===
    if sub_proy == "Eliminar proyecto":
        st.header("🗑️Eliminar proyecto")
        proyectos = obtener_proyectos()
        opciones = {p["nombre"]: p["id"] for p in proyectos}
        sel = st.selectbox("Proyecto a eliminar", list(opciones.keys()))
        if st.button("Eliminar proyecto"):
            eliminar_proyecto(opciones[sel])
            st.success("Proyecto eliminado.")


    # === PROYECTOS ACTUALES ===
    if sub_proy == "Proyectos actuales asignados":
        st.header("📁Proyectos actuales asignados")
        proyectos = obtener_proyectos()
        for p in proyectos:
            st.markdown(f"### {p['nombre']}")
            st.write(f"**Descripción:** {p.get('descripcion', '')}")
            st.write(f"**Objetivo:** {p.get('objetivo', '')}")
            st.write(f"**Ubicación:** {p.get('ubicacion', '')}")
            st.write(f"**Presupuesto:** {p.get('presupuesto', '')}")
            st.write(f"**Fecha de inicio:** {p.get('fecha_inicio', '')}")
            st.write(f"**Duración:** {p.get('duracion', '')}")
            st.write(f"**Participantes:** {', '.join(p.get('participantes', []))}")

