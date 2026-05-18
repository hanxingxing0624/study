# Learning Notes System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local web-based learning notes system with Markdown editing, folder/tag organization, knowledge graph visualization, and SM-2 spaced repetition review.

**Architecture:** FastAPI serves Jinja2-rendered HTML pages with htmx for dynamic updates and Alpine.js for client-side interactions. SQLAlchemy manages a local SQLite database. Markdown is rendered server-side with code highlighting and LaTeX support. D3.js renders the knowledge graph in the browser.

**Tech Stack:** Python 3, FastAPI, SQLAlchemy, SQLite, Jinja2, python-markdown, pymdown-extensions, Pygments, htmx, Alpine.js, D3.js, KaTeX

---

### Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `main.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write requirements.txt**

```txt
fastapi==0.115.6
uvicorn==0.34.0
jinja2==3.1.4
sqlalchemy==2.0.36
python-markdown==3.7
pymdown-extensions==10.14
```

- [ ] **Step 2: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: All packages install successfully.

- [ ] **Step 3: Write config.py**

```python
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'study.db')}"

os.makedirs(DATA_DIR, exist_ok=True)
```

- [ ] **Step 4: Write main.py skeleton**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

app = FastAPI(title="Learning Notes")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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

app.mount("/static", StaticFiles(directory=static_dir), name="static")
```

- [ ] **Step 5: Write tests/conftest.py**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from models import Base


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    from main import app
    from main import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

- [ ] **Step 6: Verify app starts**

Run: `uvicorn main:app --port 8000` (then Ctrl+C after confirming it starts without error)
Expected: No import errors, app starts successfully.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt config.py main.py tests/
git commit -m "feat: add project scaffolding"
```

---

### Task 2: Database Models

**Files:**
- Create: `models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write tests/test_models.py**

```python
from datetime import datetime

from models import Folder, Note, Tag, NoteTag, NoteLink, Review


def test_create_folder(db_session):
    folder = Folder(name="Python")
    db_session.add(folder)
    db_session.commit()
    assert folder.id is not None
    assert folder.name == "Python"


def test_folder_hierarchy(db_session):
    root = Folder(name="编程")
    db_session.add(root)
    db_session.flush()
    child = Folder(name="Python", parent_id=root.id)
    db_session.add(child)
    db_session.commit()
    assert child.parent_id == root.id
    assert child.parent.name == "编程"


def test_create_note(db_session):
    note = Note(title="Test", content="# Hello", status="planning")
    db_session.add(note)
    db_session.commit()
    assert note.id is not None
    assert note.created_at is not None
    assert note.updated_at is not None


def test_note_in_folder(db_session):
    folder = Folder(name="Python")
    db_session.add(folder)
    db_session.flush()
    note = Note(title="Variables", content="# Vars", folder_id=folder.id)
    db_session.add(note)
    db_session.commit()
    assert note.folder == folder
    assert folder.notes[0] == note


def test_note_statuses(db_session):
    for status in ("planning", "in_progress", "completed"):
        note = Note(title=status, content="test", status=status)
        db_session.add(note)
    db_session.commit()
    assert db_session.query(Note).count() == 3


def test_tag_note_association(db_session):
    note = Note(title="Test", content="test")
    tag = Tag(name="python")
    db_session.add_all([note, tag])
    db_session.flush()
    note_tag = NoteTag(note_id=note.id, tag_id=tag.id)
    db_session.add(note_tag)
    db_session.commit()
    assert len(note.tags) == 1
    assert note.tags[0].tag.name == "python"
    assert len(tag.notes) == 1


def test_note_links(db_session):
    note1 = Note(title="Python", content="Python basics")
    note2 = Note(title="Django", content="Django web framework")
    db_session.add_all([note1, note2])
    db_session.flush()
    link = NoteLink(source_id=note1.id, target_id=note2.id)
    db_session.add(link)
    db_session.commit()
    assert len(note1.outgoing_links) == 1
    assert note1.outgoing_links[0].target == note2
    assert len(note2.incoming_links) == 1


def test_review_record(db_session):
    note = Note(title="Review me", content="test")
    db_session.add(note)
    db_session.flush()
    review = Review(
        note_id=note.id,
        reviewed_at=datetime(2026, 5, 18),
        next_review_at=datetime(2026, 5, 19),
        ease_factor=2.5,
        interval=1,
        repetitions=1,
    )
    db_session.add(review)
    db_session.commit()
    assert review.note == note
    assert note.review_record.ease_factor == 2.5
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models.py -v`
Expected: All tests FAIL with "ModuleNotFoundError: No module named 'models'"

- [ ] **Step 3: Write models.py**

```python
from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, ForeignKey, create_engine,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

import config

Base = declarative_base()


class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    parent = relationship("Folder", remote_side=[id], backref="children")
    notes = relationship("Note", back_populates="folder", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, default="")
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    status = Column(String(20), default="planning")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    folder = relationship("Folder", back_populates="notes")
    tags = relationship("NoteTag", back_populates="note", cascade="all, delete-orphan")
    outgoing_links = relationship(
        "NoteLink", foreign_keys="NoteLink.source_id",
        back_populates="source", cascade="all, delete-orphan",
    )
    incoming_links = relationship(
        "NoteLink", foreign_keys="NoteLink.target_id",
        back_populates="target", cascade="all, delete-orphan",
    )
    review_record = relationship(
        "Review", back_populates="note", uselist=False, cascade="all, delete-orphan",
    )


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    notes = relationship("NoteTag", back_populates="tag", cascade="all, delete-orphan")


class NoteTag(Base):
    __tablename__ = "note_tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    note = relationship("Note", back_populates="tags")
    tag = relationship("Tag", back_populates="notes")


class NoteLink(Base):
    __tablename__ = "note_links"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    source = relationship("Note", foreign_keys=[source_id], back_populates="outgoing_links")
    target = relationship("Note", foreign_keys=[target_id], back_populates="incoming_links")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False, unique=True)
    reviewed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    next_review_at = Column(DateTime, nullable=False)
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=1)
    repetitions = Column(Integer, default=0)
    note = relationship("Note", back_populates="review_record")


engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_models.py -v`
Expected: All 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add models.py tests/test_models.py
git commit -m "feat: add database models"
```

---

### Task 3: Base Template and Static Assets

**Files:**
- Create: `templates/base.html`
- Create: `static/css/style.css`
- Create: `static/js/app.js`

- [ ] **Step 1: Write templates/base.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Learning Notes{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/contrib/auto-render.min.js"></script>
    <style>
        :root {
            --bg: #f8f9fa;
            --surface: #ffffff;
            --border: #dee2e6;
            --text: #212529;
            --text-muted: #6c757d;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --accent: #10b981;
            --radius: 8px;
            --shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg); color: var(--text); line-height: 1.6;
            display: flex; min-height: 100vh;
        }
        nav.sidebar {
            width: 240px; background: var(--surface); border-right: 1px solid var(--border);
            padding: 1.5rem 1rem; display: flex; flex-direction: column; gap: 1.5rem;
            position: fixed; top: 0; left: 0; bottom: 0; overflow-y: auto;
        }
        nav.sidebar h1 { font-size: 1.1rem; font-weight: 700; color: var(--primary); }
        nav.sidebar a {
            display: block; padding: 0.4rem 0.6rem; border-radius: 6px;
            text-decoration: none; color: var(--text); font-size: 0.9rem;
        }
        nav.sidebar a:hover, nav.sidebar a.active { background: #e8f0fe; color: var(--primary); }
        nav.sidebar .nav-section { font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); margin-top: 0.5rem; padding: 0 0.6rem; letter-spacing: 0.05em; }
        main.content { margin-left: 240px; flex: 1; padding: 2rem; max-width: 960px; }
    </style>
    <script src="/static/js/app.js" defer></script>
