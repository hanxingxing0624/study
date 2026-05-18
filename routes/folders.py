from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from main import render_template

router = APIRouter(prefix="/folders", tags=["folders"])


def build_tree(folders, parent_id=None):
    result = []
    for f in folders:
        if f.parent_id == parent_id:
            children = build_tree(folders, f.id)
            result.append({"folder": f, "children": children})
    return result


@router.get("", response_class=HTMLResponse)
async def list_folders(request: Request):
    from models import Folder
    db = request.state.db
    all_folders = db.query(Folder).order_by(Folder.name).all()
    tree = build_tree(all_folders)
    return render_template("folders.html", tree=tree, all_folders=all_folders)


@router.post("", response_class=HTMLResponse)
async def create_folder(request: Request):
    from models import Folder
    db = request.state.db
    form = await request.form()
    name = form.get("name", "").strip()
    parent_id = form.get("parent_id") or None
    if not name:
        all_folders = db.query(Folder).order_by(Folder.name).all()
        tree = build_tree(all_folders)
        return render_template("folders.html", tree=tree, all_folders=all_folders, error="Name is required")
    if parent_id:
        try:
            parent_id = int(parent_id)
        except (ValueError, TypeError):
            all_folders = db.query(Folder).order_by(Folder.name).all()
            tree = build_tree(all_folders)
            return render_template("folders.html", tree=tree, all_folders=all_folders, error="Invalid parent folder")
    folder = Folder(name=name, parent_id=parent_id)
    db.add(folder)
    db.commit()
    return RedirectResponse(url="/folders", status_code=303)


@router.get("/{folder_id}", response_class=HTMLResponse)
async def folder_detail(folder_id: int, request: Request):
    from models import Folder, Note
    db = request.state.db
    folder = db.get(Folder, folder_id)
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
    db = request.state.db
    folder = db.get(Folder, folder_id)
    if not folder:
        raise HTTPException(404)
    db.delete(folder)
    db.commit()
    return RedirectResponse(url="/folders", status_code=303)
