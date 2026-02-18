from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    tareas = relationship("Task", back_populates="categoria")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, default="")
    prioridad = Column(String, default="media")
    fecha_limite = Column(DateTime, default=None)
    completada = Column(Boolean, default=False)
    creada_en = Column(DateTime, default=datetime.now)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    categoria = relationship("Categoria", back_populates="tareas")