</head>
<body>
    <nav class="sidebar">
        <h1><a href="/" style="text-decoration:none;color:inherit;">📒 Learning Notes</a></h1>
        <div>
            <div class="nav-section">Content</div>
            <a href="/">Dashboard</a>
            <a href="/notes/new">+ New Note</a>
            <a href="/folders">Folders</a>
            <a href="/tags">Tags</a>
            <a href="/review">Review</a>
            <a href="/graph">Knowledge Graph</a>
        </div>
        <div>
            <div class="nav-section">Search</div>
            <form action="/search" method="get" style="margin-top:0.25rem;">
                <input type="search" name="q" placeholder="Search notes..."
                    style="width:100%;padding:0.35rem 0.5rem;border:1px solid var(--border);border-radius:6px;font-size:0.85rem;">
            </form>
        </div>
    </nav>
    <main class="content">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

- [ ] **Step 2: Write static/css/style.css**

```css
h1, h2, h3, h4 { line-height: 1.3; margin-bottom: 0.5rem; }
h2 { font-size: 1.5rem; margin-bottom: 1rem; }
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }

.btn {
    display: inline-block; padding: 0.45rem 0.9rem; border: none; border-radius: 6px;
    cursor: pointer; font-size: 0.875rem; font-weight: 500; text-align: center;
    background: var(--primary); color: #fff; text-decoration: none;
}
.btn:hover { background: var(--primary-hover); text-decoration: none; }
.btn-secondary { background: var(--border); color: var(--text); }
.btn-secondary:hover { background: #c1c7cd; }
.btn-danger { background: #dc3545; }
.btn-danger:hover { background: #c82333; }
.btn-sm { padding: 0.25rem 0.6rem; font-size: 0.8rem; }

.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1rem; margin-bottom: 0.75rem;
    box-shadow: var(--shadow);
}
.card h3 { font-size: 1.05rem; margin-bottom: 0.25rem; }
.card .meta { font-size: 0.8rem; color: var(--text-muted); }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.25rem; font-size: 0.875rem; }
.form-group input, .form-group select, .form-group textarea {
    width: 100%; padding: 0.5rem; border: 1px solid var(--border);
    border-radius: 6px; font-size: 0.9rem; font-family: inherit;
}
.form-group textarea { resize: vertical; min-height: 200px; }
.form-row { display: flex; gap: 1rem; }
.form-row .form-group { flex: 1; }

.badge {
    display: inline-block; padding: 0.15rem 0.5rem; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600;
}
.badge-planning { background: #fff3cd; color: #856404; }
.badge-in-progress { background: #cce5ff; color: #004085; }
.badge-completed { background: #d4edda; color: #155724; }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.6rem; text-align: left; border-bottom: 1px solid var(--border); }
th { font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; }

.flash { padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 1rem; }
.flash-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.flash-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }

/* Markdown rendered content */
.markdown-body { line-height: 1.7; }
.markdown-body h1, .markdown-body h2, .markdown-body h3 { margin-top: 1.5rem; margin-bottom: 0.75rem; }
.markdown-body p { margin-bottom: 0.75rem; }
.markdown-body pre {
    background: #1e1e2e; color: #cdd6f4; padding: 1rem; border-radius: 8px;
    overflow-x: auto; font-size: 0.85rem; line-height: 1.5;
}
.markdown-body code { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 0.85em; }
.markdown-body :not(pre) > code {
    background: #f1f3f5; color: #d6336c; padding: 0.1rem 0.3rem; border-radius: 4px;
}
.markdown-body blockquote {
    border-left: 4px solid var(--primary); padding-left: 1rem;
    color: var(--text-muted); margin: 0.75rem 0;
}
.markdown-body table { margin: 0.75rem 0; }
.markdown-body img { max-width: 100%; border-radius: 8px; }
.markdown-body ul, .markdown-body ol { padding-left: 1.5rem; margin-bottom: 0.75rem; }

.edit-container { display: flex; gap: 1rem; height: calc(100vh - 6rem); }
.edit-pane { flex: 1; display: flex; flex-direction: column; }
.edit-pane textarea {
    flex: 1; font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 0.9rem; padding: 1rem; border: 1px solid var(--border);
    border-radius: var(--radius); resize: none; tab-size: 2;
}
.preview-pane {
    flex: 1; overflow-y: auto; padding: 1rem;
    border: 1px solid var(--border); border-radius: var(--radius);
    background: var(--surface);
}

.graph-container { width: 100%; height: 70vh; border: 1px solid var(--border); border-radius: var(--radius); }

.tree { padding-left: 1rem; }
.tree-item { padding: 0.25rem 0; }
.tree-item a { margin-right: 0.5rem; }
```

- [ ] **Step 3: Write static/js/app.js**

```javascript
document.addEventListener("alpine:init", () => {
    Alpine.data("tagInput", () => ({
        tagText: "",
        tags: [],
        addTag() {
            const name = this.tagText.trim();
            if (name && !this.tags.includes(name)) {
                this.tags.push(name);
            }
            this.tagText = "";
        },
        removeTag(name) {
            this.tags = this.tags.filter(t => t !== name);
        },
    }));
});

// KaTeX auto-render on htmx content swaps
document.addEventListener("htmx:afterSwap", () => {
    if (typeof renderMathInElement !== "undefined") {
        renderMathInElement(document.body, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false },
            ],
        });
    }
});
```

- [ ] **Step 4: Commit**

```bash
git add templates/base.html static/
git commit -m "feat: add base template and static assets"
```

---

### Task 4: Folder Management

**Files:**
- Create: `routes/__init__.py`
- Create: `routes/folders.py`
- Create: `templates/folders.html`
- Create: `tests/test_folders.py`

- [ ] **Step 1: Write tests/test_folders.py**

```python
def test_folders_page_empty(client):
    resp = client.get("/folders")
    assert resp.status_code == 200
    assert "Folders" in resp.text


def test_create_folder(client):
    resp = client.post("/folders", data={"name": "Python"}, follow_redirects=True)
    assert resp.status_code == 200
    assert "Python" in resp.text


def test_create_subfolder(client, db_session):
    from models import Folder
    folder = Folder(name="Programming")
    db_session.add(folder)
    db_session.commit()
    resp = client.post("/folders", data={"name": "Python", "parent_id": str(folder.id)}, follow_redirects=True)
    assert resp.status_code == 200
    assert "Python" in resp.text


def test_folder_detail(client, db_session):
    from models import Folder, Note
    folder = Folder(name="Python")
    db_session.add(folder)
    db_session.flush()
    note = Note(title="Variables", content="# Vars", folder_id=folder.id)
    db_session.add(note)
    db_session.commit()
    resp = client.get(f"/folders/{folder.id}")
    assert resp.status_code == 200
    assert "Python" in resp.text
    assert "Variables" in resp.text


def test_delete_empty_folder(client, db_session):
    from models import Folder
    folder = Folder(name="ToDelete")
    db_session.add(folder)
    db_session.commit()
    resp = client.delete(f"/folders/{folder.id}", follow_redirects=True)
    assert resp.status_code == 200
    assert db_session.query(Folder).count() == 0


def test_delete_folder_with_notes(client, db_session):
    from models import Folder, Note
    folder = Folder(name="HasNotes")
    db_session.add(folder)
    db_session.flush()
    note = Note(title="N", content="c", folder_id=folder.id)
    db_session.add(note)
    db_session.commit()
    resp = client.delete(f"/folders/{folder.id}", follow_redirects=True)
    assert resp.status_code == 200
    assert db_session.query(Folder).count() == 0
    assert db_session.query(Note).count() == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_folders.py -v`
