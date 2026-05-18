from datetime import datetime

from models import Folder, Note, Tag, NoteTag, NoteLink, Review


def test_create_folder(db_session):
    folder = Folder(name="Python")
    db_session.add(folder)
    db_session.commit()
    assert folder.id is not None
    assert folder.name == "Python"


def test_folder_hierarchy(db_session):
    root = Folder(name="Programming")
    db_session.add(root)
    db_session.flush()
    child = Folder(name="Python", parent_id=root.id)
    db_session.add(child)
    db_session.commit()
    assert child.parent_id == root.id
    assert child.parent.name == "Programming"


def test_create_note(db_session):
    note = Note(title="Test", content="# Hello", status="planning")
    db_session.add(note)
    db_session.commit()
    assert note.id is not None
    assert note.created_at is not None
    assert note.updated_at is not None


def test_note_in_folder(db_session):
    folder = Folder(name="Python")
    db_session.add(folder)
    db_session.flush()
    note = Note(title="Variables", content="# Vars", folder_id=folder.id)
    db_session.add(note)
    db_session.commit()
    assert note.folder == folder
    assert folder.notes[0] == note


def test_note_statuses(db_session):
    for status in ("planning", "in_progress", "completed"):
        note = Note(title=status, content="test", status=status)
        db_session.add(note)
    db_session.commit()
    assert db_session.query(Note).count() == 3


def test_tag_note_association(db_session):
    note = Note(title="Test", content="test")
    tag = Tag(name="python")
    db_session.add_all([note, tag])
    db_session.flush()
    note_tag = NoteTag(note_id=note.id, tag_id=tag.id)
    db_session.add(note_tag)
    db_session.commit()
    assert len(note.tags) == 1
    assert note.tags[0].tag.name == "python"
    assert len(tag.notes) == 1


def test_note_links(db_session):
    note1 = Note(title="Python", content="Python basics")
    note2 = Note(title="Django", content="Django web framework")
    db_session.add_all([note1, note2])
    db_session.flush()
    link = NoteLink(source_id=note1.id, target_id=note2.id)
    db_session.add(link)
    db_session.commit()
    assert len(note1.outgoing_links) == 1
    assert note1.outgoing_links[0].target == note2
    assert len(note2.incoming_links) == 1


def test_review_record(db_session):
    note = Note(title="Review me", content="test")
    db_session.add(note)
    db_session.flush()
    review = Review(
        note_id=note.id,
        reviewed_at=datetime(2026, 5, 18),
        next_review_at=datetime(2026, 5, 19),
        ease_factor=2.5,
        interval=1,
        repetitions=1,
    )
    db_session.add(review)
    db_session.commit()
    assert review.note == note
    assert note.review_record.ease_factor == 2.5


def test_delete_note_cascades(db_session):
    note = Note(title="Test", content="test")
    tag = Tag(name="python")
    db_session.add_all([note, tag])
    db_session.flush()
    nt = NoteTag(note_id=note.id, tag_id=tag.id)
    link = NoteLink(source_id=note.id, target_id=note.id)
    review = Review(note_id=note.id, next_review_at=datetime(2026, 5, 19))
    db_session.add_all([nt, link, review])
    db_session.commit()
    db_session.delete(note)
    db_session.commit()
    assert db_session.query(NoteTag).count() == 0
    assert db_session.query(NoteLink).count() == 0
    assert db_session.query(Review).count() == 0
