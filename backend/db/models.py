# backend/db/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class StockVideo(Base):
    __tablename__ = "stock_videos"

    id = Column(Integer, primary_key=True, index=True)
    channel_url = Column(String, nullable=False)
    channel_name = Column(String, nullable=False)
    video_id = Column(String, nullable=False, unique=True)
    video_title = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())

    mentions = relationship(
        "StockMention",
        back_populates="stock_video",
        cascade="all, delete-orphan",
    )


class StockMention(Base):
    __tablename__ = "stock_mentions"

    id = Column(Integer, primary_key=True, index=True)
    stock_video_id = Column(
        Integer, ForeignKey("stock_videos.id", ondelete="CASCADE"), nullable=False
    )
    stock_name = Column(String, nullable=False)
    sentiment = Column(String, nullable=False)  # positive / negative / neutral
    opinion = Column(Text, nullable=False)

    stock_video = relationship("StockVideo", back_populates="mentions")
