import pandas as pd
from datetime import date

def calcular_semanas_disponibilidad(df: pd.DataFrame, hoy: date) -> pd.DataFrame:
    df_copia = df.copy()

    # Asegurar que la columna 'fin_proyecto' exista y sea datetime
    if "fin_proyecto" not in df_copia.columns:
        df_copia["fin_proyecto"] = pd.NaT
    else:
        df_copia["fin_proyecto"] = pd.to_datetime(df_copia["fin_proyecto"], errors="coerce")

    # Restar solo si 'fin_proyecto' es datetime, else asignar NaT
    df_copia["dias_restantes"] = (df_copia["fin_proyecto"] - pd.to_datetime(hoy)).dt.days

    # Para filas donde fin_proyecto es NaT, dias_restantes será NaN, convertimos a 0 o valor seguro
    df_copia["dias_restantes"] = df_copia["dias_restantes"].fillna(0).astype(int)

    # Calcular semanas disponibles como piso de días_restantes / 7, no negativo
    df_copia["semanas_disponible"] = df_copia["dias_restantes"].apply(lambda x: max(0, x // 7))

    return df_copia
