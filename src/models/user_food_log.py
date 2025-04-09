from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from src.models.base import Base
from datetime import datetime


class UserFoodLog(Base):
    __tablename__ = "user_food_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_name = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    proteins = Column(Float, nullable=False)
    fats = Column(Float, nullable=False)
    carbohydrates = Column(Float, nullable=False)
    fiber = Column(Float, nullable=True)
    amount = Column(Integer, nullable=False, default=100)
    date_added = Column(DateTime, default=datetime.now)
    is_saved = Column(Boolean, default=False)
    message_id = Column(Integer, nullable=False)
    entry_uuid = Column(String, nullable=False, unique=True)
    rating = Column(String, nullable=True)

    user = relationship("User", back_populates="food_logs")
