import streamlit as st
import pandas as pd
from supabase import create_client
import uuid
import os

# Leer credenciales desde Streamlit Secrets o entorno
SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

# Cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_trabajadores() -> pd.DataFrame:
    try:
        resp = supabase.table("trabajadores").select("*").execute()
        df = pd.DataFrame(resp.data)

        if df.empty:
            return pd.DataFrame(columns=[
                "id", "nombre", "rut", "cargo", "area", "skills", "correo", "telefono",
                "estado", "horas_por_semana", "años_experiencia",
                "proyecto_actual", "inicio_proyecto", "fin_proyecto",
                "cv_url"
            ])

        if "skills" in df.columns:
            df["skills"] = df["skills"].apply(lambda s: s.strip("{}").split(",") if isinstance(s, str) else [])

        return df

    except Exception as e:
        st.error(f"Error al obtener trabajadores: {e}")
        return pd.DataFrame()

def subir_trabajador(datos: dict, cv_file):
    try:
        if cv_file:
            unique_filename = f"{uuid.uuid4()}.pdf"
            path_on_bucket = f"cvs/{unique_filename}"

            # Leer el archivo como bytes
            file_bytes = cv_file.read()

            # Subir al bucket cvs
            supabase.storage.from_("cvs").upload(
                path_on_bucket,
                file=file_bytes,
                file_options={"content-type": "application/pdf"}
            )

            # Hacerlo público (por si no lo estaba aún)
            supabase.storage.from_("cvs").update(path_on_bucket, {
                "cacheControl": "3600", "upsert": True
            })

            # Obtener URL pública
            public_url = supabase.storage.from_("cvs").get_public_url(path_on_bucket).get("publicURL")
            datos["cv_url"] = public_url

        if isinstance(datos.get("skills"), list):
            datos["skills"] = "{" + ",".join(datos["skills"]) + "}"

        supabase.table("trabajadores").insert(datos).execute()

    except Exception as e:
        st.error(f"Error al subir trabajador: {e}")

def eliminar_trabajador(id_empleado: int):
    try:
        supabase.table("trabajadores").delete().eq("id", id_empleado).execute()
    except Exception as e:
        st.error(f"Error al eliminar trabajador: {e}")

def actualizar_trabajador(id_empleado: int, datos: dict):
    try:
        supabase.table("trabajadores").update(datos).eq("id", id_empleado).execute()
    except Exception as e:
        st.error(f"Error al actualizar trabajador: {e}")

def guardar_proyecto(nombre, descripcion, objetivo, duracion, ubicacion, presupuesto, fecha_inicio, participantes):
    try:
        if isinstance(participantes, list):
            participantes = [p.strip() for p in participantes if p.strip()]

        supabase.table("proyectos").insert({
            "nombre": nombre,
            "descripcion": descripcion,
            "objetivo": objetivo,
            "duracion": f"{duracion_semanas} semanas",
            "ubicacion": ubicacion,
            "presupuesto": presupuesto,
            "fecha_inicio": fecha_inicio.isoformat() if hasattr(fecha_inicio, "isoformat") else fecha_inicio,
            "participantes": participantes
        }).execute()

        # Actualizar trabajadores asignados automáticamente
        for nombre_trabajador in participantes:
            trabajador = supabase.table("trabajadores").select("id").eq("nombre", nombre_trabajador).execute()
            if trabajador.data:
                id_trabajador = trabajador.data[0]["id"]
                supabase.table("trabajadores").update({
                    "estado": "En proyecto",
                    "proyecto_actual": nombre,
                    "inicio_proyecto": fecha_inicio.isoformat() if hasattr(fecha_inicio, "isoformat") else fecha_inicio,
                    "fin_proyecto": None  # Se puede actualizar luego según lógica adicional
                }).eq("id", id_trabajador).execute()

    except Exception as e:
        st.error(f"Error al guardar proyecto: {e}")

def obtener_proyectos():
    try:
        response = supabase.table("proyectos").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error al obtener proyectos: {e}")
        return []

def obtener_proyecto_por_id(id_proyecto):
    try:
        response = supabase.table("proyectos").select("*").eq("id", id_proyecto).single().execute()
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error al obtener proyecto: {e}")
        return None

def actualizar_proyecto(id_proyecto, datos_actualizados):
    try:
        return supabase.table("proyectos").update(datos_actualizados).eq("id", id_proyecto).execute()
    except Exception as e:
        st.error(f"Error al actualizar proyecto: {e}")
        return None

def eliminar_proyecto(proyecto_id):
    try:
        supabase.table("proyectos").delete().eq("id", proyecto_id).execute()
    except Exception as e:
        st.error(f"Error al eliminar proyecto: {e}")
