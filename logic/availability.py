# logic/availability.py

import pandas as pd
from datetime import date

def calcular_semanas_disponibilidad(df: pd.DataFrame, fecha_actual: date) -> pd.DataFrame:
    """
    Dado un DataFrame con columna 'fecha_fin_actual' (datetime),
    agrega:
      - 'dias_restantes' = días entre fecha_fin_actual y fecha_actual.
      - 'semanas_disponible' = (dias_restantes // 7) ≥ 0.
    """
    df_copia = df.copy()

    # Asegurar que 'fecha_fin_actual' es datetime
    if not pd.api.types.is_datetime64_any_dtype(df_copia["fecha_fin_actual"]):
        df_copia["fecha_fin_actual"] = pd.to_datetime(df_copia["fecha_fin_actual"])

    # 1. Calcular días restantes
    df_copia["dias_restantes"] = (df_copia["fecha_fin_actual"] - pd.to_datetime(fecha_actual)).dt.days

    # 2. Calcular semanas disponibles (floor division) y forzar ≥ 0
    df_copia["semanas_disponible"] = df_copia["dias_restantes"].apply(lambda d: max(0, d // 7))

    return df_copia

def filtrar_por_semanas(df: pd.DataFrame, semanas_max: int) -> pd.DataFrame:
    """
    Retorna filas donde 'semanas_disponible' ≤ semanas_max.
    """
    return df[df["semanas_disponible"] <= semanas_max]
