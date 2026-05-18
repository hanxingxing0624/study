from models import Note, NoteLink
from sqlalchemy.orm import Session
import re


def extract_wikilinks(content: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def update_note_links(db: Session, note: Note):
    db.query(NoteLink).filter(NoteLink.source_id == note.id).delete()
    titles = extract_wikilinks(note.content)
    for title in titles:
        target = db.query(Note).filter(Note.title == title).first()
        if target and target.id != note.id:
            link = NoteLink(source_id=note.id, target_id=target.id)
            db.add(link)
    db.commit()


def get_link_resolver(db: Session):
    def resolve(title: str) -> str | None:
        note = db.query(Note).filter(Note.title == title).first()
        if note:
            return f"/notes/{note.id}"
        return None
    return resolve
