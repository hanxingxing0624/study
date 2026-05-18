from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException
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
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404)
    return render_template("review.html", reviewing_note=note)


@router.post("/{note_id}")
async def submit_review(note_id: int, request: Request):
    from models import Note
    db = request.state.db
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404)
    form = await request.form()
    quality = int(form.get("quality", 3))
    schedule_review(db, note, quality)
    return RedirectResponse(url="/review", status_code=303)
