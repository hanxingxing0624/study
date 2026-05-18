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


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    from datetime import datetime, timezone
    from models import Note, Review
    db = request.state.db

    total = db.query(Note).count()
    in_progress = db.query(Note).filter(Note.status == "in_progress").count()

    now = datetime.now(timezone.utc)
    due_reviews = (
        db.query(Review)
        .filter(Review.next_review_at <= now)
        .order_by(Review.next_review_at.asc())
        .limit(5)
        .all()
    )

    recent_notes = (
        db.query(Note)
        .order_by(Note.updated_at.desc())
        .limit(10)
        .all()
    )

    stats = {
        "total": total,
        "in_progress": in_progress,
        "due_reviews": len(due_reviews),
    }

    return render_template("index.html", stats=stats, recent_notes=recent_notes, due_reviews=due_reviews)


from routes import folders, notes
app.include_router(folders.router)
app.include_router(notes.router)
from routes import tags
app.include_router(tags.router)
from routes import search
app.include_router(search.router)
from routes import review
app.include_router(review.router)
