from pydantic import BaseModel
from datetime import datetime
from typing import Optional 

class TaskCreate(BaseModel):
    titulo: str
    descripcion: str
    prioridad: str  = "media"
    fecha_limite: datetime = None
    categoria_id: int = None

class TaskResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    completada: bool
    prioridad: str
    creada_en: datetime
    fecha_limite: Optional[datetime] = None
    categoria_id: Optional[int] = None

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    nombre: str

class CategoryResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True