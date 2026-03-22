# backend/db/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class Summary(Base):
    __tablename__ = "summaries"
    __table_args__ = (UniqueConstraint("youtube_url"),)

    id = Column(Integer, primary_key=True, index=True)
    youtube_url = Column(String, nullable=False, unique=True)
    video_title = Column(String, nullable=False)
    video_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())

    chapters = relationship("Chapter", back_populates="summary", cascade="all, delete-orphan", order_by="Chapter.order")

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    content = Column(String, nullable=False)
    order = Column(Integer, nullable=False)

    summary = relationship("Summary", back_populates="chapters")
