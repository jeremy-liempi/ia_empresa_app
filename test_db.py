# test_db.py

import pandas as pd
from db.db_connector import get_engine

# Obtener el engine
engine = get_engine()

# Leer la tabla 'usuarios' completa
df = pd.read_sql("SELECT * FROM usuarios;", con=engine)

print("----- DataFrame obtenido de la BD -----")
print(df)
