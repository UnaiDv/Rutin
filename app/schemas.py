from pydantic import BaseModel
from datetime import datetime

class TaskCreate(BaseModel):
    titulo: str
    descripcion: str
    prioridad: str  = "media"

class TaskResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    prioridad: str
    completada: bool
    creada_en: datetime

    class Config:
        from_attributes = True