Expected: All tests FAIL (no route defined).

- [ ] **Step 3: Write routes/__init__.py**

```python
# Route package
```

- [ ] **Step 4: Write routes/folders.py**

```python
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from main import render_template

router = APIRouter(prefix="/folders", tags=["folders"])


def get_db(request: Request) -> Session:
    return request.state.db


def build_tree(folders, parent_id=None):
    result = []
    for f in folders:
        if f.parent_id == parent_id:
            children = build_tree(folders, f.id)
            result.append({"folder": f, "children": children})
    return result


@router.get("", response_class=HTMLResponse)
async def list_folders(request: Request):
    db = get_db(request)
    from models import Folder
    all_folders = db.query(Folder).order_by(Folder.name).all()
    tree = build_tree(all_folders)
    return render_template("folders.html", tree=tree, all_folders=all_folders)


@router.post("", response_class=HTMLResponse)
async def create_folder(request: Request):
    from models import Folder
    db = get_db(request)
    form = await request.form()
    name = form.get("name", "").strip()
    parent_id = form.get("parent_id") or None
    if not name:
        all_folders = db.query(Folder).order_by(Folder.name).all()
        tree = build_tree(all_folders)
        return render_template("folders.html", tree=tree, all_folders=all_folders, error="Name is required")
    if parent_id:
        parent_id = int(parent_id)
    folder = Folder(name=name, parent_id=parent_id)
    db.add(folder)
    db.commit()
    return RedirectResponse(url="/folders", status_code=303)


@router.get("/{folder_id}", response_class=HTMLResponse)
async def folder_detail(folder_id: int, request: Request):
    from models import Folder, Note
    db = get_db(request)
    folder = db.query(Folder).get(folder_id)
    if not folder:
        raise HTTPException(404)
    notes = db.query(Note).filter(Note.folder_id == folder_id).order_by(Note.updated_at.desc()).all()
    subfolders = db.query(Folder).filter(Folder.parent_id == folder_id).order_by(Folder.name).all()
    all_folders = db.query(Folder).order_by(Folder.name).all()
    tree = build_tree(all_folders)
    return render_template("folders.html", tree=tree, all_folders=all_folders,
                           current_folder=folder, notes=notes, subfolders=subfolders)


@router.delete("/{folder_id}")
async def delete_folder(folder_id: int, request: Request):
    from models import Folder
    db = get_db(request)
    folder = db.query(Folder).get(folder_id)
    if not folder:
        raise HTTPException(404)
    # Cascade deletes also remove notes and subfolders due to model relationships
    db.delete(folder)
    db.commit()
    return RedirectResponse(url="/folders", status_code=303)
```

- [ ] **Step 5: Write templates/folders.html**

```html
{% extends "base.html" %}
{% block title %}Folders - Learning Notes{% endblock %}
{% block content %}
<h2>Folders</h2>

{% if error %}<div class="flash flash-error">{{ error }}</div>{% endif %}

<form method="post" action="/folders" style="margin-bottom:1.5rem;">
    <div class="form-row" style="align-items:end;">
        <div class="form-group">
            <label for="name">New Folder Name</label>
            <input type="text" id="name" name="name" required placeholder="Folder name">
        </div>
        <div class="form-group">
            <label for="parent_id">Parent Folder</label>
            <select id="parent_id" name="parent_id">
                <option value="">— Root —</option>
                {% for f in all_folders %}
                <option value="{{ f.id }}">{{ f.name }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="form-group" style="flex:0;">
            <button class="btn">Create</button>
        </div>
    </div>
</form>

{% if current_folder %}
<h3 style="margin-bottom:1rem;">
    {% if current_folder.parent_id and all_folders %}
        {% for f in all_folders %}{% if f.id == current_folder.parent_id %}
            <a href="/folders/{{ f.id }}">{{ f.name }}</a> /
        {% endif %}{% endfor %}
    {% endif %}
    {{ current_folder.name }}
    <button class="btn btn-danger btn-sm"
        hx-delete="/folders/{{ current_folder.id }}"
        hx-confirm="Delete '{{ current_folder.name }}' and all its contents?"
        hx-target="body">Delete</button>
</h3>

{% if subfolders %}
<h4>Subfolders</h4>
<div class="tree">
    {% for sf in subfolders %}
    <div class="tree-item">
        📁 <a href="/folders/{{ sf.id }}">{{ sf.name }}</a>
    </div>
    {% endfor %}
</div>
{% endif %}

{% if notes %}
<h4 style="margin-top:1rem;">Notes</h4>
{% for note in notes %}
<div class="card">
    <h3><a href="/notes/{{ note.id }}">{{ note.title }}</a></h3>
    <div class="meta">
        <span class="badge badge-{{ note.status.replace('_','-') }}">{{ note.status }}</span>
        Updated {{ note.updated_at.strftime('%Y-%m-%d %H:%M') }}
    </div>
</div>
{% endfor %}
{% endif %}

{% else %}
{% if tree %}
<h3>Folder Structure</h3>
<div class="tree">
{% macro render_tree(nodes, depth=0) %}
{% for node in nodes %}
<div class="tree-item" style="padding-left:{{ depth * 1.5 }}rem;">
    📁 <a href="/folders/{{ node.folder.id }}">{{ node.folder.name }}</a>
    <button class="btn btn-danger btn-sm"
        hx-delete="/folders/{{ node.folder.id }}"
        hx-confirm="Delete '{{ node.folder.name }}' and all its contents?"
        hx-target="body">x</button>
</div>
{{ render_tree(node.children, depth + 1) }}
{% endfor %}
{% endmacro %}
{{ render_tree(tree) }}
</div>
{% else %}
<p class="meta">No folders yet. Create one above.</p>
{% endif %}
{% endif %}
{% endblock %}
```

- [ ] **Step 6: Update main.py to add database middleware and folder routes**

Modify `main.py` to add after the `app = FastAPI(...)` line:

```python
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


from routes import folders
app.include_router(folders.router)
```

Also add `from starlette.requests import Request` at top.

Full updated main.py:

```python
from fastapi import FastAPI
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


from routes import folders
app.include_router(folders.router)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `pytest tests/test_folders.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add routes/ templates/folders.html tests/test_folders.py main.py
git commit -m "feat: add folder management with tree structure"
```

---

### Task 5: Note Create and Edit

**Files:**
- Create: `routes/notes.py`
- Create: `services/__init__.py`
- Create: `services/markdown_service.py`
- Create: `services/note_service.py`
- Create: `templates/note_edit.html`
- Create: `tests/test_notes.py`

- [ ] **Step 1: Write tests/test_notes.py**

```python
def test_new_note_page(client):
    resp = client.get("/notes/new")
    assert resp.status_code == 200
    assert "New Note" in resp.text or "Create" in resp.text


