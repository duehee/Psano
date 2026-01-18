from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String
from sqlalchemy.orm import relationship

from database import Base

class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, autoincrement=True)

    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False)

    choice = Column(Enum("A", "B", name="answer_choice"), nullable=False)
    chosen_value_key = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 관계
    session = relationship("Session", back_populates="answers")
    question = relationship("Question", back_populates="answers")
