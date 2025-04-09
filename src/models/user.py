from sqlalchemy import Boolean, Column, Integer, BigInteger, String
from sqlalchemy.orm import relationship
from src.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    agreement_accepted = Column(Boolean, default=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    food_logs = relationship("UserFoodLog", back_populates="user")
    reports = relationship("UserReport", back_populates="user")
    weight_history = relationship("UserWeightHistory", back_populates="user")
