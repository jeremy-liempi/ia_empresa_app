# logic/data_utils.py
import pandas as pd
import streamlit as st 
from db.db_connector import get_engine

@st.cache_data(ttl=300)
def cargar_trabajadores() -> pd.DataFrame:
    engine = get_engine()
    query = """
        SELECT
          id,
          nombre,
          rol,
          habilidades,
          semanas_disponible,
          fecha_fin_actual
        FROM trabajadores;
    """
    df = pd.read_sql(query, con=engine)
    # Asegúrate de que pandas lo trate como fecha:
    df["fecha_fin_actual"] = pd.to_datetime(df["fecha_fin_actual"], errors="coerce")
    return df