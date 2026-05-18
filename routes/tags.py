from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from main import render_template

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_class=HTMLResponse)
async def list_tags(request: Request):
    from models import Tag
    db = request.state.db
    tags = db.query(Tag).order_by(Tag.name).all()
    tag_counts = []
    for tag in tags:
        count = len(tag.notes)
        tag_counts.append((tag, count))
    return render_template("tags.html", tag_counts=tag_counts)


@router.post("")
async def create_tag(request: Request):
    from models import Tag
    db = request.state.db
    form = await request.form()
    name = form.get("name", "").strip()
    if name:
        existing = db.query(Tag).filter(Tag.name == name).first()
        if not existing:
            tag = Tag(name=name)
            db.add(tag)
            db.commit()
    return RedirectResponse(url="/tags", status_code=303)


@router.post("/{tag_id}/rename")
async def rename_tag(tag_id: int, request: Request):
    from models import Tag
    db = request.state.db
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(404)
    form = await request.form()
    name = form.get("name", "").strip()
    if name:
        tag.name = name
        db.commit()
    return RedirectResponse(url="/tags", status_code=303)


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, request: Request):
    from models import Tag, NoteTag
    db = request.state.db
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(404)
    db.query(NoteTag).filter(NoteTag.tag_id == tag_id).delete()
    db.delete(tag)
    db.commit()
    return RedirectResponse(url="/tags", status_code=303)


@router.get("/{tag_id}", response_class=HTMLResponse)
async def tag_detail(tag_id: int, request: Request):
    from models import Tag
    db = request.state.db
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(404)
    notes = [nt.note for nt in tag.notes]
    notes.sort(key=lambda n: n.updated_at, reverse=True)
    return render_template("tags.html", tag=tag, notes=notes)
