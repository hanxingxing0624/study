from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse

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
