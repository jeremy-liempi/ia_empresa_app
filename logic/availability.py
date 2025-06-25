# logic/availability.py

import pandas as pd
from datetime import date

def calcular_semanas_disponibilidad(df: pd.DataFrame, fecha_actual: date) -> pd.DataFrame:
    """
    Agrega columnas 'dias_restantes' y 'semanas_disponible' al DataFrame.
    Requiere columna 'fin_proyecto' en formato fecha.
    """
    df_copia = df.copy()

    # Asegura que la columna exista
    if "fin_proyecto" not in df_copia.columns:
        df_copia["fin_proyecto"] = pd.NaT

    # Asegura que es tipo datetime
    df_copia["fin_proyecto"] = pd.to_datetime(df_copia["fin_proyecto"], errors="coerce")

    # Cálculo de días restantes
    df_copia["dias_restantes"] = (df_copia["fin_proyecto"] - fecha_actual).dt.days

    # Cálculo de semanas disponibles, asegurando que no haya valores negativos ni NaN
    df_copia["semanas_disponible"] = df_copia["dias_restantes"].apply(
        lambda d: max(0, d // 7) if pd.notnull(d) else 0
    )

    return df_copia

def filtrar_por_semanas(df: pd.DataFrame, semanas_max: int) -> pd.DataFrame:
    """
    Filtra el DataFrame por semanas de disponibilidad ≤ semanas_max.
    """
    if "semanas_disponible" not in df.columns:
        return df  # No filtra si no hay esa columna
    return df[df["semanas_disponible"] <= semanas_max]
