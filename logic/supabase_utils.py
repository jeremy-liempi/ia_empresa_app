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
    resp = supabase.table("trabajadores").select("*").execute()
    df = pd.DataFrame(resp.data)

    # Si la tabla está vacía, crear columnas manualmente
    if df.empty:
        df = pd.DataFrame(columns=[
            "id", "nombre", "rut", "cargo", "area", "skills",
            "proyecto_actual", "inicio_proyecto", "fin_proyecto",
            "correo", "telefono", "comentarios", "disponibilidad",
            "cv_url", "años_experiencia"
        ])

    # Asegurar que skills sea una lista vacía si está en blanco
    if "skills" in df.columns:
        df["skills"] = df["skills"].apply(lambda x: x or [])

    return df

def subir_trabajador(datos: dict, cv_bytes: bytes, filename: str) -> None:
    # Subir CV
    supabase.storage.from_("cvs").upload(f"cvs/{filename}", cv_bytes)
    datos["cv_url"] = f"https://shqaysajpwnrvouumngd.supabase.co/storage/v1/object/public/cvs/{filename}"

    # Convertir lista de skills a texto plano
    if "skills" in datos and isinstance(datos["skills"], list):
        datos["skills"] = "{%s}" % ",".join(datos["skills"])

    supabase.table("trabajadores").insert(datos).execute()

def eliminar_trabajador(id: int) -> None:
    supabase.table("trabajadores").delete().eq("id", id).execute()

