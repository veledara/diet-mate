from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.models.base import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)
    description = Column(String)
    icon_url = Column(String(255), nullable=True)

    user_achievements = relationship("UserAchievement", back_populates="achievement")
