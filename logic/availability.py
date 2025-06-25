# logic/availability.py

import pandas as pd
from datetime import date

def calcular_semanas_disponibilidad(df: pd.DataFrame, fecha_actual: date) -> pd.DataFrame:
    df_copia = df.copy()

    # 1) Determinar columna de fin de proyecto: fecha_fin_actual > fin_proyecto > nada
    if "fecha_fin_actual" in df_copia.columns:
        fin = pd.to_datetime(df_copia["fecha_fin_actual"], errors="coerce")
    elif "fin_proyecto" in df_copia.columns:
        fin = pd.to_datetime(df_copia["fin_proyecto"], errors="coerce")
    else:
        fin = pd.NaT

    # 2) Calcular días restantes (NaT → NaN)
    df_copia["dias_restantes"] = (fin - pd.to_datetime(fecha_actual)).dt.days

    # 3) Convertir días a semanas (enteras, no negativas)
    df_copia["semanas_disponible"] = df_copia["dias_restantes"].apply(
        lambda d: max(0, int(d) // 7) if pd.notnull(d) else 0
    )

    return df_copia

def filtrar_por_semanas(df: pd.DataFrame, semanas_max: int) -> pd.DataFrame:
    """
    Filtra el DataFrame por semanas de disponibilidad ≤ semanas_max.
    """
    if "semanas_disponible" not in df.columns:
        return df  # No filtra si no hay esa columna
    return df[df["semanas_disponible"] <= semanas_max]

