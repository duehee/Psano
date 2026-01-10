from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship

from database import Base

class TalkMessage(Base):
    __tablename__ = "talk_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)

    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)

    user_text = Column(Text, nullable=False)
    assistant_text = Column(Text, nullable=False)

    status = Column(Enum("ok", "fallback", "error", name="talk_status"), nullable=False, default="ok")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 관계
    session = relationship("Session", back_populates="talk_messages")