from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Rutiner-v1")

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

tasks = []

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

@app.post("/create")
def crear_tarea(title: str = Form(...)):
    tasks.append(title)
    return RedirectResponse("/", status_code=303)
