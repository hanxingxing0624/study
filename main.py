from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

from config import BASE_DIR, DATA_DIR

app = FastAPI(title="Learning Notes")

templates_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")

jinja_env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_template(name: str, **kwargs) -> str:
    template = jinja_env.get_template(name)
    return template.render(**kwargs)


os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static", "css"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static", "js"), exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

from models import SessionLocal


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    db = SessionLocal()
    request.state.db = db
    try:
        response = await call_next(request)
    finally:
        db.close()
    return response


def get_db(request: Request):
    return request.state.db


from routes import folders, notes
app.include_router(folders.router)
app.include_router(notes.router)
from routes import tags
app.include_router(tags.router)
from routes import search
app.include_router(search.router)
