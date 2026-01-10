from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    visitor_name = Column(String(100), nullable=False)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    # 관계
    answers = relationship("Answer", back_populates="session", cascade="all, delete-orphan")
    talk_messages = relationship("TalkMessage", back_populates="session", cascade="all, delete-orphan")