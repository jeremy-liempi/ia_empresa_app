# logic/supabase_utils.py

import os
import streamlit as st
from supabase import create_client
import pandas as pd

# Cargar credenciales de Supabase (local .env o Streamlit Secrets)
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]

# Crear cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_trabajadores() -> pd.DataFrame:
    """
    Devuelve un DataFrame con todos los registros de la tabla 'trabajadores'.
    """
    resp = supabase.table("trabajadores").select("*").execute()
    return pd.DataFrame(resp.data)

def subir_trabajador(datos: dict, cv_bytes: bytes, filename: str) -> None:
    """
    Sube un nuevo trabajador:
    1) Guarda el CV en el bucket 'cvs' de Supabase Storage.
    2) Inserta el registro en la tabla 'trabajadores', incluyendo la URL pública del CV.
    """
    # 1) Subir el PDF al bucket
    supabase.storage.from_("cvs").upload(f"cvs/{filename}", cv_bytes)
    # Construir URL pública
    cv_url = f"{SUPABASE_URL}/storage/v1/object/public/cvs/{filename}"
    # 2) Insertar el registro, añadiendo la URL del CV
    registro = {**datos, "cv_url": cv_url}
    supabase.table("trabajadores").insert(registro).execute()

def eliminar_trabajador(id: int) -> None:
    """
    Elimina el trabajador cuyo campo 'id' coincida con el proporcionado.
    """
    supabase.table("trabajadores").delete().eq("id", id).execute()

