from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base


class UserNutrition(Base):
    __tablename__ = "user_nutrition"

    id = Column(Integer, primary_key=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id"), unique=True)
    calories = Column(Float, nullable=False)
    proteins = Column(Float, nullable=False)
    fats = Column(Float, nullable=False)
    carbohydrates = Column(Float, nullable=False)

    user_profile = relationship("UserProfile", back_populates="nutrition")
