# models/proyecto.py

from sqlalchemy import Column, Integer, String, Date, Text
from db.db_connector import Base

class Proyecto(Base):
    __tablename__ = "proyectos"

    id             = Column(Integer, primary_key=True)
    nombre         = Column(String, nullable=False)
    fecha_inicio   = Column(Date, nullable=False)
    descripcion    = Column(Text)     # Descripción libre
    metodologia_ia = Column(Text)     # Aquí guardas el texto que devuelve la IA

    def __repr__(self):
        return f"<Proyecto(id={self.id}, nombre={self.nombre})>"
