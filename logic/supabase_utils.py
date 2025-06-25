import streamlit as st
import pandas as pd
from supabase import create_client
import uuid

# Leer credenciales desde Streamlit Secrets
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_trabajadores():
    """
    Descarga todos los registros de la tabla 'trabajadores'
    """
    try:
        data = supabase.table("trabajadores").select("*").execute().data
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)

        # Convertir skills de texto a lista si es necesario
        if "skills" in df.columns:
            df["skills"] = df["skills"].apply(lambda s: s.strip("{}").split(",") if s else [])
        return df

    except Exception as e:
        st.error(f"Error al obtener trabajadores: {e}")
        return pd.DataFrame()

def subir_trabajador(datos: dict, cv_file):
    """
    Sube un nuevo trabajador a Supabase y su CV al bucket "cvs"
    """
    try:
        # Subir el CV al bucket
        if cv_file:
            unique_filename = f"{uuid.uuid4()}.pdf"
            path_on_bucket = f"cvs/{unique_filename}"
            supabase.storage.from_("cvs").upload(path_on_bucket, cv_file.read())
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{path_on_bucket}"
            datos["cv_url"] = public_url

        # Convertir skills a formato {skill1,skill2}
        if isinstance(datos.get("skills"), list):
            datos["skills"] = "{" + ",".join(datos["skills"]) + "}"

        # Insertar en Supabase
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

