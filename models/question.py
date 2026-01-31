from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship

from database import Base
from util.utils import now_kst_naive

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=False)

    axis_key = Column(String(64), nullable=False)
    question_text = Column(Text, nullable=False)
    choice_a = Column(String(255), nullable=False)
    choice_b = Column(String(255), nullable=False)
    value_a_key = Column(String(64), nullable=True)
    value_b_key = Column(String(64), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=now_kst_naive, nullable=False)
    updated_at = Column(DateTime, default=now_kst_naive, onupdate=now_kst_naive, nullable=False)

    # 관계
    answers = relationship("Answer", back_populates="question")
