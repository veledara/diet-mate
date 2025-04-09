from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base


class UserWeightHistory(Base):
    __tablename__ = "user_weight_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight = Column(Float, nullable=False)
    date_added = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="weight_history")