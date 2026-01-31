from sqlalchemy import Column, Integer, String, Text, DateTime

from database import Base
from util.utils import now_kst_naive

class PsanoState(Base):
    __tablename__ = "psano_state"

    id = Column(Integer, primary_key=True)

    current_phase = Column(String(20), nullable=False, default="teach")
    current_question = Column(Integer, nullable=False, default=1)

    # 대화기 전환 후 "자아 프롬프트" 저장(옵션)
    persona_prompt = Column(Text, nullable=True)

    # 글로벌 대화 턴 카운터 (talk phase)
    global_turn_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=now_kst_naive, nullable=False)
    updated_at = Column(DateTime, default=now_kst_naive, onupdate=now_kst_naive, nullable=False)