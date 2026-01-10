from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base

class PsanoState(Base):
    __tablename__ = "psano_state"

    # 단일 레코드(항상 1)로 운영
    id = Column(Integer, primary_key=True)

    current_phase = Column(String(20), nullable=False, default="formation")
    current_question = Column(Integer, nullable=False, default=1)

    # 대화기 전환 후 "자아 프롬프트" 저장(옵션)
    persona_prompt = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)