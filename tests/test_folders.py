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
