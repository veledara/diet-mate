from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import Base


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(Integer, ForeignKey("achievements.id"))
    unlocked_at = Column(DateTime, default=datetime.now)

    achievement = relationship("Achievement", back_populates="user_achievements")
