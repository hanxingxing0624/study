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
