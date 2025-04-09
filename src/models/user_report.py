from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.models.base import Base
from datetime import datetime


class UserReport(Base):
    __tablename__ = "user_reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    report_type = Column(String(50))
    content = Column(Text)

    user = relationship("User", back_populates="reports")
