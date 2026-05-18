from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, ForeignKey, create_engine,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

import config

Base = declarative_base()


class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    parent = relationship("Folder", remote_side=[id], back_populates="children")
    children = relationship("Folder", back_populates="parent", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="folder", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, default="")
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    status = Column(String(20), default="计划中")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    folder = relationship("Folder", back_populates="notes")
    tags = relationship("NoteTag", back_populates="note", cascade="all, delete-orphan")
    outgoing_links = relationship(
        "NoteLink", foreign_keys="NoteLink.source_id",
        back_populates="source", cascade="all, delete-orphan",
    )
    incoming_links = relationship(
        "NoteLink", foreign_keys="NoteLink.target_id",
        back_populates="target", cascade="all, delete-orphan",
    )
    review_record = relationship(
        "Review", back_populates="note", uselist=False, cascade="all, delete-orphan",
    )


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    notes = relationship("NoteTag", back_populates="tag", cascade="all, delete-orphan")


class NoteTag(Base):
    __tablename__ = "note_tags"
    __table_args__ = (UniqueConstraint("note_id", "tag_id"),)
    id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    note = relationship("Note", back_populates="tags")
    tag = relationship("Tag", back_populates="notes")


class NoteLink(Base):
    __tablename__ = "note_links"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    source = relationship("Note", foreign_keys=[source_id], back_populates="outgoing_links")
    target = relationship("Note", foreign_keys=[target_id], back_populates="incoming_links")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False, unique=True)
    reviewed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    next_review_at = Column(DateTime, nullable=False)
    ease_factor = Column(Float, default=2.5)
    interval = Column(Integer, default=1)
    repetitions = Column(Integer, default=0)
    note = relationship("Note", back_populates="review_record")


engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
