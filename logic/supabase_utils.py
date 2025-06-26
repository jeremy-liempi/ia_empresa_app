import streamlit as st
import pandas as pd
from supabase import create_client
import uuid

# Leer credenciales desde Streamlit Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_trabajadores() -> pd.DataFrame:
    """
    Recupera todos los trabajadores desde Supabase como DataFrame
    """
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

        # Convertir skills de texto a lista si vienen en formato "{a,b,c}"
        if "skills" in df.columns:
            df["skills"] = df["skills"].apply(lambda s: s.strip("{}").split(",") if isinstance(s, str) else [])

        return df

    except Exception as e:
        st.error(f"Error al obtener trabajadores: {e}")
        return pd.DataFrame()

def subir_trabajador(datos: dict, cv_file):
    """
    Sube un nuevo trabajador a Supabase y su CV al bucket "cvs"
    """
    try:
        # Subir CV si existe
        if cv_file:
            unique_filename = f"{uuid.uuid4()}.pdf"
            path_on_bucket = f"cvs/{unique_filename}"
            supabase.storage.from_("cvs").upload(path_on_bucket, cv_file.read())
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{path_on_bucket}"
            datos["cv_url"] = public_url

        # Convertir skills a texto con formato {a,b,c}
        if isinstance(datos.get("skills"), list):
            datos["skills"] = "{" + ",".join(datos["skills"]) + "}"

        supabase.table("trabajadores").insert(datos).execute()

    except Exception as e:
        st.error(f"Error al subir trabajador: {e}")

def eliminar_trabajador(id_empleado: int):
    """
    Elimina un trabajador por su ID
    """
    try:
        supabase.table("trabajadores").delete().eq("id", id_empleado).execute()
    except Exception as e:
        st.error(f"Error al eliminar trabajador: {e}")
def actualizar_trabajador(id_empleado: int, datos: dict):
    """
    Actualiza los campos de un trabajador por su ID.
    """
    try:
        supabase.table("trabajadores").update(datos).eq("id", id_empleado).execute()
    except Exception as e:
        st.error(f"Error al actualizar trabajador: {e}")
def guardar_proyecto(nombre, descripcion, objetivo, duracion, ubicacion, presupuesto, fecha_inicio, participantes):
    try:
        # Convertir lista de participantes en string
        participantes_str = "{" + ",".join(participantes) + "}"

        data = {
            "nombre": nombre,
            "descripcion": descripcion,
            "objetivo": objetivo,
            "duracion": duracion,
            "ubicacion": ubicacion,
            "presupuesto": presupuesto,
            "fecha_inicio": fecha_inicio.isoformat(),
            "participantes": participantes_str,
        }

        response = supabase.table("proyectos").insert(data).execute()
        return response

    except Exception as e:
        st.error(f"Error al guardar proyecto: {e}")
        return None
