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
