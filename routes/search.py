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
