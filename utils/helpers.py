# utils/helpers.py

from db.db_connector import engine
from models.usuario import Base as BaseUsuario
from models.proyecto import Base as BaseProyecto

def crear_tablas():
    """
    Crea (si no existen) las tablas 'usuarios' y 'proyectos' 
    en la base de datos, basándose en los modelos de SQLAlchemy.
    """
    BaseUsuario.metadata.create_all(bind=engine)
    BaseProyecto.metadata.create_all(bind=engine)
    print("Tablas 'usuarios' y 'proyectos' creadas (si no existían).")
