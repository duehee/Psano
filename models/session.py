from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    visitor_name = Column(String(100), nullable=False)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    end_reason = Column(String(50), nullable=True)
    start_question_id = Column(Integer, nullable=True)

    # idle-based talk
    idle_id = Column(Integer, nullable=True)
    idle_talk_memory = Column(Text, nullable=True)
    idle_turn_count = Column(Integer, default=0, nullable=False)

    # 관계
    answers = relationship("Answer", back_populates="session", cascade="all, delete-orphan")