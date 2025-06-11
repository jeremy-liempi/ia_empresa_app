# models/usuario.py

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

# Base para declarar modelos
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    rol = Column(String(50), nullable=False)
    fecha_fin_actual = Column(Date, nullable=True)

    def __repr__(self):
        return f"<Usuario(id={self.id}, nombre={self.nombre}, rol={self.rol})>"