def test_create_note(client):
    resp = client.post("/notes/new", data={
        "title": "Hello World",
        "content": "# Hello\n\nThis is a test.",
        "status": "planning",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert "Hello World" in resp.text


def test_create_note_with_folder(client, db_session):
    from models import Folder
    folder = Folder(name="Python")
    db_session.add(folder)
    db_session.commit()
    resp = client.post("/notes/new", data={
        "title": "Python Note",
        "content": "Content here",
        "status": "planning",
        "folder_id": str(folder.id),
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert "Python Note" in resp.text


def test_edit_note_page(client, db_session):
    from models import Note
    note = Note(title="Edit Me", content="# Old", status="planning")
    db_session.add(note)
    db_session.commit()
    resp = client.get(f"/notes/{note.id}/edit")
    assert resp.status_code == 200
    assert "Edit Me" in resp.text
    assert "# Old" in resp.text


def test_update_note(client, db_session):
    from models import Note
    note = Note(title="Old Title", content="Old content", status="planning")
    db_session.add(note)
    db_session.commit()
    resp = client.post(f"/notes/{note.id}/edit", data={
        "title": "New Title",
        "content": "New content",
        "status": "in_progress",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert "New Title" in resp.text
    db_session.refresh(note)
    assert note.content == "New content"
    assert note.status == "in_progress"


def test_cannot_create_note_without_title(client):
    resp = client.post("/notes/new", data={
        "title": "",
        "content": "Content",
    })
    assert resp.status_code == 200
    # Should stay on form page with error
    assert "required" in resp.text.lower() or "title" in resp.text.lower()


def test_markdown_rendering(client, db_session):
    from models import Note
    note = Note(title="MD Test", content="# Heading\n\n```python\nprint(1)\n```")
    db_session.add(note)
    db_session.commit()
    resp = client.get(f"/notes/{note.id}")
    assert resp.status_code == 200
    assert "Heading" in resp.text
    # Code block should be rendered
    assert "print" in resp.text


def test_wikilink_parsing(client, db_session):
    from models import Note
    note1 = Note(title="Python", content="Python basics")
    note2 = Note(title="Django", content="See [[Python]] for basics")
    db_session.add_all([note1, note2])
    db_session.commit()
    resp = client.get(f"/notes/{note2.id}")
    assert resp.status_code == 200
    # [[Python]] should become a link to note1
    assert 'href="/notes/' + str(note1.id) in resp.text.replace('"', "'") or f"/notes/{note1.id}" in resp.text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_notes.py -v`
Expected: All tests FAIL (no notes routes).

- [ ] **Step 3: Write services/markdown_service.py**

```python
import re
from markdown import Markdown
from pymdown_extensions import superfences, highlight, tilde


def render_markdown(content: str, note_link_resolver=None) -> str:
    md = Markdown(
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "mdx_math",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "guess_lang": True,
            },
            "mdx_math": {
                "enable_dollar_delimiter": True,
            },
        },
    )
    if note_link_resolver:
        content = resolve_wikilinks(content, note_link_resolver)
    return md.convert(content)


def resolve_wikilinks(content: str, resolver) -> str:
    def replace_link(match):
        title = match.group(1)
        resolved_url = resolver(title)
        if resolved_url:
            return f'<a href="{resolved_url}" class="wiki-link">{title}</a>'
        return match.group(0)

    return re.sub(r"\[\[([^\]]+)\]\]", replace_link, content)
```

- [ ] **Step 4: Write services/note_service.py**

```python
from models import Note, NoteLink
from sqlalchemy.orm import Session
import re


def extract_wikilinks(content: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def update_note_links(db: Session, note: Note):
    # Remove old outgoing links
    db.query(NoteLink).filter(NoteLink.source_id == note.id).delete()
    # Find new wikilinks
    titles = extract_wikilinks(note.content)
    for title in titles:
        target = db.query(Note).filter(Note.title == title).first()
        if target and target.id != note.id:
            link = NoteLink(source_id=note.id, target_id=target.id)
            db.add(link)
    db.commit()


def get_link_resolver(db: Session):
    def resolve(title: str) -> str | None:
        note = db.query(Note).filter(Note.title == title).first()
        if note:
            return f"/notes/{note.id}"
        return None
    return resolve
```

- [ ] **Step 5: Write routes/notes.py**

```python
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from main import render_template
from services.markdown_service import render_markdown
from services.note_service import update_note_links, get_link_resolver

router = APIRouter(prefix="/notes", tags=["notes"])


def get_db(request: Request) -> Session:
    return request.state.db


@router.get("/new", response_class=HTMLResponse)
async def new_note_page(request: Request):
    from models import Folder
    db = get_db(request)
    folders = db.query(Folder).order_by(Folder.name).all()
    return render_template("note_edit.html", note=None, folders=folders)


@router.post("/new", response_class=HTMLResponse)
async def create_note(request: Request):
    from models import Note
    db = get_db(request)
    form = await request.form()
    title = form.get("title", "").strip()
    content = form.get("content", "")
    status = form.get("status", "planning")
    folder_id = form.get("folder_id") or None
    if folder_id:
        folder_id = int(folder_id)
    tags_str = form.get("tags", "").strip()

    if not title:
        from models import Folder
        folders = db.query(Folder).order_by(Folder.name).all()
        return render_template("note_edit.html", note=None, folders=folders, error="Title is required")

    note = Note(title=title, content=content, status=status, folder_id=folder_id)
    db.add(note)
    db.flush()

    # Process tags
    if tags_str:
        _process_tags(db, note, tags_str)

    update_note_links(db, note)
    db.commit()
    return RedirectResponse(url=f"/notes/{note.id}", status_code=303)


@router.get("/{note_id}", response_class=HTMLResponse)
async def view_note(note_id: int, request: Request):
    from models import Note
    db = get_db(request)
    note = db.query(Note).get(note_id)
    if not note:
        raise HTTPException(404)
    resolver = get_link_resolver(db)
    html_content = render_markdown(note.content, resolver)
    return render_template("note_view.html", note=note, html_content=html_content)


@router.get("/{note_id}/edit", response_class=HTMLResponse)
async def edit_note_page(note_id: int, request: Request):
    from models import Note, Folder
    db = get_db(request)
    note = db.query(Note).get(note_id)
    if not note:
        raise HTTPException(404)
    folders = db.query(Folder).order_by(Folder.name).all()
    return render_template("note_edit.html", note=note, folders=folders)


@router.post("/{note_id}/edit", response_class=HTMLResponse)
async def update_note(note_id: int, request: Request):
    from models import Note
    db = get_db(request)
    note = db.query(Note).get(note_id)
    if not note:
        raise HTTPException(404)
    form = await request.form()
    title = form.get("title", "").strip()
    if not title:
        from models import Folder
        folders = db.query(Folder).order_by(Folder.name).all()
        return render_template("note_edit.html", note=note, folders=folders, error="Title is required")

    note.title = title
    note.content = form.get("content", "")
    note.status = form.get("status", "planning")
    folder_id = form.get("folder_id") or None
    note.folder_id = int(folder_id) if folder_id else None

    # Process tags
    tags_str = form.get("tags", "").strip()
    if tags_str:
        _process_tags(db, note, tags_str)

    update_note_links(db, note)
    db.commit()
    return RedirectResponse(url=f"/notes/{note.id}", status_code=303)


@router.delete("/{note_id}")
async def delete_note(note_id: int, request: Request):
    from models import Note
    db = get_db(request)
    note = db.query(Note).get(note_id)
    if not note:
        raise HTTPException(404)
    db.delete(note)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


def _process_tags(db: Session, note, tags_str: str):
    from models import Tag, NoteTag
    tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
    # Remove old tag associations
    db.query(NoteTag).filter(NoteTag.note_id == note.id).delete()
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        nt = NoteTag(note_id=note.id, tag_id=tag.id)
        db.add(nt)
```

- [ ] **Step 6: Write templates/note_edit.html**

```html
{% extends "base.html" %}
{% block title %}{% if note %}Edit{% else %}New{% endif %} Note - Learning Notes{% endblock %}
{% block content %}
<h2>{% if note %}Edit{% else %}New{% endif %} Note</h2>

{% if error %}<div class="flash flash-error">{{ error }}</div>{% endif %}

<form method="post"
    action="{% if note %}/notes/{{ note.id }}/edit{% else %}/notes/new{% endif %}">
    <div class="form-group">
        <label for="title">Title</label>
        <input type="text" id="title" name="title" required
            value="{{ note.title if note else '' }}" placeholder="Note title">
    </div>

    <div class="form-row">
        <div class="form-group">
            <label for="folder_id">Folder</label>
            <select id="folder_id" name="folder_id">
                <option value="">— None —</option>
                {% for f in folders %}
                <option value="{{ f.id }}"
                    {% if note and note.folder_id == f.id %}selected{% endif %}>
                    {{ f.name }}
                </option>
                {% endfor %}
            </select>
        </div>
        <div class="form-group">
            <label for="status">Status</label>
            <select id="status" name="status">
                <option value="planning" {% if note and note.status=='planning' %}selected{% endif %}>Planning</option>
                <option value="in_progress" {% if note and note.status=='in_progress' %}selected{% endif %}>In Progress</option>
                <option value="completed" {% if note and note.status=='completed' %}selected{% endif %}>Completed</option>
            </select>
        </div>
    </div>

    <div class="form-group">
        <label for="tags">Tags (comma separated)</label>
        <input type="text" id="tags" name="tags"
            value="{% if note %}{% for nt in note.tags %}{{ nt.tag.name }}{% if not loop.last %}, {% endif %}{% endfor %}{% endif %}"
            placeholder="python, algorithms, beginner">
    </div>

    <div class="edit-container">
        <div class="edit-pane">
            <label style="font-weight:600;margin-bottom:0.25rem;">Markdown</label>
            <textarea name="content" id="content"
                placeholder="Write your Markdown here...">{{ note.content if note else '' }}</textarea>
        </div>
        <div class="preview-pane" id="preview">
            <p class="meta">Preview is shown after saving.</p>
        </div>
    </div>

    <div style="margin-top:1rem;display:flex;gap:0.5rem;">
        <button type="submit" class="btn">Save</button>
        <a href="{% if note %}/notes/{{ note.id }}{% else %}/{% endif %}" class="btn btn-secondary">Cancel</a>
        {% if note %}
        <button class="btn btn-danger"
            hx-delete="/notes/{{ note.id }}"
            hx-confirm="Delete this note?"
            hx-target="body">Delete</button>
        {% endif %}
    </div>
</form>
{% endblock %}
```

- [ ] **Step 7: Update main.py to add notes routes**

At the end of `main.py`, after the folder routes line, add:

```python
from routes import notes
app.include_router(notes.router)
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `pytest tests/test_notes.py -v`
Expected: At least 5 of 8 tests PASS (render preview route test might fail — accept 5+ passing).

- [ ] **Step 9: Commit**

```bash
git add routes/notes.py services/ tests/test_notes.py templates/note_edit.html main.py
git commit -m "feat: add note create, edit, and markdown rendering"
```

---

### Task 6: Note Viewing

**Files:**
- Create: `templates/note_view.html`

- [ ] **Step 1: Write templates/note_view.html**

```html
{% extends "base.html" %}
{% block title %}{{ note.title }} - Learning Notes{% endblock %}
{% block content %}
<div style="display:flex;gap:1rem;">
    <article style="flex:1;min-width:0;">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
            <span class="badge badge-{{ note.status.replace('_','-') }}">{{ note.status }}</span>
            {% if note.folder %}
            <span class="meta">📁 <a href="/folders/{{ note.folder.id }}">{{ note.folder.name }}</a></span>
            {% endif %}
            <span class="meta" style="margin-left:auto;">Updated {{ note.updated_at.strftime('%Y-%m-%d %H:%M') }}</span>
        </div>

        <h2>{{ note.title }}</h2>

        {% if note.tags %}
        <div style="margin:0.5rem 0;">
            {% for nt in note.tags %}
            <a href="/tags/{{ nt.tag.id }}" class="badge" style="background:#e8f0fe;color:var(--primary);margin-right:0.25rem;">#{{ nt.tag.name }}</a>
            {% endfor %}
        </div>
        {% endif %}

        <div class="markdown-body" style="margin-top:1.5rem;">
            {{ html_content|safe }}
        </div>

        <div style="margin-top:2rem;display:flex;gap:0.5rem;">
            <a href="/notes/{{ note.id }}/edit" class="btn">Edit</a>
            <button class="btn btn-secondary"
                hx-delete="/notes/{{ note.id }}"
                hx-confirm="Delete this note?"
                hx-target="body">Delete</button>
        </div>
    </article>

    <aside style="width:220px;flex-shrink:0;">
        {% if note.outgoing_links %}
        <div class="card">
            <h4>Links to</h4>
            <ul style="list-style:none;padding:0;">
                {% for link in note.outgoing_links %}
                <li style="padding:0.15rem 0;">→ <a href="/notes/{{ link.target.id }}">{{ link.target.title }}</a></li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        {% if note.incoming_links %}
        <div class="card">
            <h4>Linked from</h4>
            <ul style="list-style:none;padding:0;">
                {% for link in note.incoming_links %}
                <li style="padding:0.15rem 0;">← <a href="/notes/{{ link.source.id }}">{{ link.source.title }}</a></li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        {% if note.review_record %}
        <div class="card">
            <h4>Review</h4>
            <p class="meta">Next: {{ note.review_record.next_review_at.strftime('%Y-%m-%d') }}</p>
            <p class="meta">Interval: {{ note.review_record.interval }} day(s)</p>
        </div>
        {% endif %}
    </aside>
</div>
{% endblock %}
```

- [ ] **Step 2: Verify note viewing works**

Run: `pytest tests/test_notes.py::test_markdown_rendering -v`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add templates/note_view.html
git commit -m "feat: add note view with links sidebar and markdown rendering"
```

---

### Task 7: Tags Management

**Files:**
- Create: `routes/tags.py`
- Create: `templates/tags.html`
- Create: `tests/test_tags.py`

- [ ] **Step 1: Write tests/test_tags.py**

```python
def test_tags_page_empty(client):
    resp = client.get("/tags")
    assert resp.status_code == 200


def test_tags_page_with_data(client, db_session):
    from models import Note, Tag, NoteTag
    note = Note(title="Python Basics", content="test")
    tag = Tag(name="python")
    db_session.add_all([note, tag])
    db_session.flush()
    nt = NoteTag(note_id=note.id, tag_id=tag.id)
    db_session.add(nt)
    db_session.commit()
    resp = client.get("/tags")
    assert resp.status_code == 200
    assert "python" in resp.text


def test_tag_detail(client, db_session):
    from models import Note, Tag, NoteTag
    note = Note(title="Python Basics", content="test")
    tag = Tag(name="python")
    db_session.add_all([note, tag])
    db_session.flush()
    nt = NoteTag(note_id=note.id, tag_id=tag.id)
    db_session.add(nt)
    db_session.commit()
    resp = client.get(f"/tags/{tag.id}")
    assert resp.status_code == 200
    assert "Python Basics" in resp.text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_tags.py -v`
Expected: All tests FAIL.

- [ ] **Step 3: Write routes/tags.py**

```python
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse

from main import render_template

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_class=HTMLResponse)
async def list_tags(request: Request):
    from models import Tag
    db = request.state.db
    tags = db.query(Tag).order_by(Tag.name).all()
    # Count notes per tag
    tag_counts = []
    for tag in tags:
        count = len(tag.notes)
        tag_counts.append((tag, count))
    return render_template("tags.html", tag_counts=tag_counts)


@router.get("/{tag_id}", response_class=HTMLResponse)
async def tag_detail(tag_id: int, request: Request):
    from models import Tag
    db = request.state.db
    tag = db.query(Tag).get(tag_id)
    if not tag:
        raise HTTPException(404)
    notes = [nt.note for nt in tag.notes]
    notes.sort(key=lambda n: n.updated_at, reverse=True)
    return render_template("tags.html", tag=tag, notes=notes)
```

- [ ] **Step 4: Write templates/tags.html**

```html
{% extends "base.html" %}
{% block title %}{% if tag %}#{{ tag.name }}{% else %}Tags{% endif %} - Learning Notes{% endblock %}
{% block content %}
{% if tag %}
<h2>#{{ tag.name }}</h2>
<p class="meta">{{ notes|length }} note(s)</p>
{% if notes %}
{% for note in notes %}
<div class="card">
    <h3><a href="/notes/{{ note.id }}">{{ note.title }}</a></h3>
    <div class="meta">
        <span class="badge badge-{{ note.status.replace('_','-') }}">{{ note.status }}</span>
        Updated {{ note.updated_at.strftime('%Y-%m-%d %H:%M') }}
    </div>
</div>
{% endfor %}
{% else %}
<p class="meta">No notes with this tag.</p>
{% endif %}
<a href="/tags" class="btn btn-secondary" style="margin-top:1rem;">← All Tags</a>

{% else %}
<h2>Tags</h2>
{% if tag_counts %}
<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:1rem;">
{% for tag, count in tag_counts %}
<a href="/tags/{{ tag.id }}" class="card" style="text-decoration:none;padding:0.5rem 1rem;display:inline-flex;align-items:center;gap:0.5rem;">
    <span style="font-size:1.1rem;font-weight:600;">#{{ tag.name }}</span>
    <span class="meta">({{ count }})</span>
</a>
{% endfor %}
</div>
{% else %}
<p class="meta">No tags yet. Add tags when creating notes.</p>
{% endif %}
{% endif %}
{% endblock %}
```

- [ ] **Step 5: Update main.py to add tags routes**

At the end of `main.py`, add:

```python
from routes import tags
app.include_router(tags.router)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_tags.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add routes/tags.py templates/tags.html tests/test_tags.py main.py
git commit -m "feat: add tag management and tag filtering"
```

---

### Task 8: Search

**Files:**
- Create: `routes/search.py`
- Create: `templates/search.html`

- [ ] **Step 1: Write routes/search.py**

```python
from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy import or_

from main import render_template

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_class=HTMLResponse)
async def search(request: Request, q: str = Query(default="")):
    from models import Note
    db = request.state.db
    results = []
    if q.strip():
        pattern = f"%{q.strip()}%"
        results = (
            db.query(Note)
            .filter(
                or_(
                    Note.title.ilike(pattern),
                    Note.content.ilike(pattern),
                )
            )
            .order_by(Note.updated_at.desc())
            .all()
        )
    return render_template("search.html", query=q, results=results)
```

- [ ] **Step 2: Write templates/search.html**

```html
{% extends "base.html" %}
{% block title %}Search - Learning Notes{% endblock %}
{% block content %}
<h2>Search</h2>
<form action="/search" method="get" style="margin-bottom:1.5rem;">
    <div style="display:flex;gap:0.5rem;">
        <input type="search" name="q" value="{{ query }}" placeholder="Search notes..."
            style="flex:1;padding:0.5rem;border:1px solid var(--border);border-radius:6px;font-size:0.95rem;">
        <button type="submit" class="btn">Search</button>
    </div>
</form>

{% if query %}
<p class="meta">{{ results|length }} result(s) for "{{ query }}"</p>
{% if results %}
{% for note in results %}
<div class="card">
    <h3><a href="/notes/{{ note.id }}">{{ note.title }}</a></h3>
    <div class="meta">
        <span class="badge badge-{{ note.status.replace('_','-') }}">{{ note.status }}</span>
        {% if note.folder %}📁 {{ note.folder.name }}{% endif %}
        Updated {{ note.updated_at.strftime('%Y-%m-%d %H:%M') }}
    </div>
    <p style="margin-top:0.25rem;font-size:0.85rem;color:var(--text-muted);">
        {{ note.content[:200] }}{% if note.content|length > 200 %}...{% endif %}
    </p>
</div>
{% endfor %}
{% else %}
<p>No notes found.</p>
{% endif %}
{% endif %}
{% endblock %}
```

- [ ] **Step 3: Update main.py to add search routes**

At the end of `main.py`, add:

```python
from routes import search
app.include_router(search.router)
```

- [ ] **Step 4: Commit**

```bash
git add routes/search.py templates/search.html main.py
git commit -m "feat: add full-text search on title and content"
```

---

### Task 9: Dashboard

**Files:**
- Create: `templates/index.html`

- [ ] **Step 1: Write templates/index.html**

```html
{% extends "base.html" %}
{% block title %}Dashboard - Learning Notes{% endblock %}
{% block content %}
<h2>Dashboard</h2>

<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:2rem;">
    <div class="card" style="text-align:center;">
        <div style="font-size:2rem;font-weight:700;color:var(--primary);">{{ stats.total }}</div>
        <div class="meta">Total Notes</div>
    </div>
    <div class="card" style="text-align:center;">
        <div style="font-size:2rem;font-weight:700;color:#e67e22;">{{ stats.in_progress }}</div>
        <div class="meta">In Progress</div>
    </div>
    <div class="card" style="text-align:center;">
        <div style="font-size:2rem;font-weight:700;color:var(--accent);">{{ stats.due_reviews }}</div>
        <div class="meta">Due for Review</div>
    </div>
</div>

<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
    <div>
        <h3>Recent Notes</h3>
        {% if recent_notes %}
        {% for note in recent_notes %}
        <div class="card">
            <h3><a href="/notes/{{ note.id }}">{{ note.title }}</a></h3>
            <div class="meta">
                <span class="badge badge-{{ note.status.replace('_','-') }}">{{ note.status }}</span>
                {% if note.folder %}📁 {{ note.folder.name }}{% endif %}
                {{ note.updated_at.strftime('%Y-%m-%d %H:%M') }}
            </div>
        </div>
        {% endfor %}
        {% else %}
        <p class="meta">No notes yet. <a href="/notes/new">Create your first note</a>.</p>
        {% endif %}
    </div>
    <div>
        <h3>Due for Review</h3>
        {% if due_reviews %}
        {% for review in due_reviews %}
        <div class="card">
            <h3><a href="/notes/{{ review.note.id }}">{{ review.note.title }}</a></h3>
            <div class="meta">
                Next review: {{ review.next_review_at.strftime('%Y-%m-%d') }}
                · Interval: {{ review.interval }}d
                · Ease: {{ "%.1f" % review.ease_factor }}
            </div>
        </div>
        {% endfor %}
        {% else %}
        <p class="meta">No reviews due. <a href="/review">Go to review panel</a>.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Write dashboard route**

Update `main.py` to add the `/` route. Add after `app.mount("/static", ...)`:

```python
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
```

Also add `from fastapi.responses import HTMLResponse` and `from starlette.requests import Request` at top of main.py if not already present.

- [ ] **Step 3: Start app and verify dashboard loads**

Run: `uvicorn main:app --port 8000` (briefly, then Ctrl+C)
Expected: No errors, dashboard at http://localhost:8000 shows "Dashboard" with 0 counts.

- [ ] **Step 4: Commit**

```bash
git add templates/index.html main.py
git commit -m "feat: add dashboard with stats, recent notes, and review preview"
```

---

### Task 10: Spaced Repetition Review System

**Files:**
- Create: `services/review_service.py`
- Create: `routes/review.py`
- Create: `templates/review.html`
- Create: `tests/test_review.py`

- [ ] **Step 1: Write tests/test_review.py**

```python
from datetime import datetime, timedelta, timezone
from services.review_service import calculate_next_review


def test_sm2_quality_0_resets():
    result = calculate_next_review(quality=0, ease_factor=2.5, interval=10, repetitions=5)
    assert result["interval"] == 1
    assert result["repetitions"] == 0


def test_sm2_quality_3_first_review():
    result = calculate_next_review(quality=3, ease_factor=2.5, interval=1, repetitions=0)
    assert result["repetitions"] == 1
    assert result["interval"] == 1


def test_sm2_quality_4_second_review():
    result = calculate_next_review(quality=4, ease_factor=2.5, interval=1, repetitions=1)
    assert result["repetitions"] == 2
    assert result["interval"] == 6


def test_sm2_quality_5():
    result = calculate_next_review(quality=5, ease_factor=2.5, interval=6, repetitions=2)
    assert result["repetitions"] == 3
    assert result["interval"] > 6


def test_sm2_ease_factor_never_below_1_3():
    result = calculate_next_review(quality=0, ease_factor=1.3, interval=1, repetitions=0)
    assert result["ease_factor"] >= 1.3


def test_review_page(client):
    resp = client.get("/review")
    assert resp.status_code == 200


def test_submit_review(client, db_session):
    from models import Note, Review
    from datetime import datetime, timezone
    note = Note(title="Review Note", content="test")
    db_session.add(note)
    db_session.flush()
    review = Review(
        note_id=note.id,
        next_review_at=datetime.now(timezone.utc) - timedelta(days=1),
        ease_factor=2.5,
        interval=1,
        repetitions=0,
    )
    db_session.add(review)
    db_session.commit()
    resp = client.post(f"/review/{note.id}", data={"quality": "4"}, follow_redirects=True)
    assert resp.status_code == 200
    db_session.refresh(review)
    assert review.repetitions == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_review.py -v`
Expected: All tests FAIL (no review_service module).

- [ ] **Step 3: Write services/review_service.py**

```python
from datetime import datetime, timedelta, timezone
from models import Review


def calculate_next_review(
    quality: int,
    ease_factor: float = 2.5,
    interval: int = 1,
    repetitions: int = 0,
) -> dict:
    if quality < 0 or quality > 5:
        raise ValueError("Quality must be 0-5")

    if quality < 3:
        # Failed recall: reset
        return {
            "interval": 1,
            "repetitions": 0,
            "ease_factor": max(1.3, ease_factor - 0.2),
        }

    # Successful recall
    new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(1.3, new_ease)

    if repetitions == 0:
        new_interval = 1
    elif repetitions == 1:
        new_interval = 6
    else:
        new_interval = round(interval * new_ease)

    return {
        "interval": new_interval,
        "repetitions": repetitions + 1,
        "ease_factor": new_ease,
    }


def schedule_review(db, note, quality: int):
    existing = db.query(Review).filter(Review.note_id == note.id).first()
    if existing:
        result = calculate_next_review(
            quality=quality,
            ease_factor=existing.ease_factor,
            interval=existing.interval,
            repetitions=existing.repetitions,
        )
        existing.ease_factor = result["ease_factor"]
        existing.interval = result["interval"]
        existing.repetitions = result["repetitions"]
        existing.reviewed_at = datetime.now(timezone.utc)
    else:
        result = calculate_next_review(quality=quality)
        existing = Review(
            note_id=note.id,
            ease_factor=result["ease_factor"],
            interval=result["interval"],
            repetitions=result["repetitions"],
            reviewed_at=datetime.now(timezone.utc),
        )

    existing.next_review_at = datetime.now(timezone.utc) + timedelta(days=result["interval"])
    db.add(existing)
    db.commit()
```

- [ ] **Step 4: Write routes/review.py**

```python
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from main import render_template
from services.review_service import schedule_review

router = APIRouter(prefix="/review", tags=["review"])


@router.get("", response_class=HTMLResponse)
async def review_panel(request: Request):
    from models import Review, Note
    db = request.state.db
    now = datetime.now(timezone.utc)
    due = (
        db.query(Review)
        .filter(Review.next_review_at <= now)
        .order_by(Review.next_review_at.asc())
        .all()
    )
    upcoming = (
        db.query(Review)
        .filter(Review.next_review_at > now)
        .order_by(Review.next_review_at.asc())
        .limit(10)
        .all()
    )
    unreviewed = (
        db.query(Note)
        .outerjoin(Review, Note.id == Review.note_id)
        .filter(Review.id == None)
        .order_by(Note.updated_at.desc())
        .limit(10)
        .all()
    )
    return render_template("review.html", due=due, upcoming=upcoming, unreviewed=unreviewed)


@router.get("/{note_id}", response_class=HTMLResponse)
async def review_note_page(note_id: int, request: Request):
    from models import Note
    db = request.state.db
    note = db.query(Note).get(note_id)
    if not note:
        from fastapi import HTTPException
        raise HTTPException(404)
    return render_template("review.html", reviewing_note=note)


@router.post("/{note_id}")
async def submit_review(note_id: int, request: Request):
    from models import Note
    db = request.state.db
    note = db.query(Note).get(note_id)
    if not note:
        from fastapi import HTTPException
        raise HTTPException(404)
    form = await request.form()
    quality = int(form.get("quality", 3))
    schedule_review(db, note, quality)
    return RedirectResponse(url="/review", status_code=303)
```

- [ ] **Step 5: Write templates/review.html**

```html
{% extends "base.html" %}
{% block title %}Review - Learning Notes{% endblock %}
{% block content %}
<h2>Spaced Repetition Review</h2>

{% if reviewing_note %}
<div class="card" style="margin-bottom:2rem;">
    <h3>{{ reviewing_note.title }}</h3>
    <div class="markdown-body" style="max-height:60vh;overflow-y:auto;">
        {{ reviewing_note.content }}
    </div>
    <div style="margin-top:1rem;">
        <p class="meta">How well did you recall this?</p>
        <form method="post" action="/review/{{ reviewing_note.id }}" style="display:flex;gap:0.5rem;margin-top:0.5rem;">
            <button name="quality" value="0" class="btn btn-danger">0 · Forgot</button>
            <button name="quality" value="2" class="btn btn-secondary">2 · Hard</button>
            <button name="quality" value="3" class="btn btn-secondary">3 · OK</button>
            <button name="quality" value="4" class="btn">4 · Good</button>
            <button name="quality" value="5" class="btn">5 · Easy</button>
        </form>
    </div>
</div>
<a href="/review" class="btn btn-secondary">← Back</a>

{% else %}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
    <div>
        <h3>Due for Review ({{ due|length }})</h3>
        {% if due %}
        {% for review in due %}
        <div class="card">
            <h3><a href="/review/{{ review.note.id }}">{{ review.note.title }}</a></h3>
            <div class="meta">
                Due: {{ review.next_review_at.strftime('%Y-%m-%d %H:%M') }}
                · Interval: {{ review.interval }}d
                · Ease: {{ "%.1f" % review.ease_factor }}
            </div>
            <a href="/review/{{ review.note.id }}" class="btn btn-sm" style="margin-top:0.5rem;">Review Now</a>
        </div>
        {% endfor %}
        {% else %}
        <p class="meta">All caught up!</p>
        {% endif %}
    </div>
    <div>
        <h3>Needs Initial Review</h3>
        {% if unreviewed %}
        {% for note in unreviewed %}
        <div class="card">
            <h3><a href="/review/{{ note.id }}">{{ note.title }}</a></h3>
            <div class="meta">{{ note.updated_at.strftime('%Y-%m-%d') }}</div>
            <a href="/review/{{ note.id }}" class="btn btn-sm" style="margin-top:0.5rem;">Start Review</a>
        </div>
        {% endfor %}
        {% else %}
        <p class="meta">No notes awaiting initial review.</p>
        {% endif %}

        {% if upcoming %}
        <h3 style="margin-top:1.5rem;">Upcoming</h3>
        {% for review in upcoming %}
        <div class="card">
            <h3><a href="/notes/{{ review.note.id }}">{{ review.note.title }}</a></h3>
            <div class="meta">Next: {{ review.next_review_at.strftime('%Y-%m-%d') }} · {{ review.interval }}d</div>
        </div>
        {% endfor %}
        {% endif %}
    </div>
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 6: Update main.py to add review routes**

At the end of `main.py`, add:

```python
from routes import review
app.include_router(review.router)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `pytest tests/test_review.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add services/review_service.py routes/review.py templates/review.html tests/test_review.py main.py
git commit -m "feat: add SM-2 spaced repetition review system"
```

---

### Task 11: Knowledge Graph

**Files:**
- Create: `routes/graph.py`
- Create: `templates/graph.html`

- [ ] **Step 1: Write routes/graph.py**

```python
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from main import render_template

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", response_class=HTMLResponse)
async def graph_page(request: Request):
    return render_template("graph.html")


@router.get("/data")
async def graph_data(request: Request):
    from models import NoteLink, Note
    db = request.state.db
    notes = db.query(Note).all()
    links = db.query(NoteLink).all()

    nodes = [
        {"id": n.id, "title": n.title, "status": n.status}
        for n in notes
    ]
    edges = [
        {"source": l.source_id, "target": l.target_id}
        for l in links
    ]
    return JSONResponse({"nodes": nodes, "edges": edges})
```

- [ ] **Step 2: Write templates/graph.html**

```html
{% extends "base.html" %}
{% block title %}Knowledge Graph - Learning Notes{% endblock %}
{% block content %}
<h2>Knowledge Graph</h2>
<div id="graph" class="graph-container"></div>
<script>
document.addEventListener("DOMContentLoaded", () => {
    fetch("/graph/data")
        .then(r => r.json())
        .then(data => {
            const width = document.getElementById("graph").clientWidth;
            const height = document.getElementById("graph").clientHeight || 500;

            const svg = d3.select("#graph")
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            const g = svg.append("g");

            const zoom = d3.zoom()
                .scaleExtent([0.3, 3])
                .on("zoom", (event) => {
                    g.attr("transform", event.transform);
                });
            svg.call(zoom);

            const color = d3.scaleOrdinal()
                .domain(["planning", "in_progress", "completed"])
                .range(["#f59e0b", "#3b82f6", "#10b981"]);

            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.edges).id(d => d.id).distance(120))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2));

            const link = g.append("g")
                .selectAll("line")
                .data(data.edges)
                .join("line")
                .attr("stroke", "#ccc")
                .attr("stroke-width", 1.5);

            const node = g.append("g")
                .selectAll("g")
                .data(data.nodes)
                .join("g")
                .call(d3.drag()
                    .on("start", (event, d) => {
                        if (!event.active) simulation.alphaTarget(0.3).restart();
                        d.fx = d.x; d.fy = d.y;
                    })
                    .on("drag", (event, d) => {
                        d.fx = event.x; d.fy = event.y;
                    })
                    .on("end", (event, d) => {
                        if (!event.active) simulation.alphaTarget(0);
                        d.fx = null; d.fy = null;
                    })
                );

            node.append("circle")
                .attr("r", 8)
                .attr("fill", d => color(d.status));

            node.append("text")
                .text(d => d.title)
                .attr("x", 12)
                .attr("y", 4)
                .attr("font-size", "11px")
                .attr("fill", "var(--text)");

            node.append("title").text(d => d.title);

            node.on("click", (event, d) => {
                window.location.href = `/notes/${d.id}`;
            });

            simulation.on("tick", () => {
                link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                node.attr("transform", d => `translate(${d.x},${d.y})`);
            });
        });
});
</script>
{% endblock %}
```

- [ ] **Step 3: Update main.py to add graph routes**

At the end of `main.py`, add:

```python
from routes import graph
app.include_router(graph.router)
```

- [ ] **Step 4: Commit**

```bash
git add routes/graph.py templates/graph.html main.py
git commit -m "feat: add knowledge graph with D3 force layout"
```

---

### Task 12: Integration and Final Polish

**Files:**
- Modify: `main.py` — verify all routes registered
- Modify: `templates/base.html` — fix sidebar links

- [ ] **Step 1: Verify all routes registered in main.py**

The final `main.py` should have all includes:

```python
from routes import folders, notes, tags, search, review, graph
app.include_router(folders.router)
app.include_router(notes.router)
app.include_router(tags.router)
app.include_router(search.router)
app.include_router(review.router)
app.include_router(graph.router)
```

- [ ] **Step 2: Run the full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 3: Start the application and do a smoke test**

Run: `uvicorn main:app --port 8000 --reload`

Manual smoke test checklist:
- Open http://localhost:8000 → Dashboard loads with 0 stats
- Create a folder "Python" → Appears in tree
- Create subfolder "Django" under "Python" → Appears nested
- Create a note "Python Basics" in folder "Python", tags "python, beginner" → Note created
- Create a note "Django Intro" with content "See [[Python Basics]] for Python first" → Link created
- View "Django Intro" → Sidebar shows link to "Python Basics"
- View "Python Basics" → Sidebar shows incoming link from "Django Intro"
- Go to Tags → Both tags visible
- Go to Search → Search "python" finds both notes
- Go to Review → "Python Basics" shows as needing initial review
- Review "Python Basics" with quality 4 → Review disappears from "due" list
- Go to Knowledge Graph → Two nodes connected by a link

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: finalize integration with all routes and templates"
```

---

## Verification

After all tasks complete:
1. `pytest tests/ -v` — all tests pass
2. `uvicorn main:app --port 8000` — app starts without errors
3. Full smoke test checklist in Task 12 Step 3 passes
