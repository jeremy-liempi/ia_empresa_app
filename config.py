# config.py
import os
from dotenv import load_dotenv

# 1. Cargar variables de entorno desde .env
load_dotenv()

# 2. Asignar variables a constantes
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_URI = os.getenv("DB_URI")

# 3. Validar que existan; si no, lanzar error
if OPENAI_API_KEY is None:
    raise ValueError("Falta la variable de entorno OPENAI_API_KEY en el archivo .env")
if DB_URI is None:
    raise ValueError("Falta la variable de entorno DB_URI en el archivo .env")
