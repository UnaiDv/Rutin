from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from time import sleep

from .database import SessionLocal, engine, Base
from .models import Task
from .schemas import TaskCreate, TaskResponse

Base.metadata.create_all(bind=engine)


app = FastAPI(title="Rutin - Tu organizador de vida")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="clave1234 ")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, buscar: str = None, 
        prioridad: str = None, estado: str = None, 
        db: Session = Depends(get_db)):

    mensaje = request.session.pop("mensaje", None)

    query = db.query(Task)

    if buscar:
        query = query.filter(Task.titulo.ilike(f"%{buscar}%"))
    if prioridad:
        query = query.filter(Task.prioridad == prioridad)
    if estado == "completadas":
        query = query.filter(Task.completada == True)
    elif estado == "pendientes":
        query = query.filter(Task.completada == False)
    
    query = query.order_by(Task.creada_en.desc())

    tasks = query.all()
    
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks, 
                                    "buscar": buscar, "filtro_prioridad": prioridad, "filtro_completadas": estado, "mensaje": mensaje})



@app.post("/create")
def crear_tarea(request: Request, titulo: str = Form(...), descripcion: str=Form(""), prioridad: str=Form("media"), db: Session = Depends(get_db)):
    nueva_tarea = Task(titulo=titulo, descripcion=descripcion, prioridad=prioridad)
    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)

    request.session["mensaje"] = "Tarea creada con éxito!"

    return RedirectResponse("/", status_code=303)


@app.post("/borrar/{task_id}")
def borrar_tarea(request: Request, task_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Task).filter(Task.id == task_id).first()

    if tarea:
        db.delete(tarea)
        db.commit()

    request.session["mensaje"] = "Tarea borrada con éxito!"
    
    return RedirectResponse("/", status_code=303)


@app.post("/completar/{task_id}")
def completar_tarea(task_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Task).filter(Task.id == task_id).first()

    if tarea:
        tarea.completada = not tarea.completada
        db.commit()
    return RedirectResponse("/", status_code=303)


@app.get("/editar/{task_id}")
def editar_tarea(request: Request, task_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Task).filter(Task.id == task_id).first()
    if not tarea:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("editar_tareas.html", {"request": request, "task": tarea})


@app.post("/editar/{task_id}")
def editar_la_tarea(request: Request, task_id: int, titulo: str = Form(...), descripcion: str = Form(""), prioridad: str = Form("media"), db: Session = Depends(get_db)):
    tarea = db.query(Task).filter(Task.id == task_id).first()

    if tarea:
        tarea.titulo = titulo
        tarea.descripcion = descripcion
        tarea.prioridad = prioridad
        db.commit()
    
    request.session["mensaje"] = "Tarea editada con éxito!"

    return RedirectResponse("/", status_code=303)


@app.post("/duplicar/{task_id}")
def duplicar_tarea(request: Request, task_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Task).filter(Task.id == task_id).first()

    if tarea:
        tarea_duplicada = Task(titulo = "Copia de " + tarea.titulo, descripcion = tarea.descripcion, prioridad = tarea.prioridad)
        db.add(tarea_duplicada)
        db.commit()
    request.session["mensaje"] = "Tarea duplicada con éxito!"

    return RedirectResponse("/", status_code = 303)