from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime

from .database import SessionLocal, engine, Base
from .models import Task, Categoria 
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
    categorias = db.query(Categoria).all()
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
                                    "buscar": buscar, "filtro_prioridad": prioridad, "filtro_completadas": estado, "mensaje": mensaje, "categorias": categorias})



@app.post("/create")
def crear_tarea(request: Request, titulo: str = Form(...), descripcion: str=Form(""), prioridad: str=Form("media"), fecha_limite: str=Form(None), categoria_id: int = Form(None), db: Session = Depends(get_db)):
    fecha = datetime.strptime(fecha_limite, "%Y-%m-%d") if fecha_limite else None
    nueva_tarea = Task(titulo=titulo, descripcion=descripcion, prioridad=prioridad, fecha_limite=fecha, categoria_id=categoria_id)
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
    categorias = db.query(Categoria).all()
    if not tarea:
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse("editar_tareas.html", {"request": request, "task": tarea, "categorias": categorias})


@app.post("/editar/{task_id}")
def editar_la_tarea(request: Request, task_id: int, titulo: str = Form(...), descripcion: str = Form(""), prioridad: str = Form("media"), fecha_limite: str=Form(None), categoria_id: int=Form(None), db: Session = Depends(get_db)):
    tarea = db.query(Task).filter(Task.id == task_id).first()
    fecha = datetime.strptime(fecha_limite, "%Y-%m-%d") if fecha_limite else None
    if tarea:
        tarea.titulo = titulo
        tarea.descripcion = descripcion
        tarea.prioridad = prioridad
        tarea.fecha_limite = fecha
        tarea.categoria_id = categoria_id
        db.commit()
    
    request.session["mensaje"] = "Tarea editada con éxito!"

    return RedirectResponse("/", status_code=303)


@app.post("/duplicar/{task_id}")
def duplicar_tarea(request: Request, task_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Task).filter(Task.id == task_id).first()

    if tarea:
        tarea_duplicada = Task(titulo = "Copia de " + tarea.titulo, descripcion = tarea.descripcion, prioridad = tarea.prioridad, categoria_id = tarea.categoria_id)
        db.add(tarea_duplicada)
        db.commit()
    request.session["mensaje"] = "Tarea duplicada con éxito!"

    return RedirectResponse("/", status_code = 303)

@app.get("/estadisticas")
def estadisticas(request: Request, db: Session = Depends(get_db)):
    total = db.query(Task).count()
    completadas = db.query(Task).filter(Task.completada == True).count()
    pendientes = db.query(Task).filter(Task.completada == False).count() 
    porcentaje_completadas = completadas * 100 // total if total > 0 else 0

    
    return templates.TemplateResponse("estadisticas.html", {"request": request, "completadas": completadas, "pendientes": pendientes, "total": total, "porcentaje_completadas": porcentaje_completadas})

@app.get("/categorias")
def categorias_pagina(request: Request, db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    mensaje_categoria = request.session.pop("mensaje_categoria", None)

    return templates.TemplateResponse("categorias.html", {"request": request, "categorias": categorias, "mensaje_categoria": mensaje_categoria})

@app.post("/categorias/crear")
def categorias_crear(request: Request, nombre: str = Form(...), db: Session = Depends(get_db)):
    categoria_nueva = Categoria(nombre=nombre)
    db.add(categoria_nueva)
    db.commit()
    db.refresh(categoria_nueva)

    request.session["mensaje_categoria"] = "Categoria creada con éxito!"
    
    return RedirectResponse("/categorias", status_code = 303)

@app.post("/categorias/borrar/{categoria_id}")
def categorias_borrar(request: Request, categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    
    if not categoria:
        return RedirectResponse("/categorias", status_code = 303)
    
    db.delete(categoria)
    db.commit()

    return RedirectResponse("/categorias", status_code = 303)

@app.get("/categorias/editar/{categoria_id}")
def categorias_editar(request: Request, categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        return RedirectResponse("/categorias", status_code = 303)

    return templates.TemplateResponse("editar_categorias.html", {"request": request, "categoria": categoria})

@app.post("/categorias/editar/{categoria_id}")
def categorias_editar(request: Request, categoria_id: int, nombre: str = Form(...), db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()

    if not categoria:
        return RedirectResponse("/categorias", status_code = 303)

    categoria.nombre = nombre
    db.commit()

    request.session["mensaje_categoria"] = "Categoria editada con éxito!!"

    return RedirectResponse("/categorias", status_code = 303)