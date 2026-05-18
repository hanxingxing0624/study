from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from main import render_template
from services.markdown_service import render_markdown
from services.note_service import update_note_links, get_link_resolver

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/new", response_class=HTMLResponse)
async def new_note_page(request: Request):
    from models import Folder
    db = request.state.db
    folders = db.query(Folder).order_by(Folder.name).all()
    return render_template("note_edit.html", note=None, folders=folders)


@router.post("/new", response_class=HTMLResponse)
async def create_note(request: Request):
    from models import Note, Folder
    db = request.state.db
    form = await request.form()
    title = form.get("title", "").strip()
    content = form.get("content", "")
    status = form.get("status", "计划中")
    folder_id = form.get("folder_id") or None
    if folder_id:
        try:
            folder_id = int(folder_id)
        except (ValueError, TypeError):
            folder_id = None
    tags_str = form.get("tags", "").strip()

    if not title:
        folders = db.query(Folder).order_by(Folder.name).all()
        return render_template("note_edit.html", note=None, folders=folders, error="标题不能为空")

    note = Note(title=title, content=content, status=status, folder_id=folder_id)
    db.add(note)
    db.flush()

    if tags_str:
        _process_tags(db, note, tags_str)

    update_note_links(db, note)
    db.commit()
    return RedirectResponse(url=f"/notes/{note.id}", status_code=303)


@router.get("/{note_id}", response_class=HTMLResponse)
async def view_note(note_id: int, request: Request):
    from models import Note
    db = request.state.db
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404)
    resolver = get_link_resolver(db)
    html_content = render_markdown(note.content, resolver)
    return render_template("note_view.html", note=note, html_content=html_content)


@router.get("/{note_id}/edit", response_class=HTMLResponse)
async def edit_note_page(note_id: int, request: Request):
    from models import Note, Folder
    db = request.state.db
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404)
    folders = db.query(Folder).order_by(Folder.name).all()
    return render_template("note_edit.html", note=note, folders=folders)


@router.post("/{note_id}/edit", response_class=HTMLResponse)
async def update_note(note_id: int, request: Request):
    from models import Note, Folder
    db = request.state.db
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404)
    form = await request.form()
    title = form.get("title", "").strip()
    if not title:
        folders = db.query(Folder).order_by(Folder.name).all()
        return render_template("note_edit.html", note=note, folders=folders, error="标题不能为空")

    note.title = title
    note.content = form.get("content", "")
    note.status = form.get("status", "计划中")
    folder_id = form.get("folder_id") or None
    note.folder_id = int(folder_id) if folder_id else None

    tags_str = form.get("tags", "").strip()
    if tags_str:
        _process_tags(db, note, tags_str)

    update_note_links(db, note)
    db.commit()
    return RedirectResponse(url=f"/notes/{note.id}", status_code=303)


@router.delete("/{note_id}")
async def delete_note(note_id: int, request: Request):
    from models import Note
    db = request.state.db
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404)
    db.delete(note)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


def _process_tags(db, note, tags_str: str):
    from models import Tag, NoteTag
    tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
    db.query(NoteTag).filter(NoteTag.note_id == note.id).delete()
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        nt = NoteTag(note_id=note.id, tag_id=tag.id)
        db.add(nt)
