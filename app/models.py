from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from .database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, default="")
    prioridad = Column(String, default="media")
    completada = Column(Boolean, default=False)
    creada_en = Column(DateTime, default=datetime.now)