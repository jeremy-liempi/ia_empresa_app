import pandas as pd
from datetime import date

def calcular_semanas_disponibilidad(df: pd.DataFrame, hoy: date) -> pd.DataFrame:
    df = df.copy()
    df["fin_proyecto"] = pd.to_datetime(df["fin_proyecto"], errors="coerce")
    df["dias_restantes"] = (df["fin_proyecto"] - hoy).dt.days
    df["semanas_disponible"] = df["dias_restantes"].apply(lambda d: max(0, d // 7) if pd.notnull(d) else 0)
    return df
