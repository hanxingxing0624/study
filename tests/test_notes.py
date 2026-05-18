import pytest


def test_new_note_page(client):
    resp = client.get("/notes/new")
    assert resp.status_code == 200
    assert "New Note" in resp.text or "Note" in resp.text


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
    assert "required" in resp.text.lower() or "title" in resp.text.lower()


def test_markdown_rendering(client, db_session):
    from models import Note
    note = Note(title="MD Test", content="# Heading\n\n```python\nprint(1)\n```")
    db_session.add(note)
    db_session.commit()
    resp = client.get(f"/notes/{note.id}")
    assert resp.status_code == 200
    assert "Heading" in resp.text
    assert "print" in resp.text


def test_wikilink_parsing(client, db_session):
    from models import Note
    note1 = Note(title="Python", content="Python basics")
    note2 = Note(title="Django", content="See [[Python]] for basics")
    db_session.add_all([note1, note2])
    db_session.commit()
    resp = client.get(f"/notes/{note2.id}")
    assert resp.status_code == 200
    assert f"/notes/{note1.id}" in resp.text
