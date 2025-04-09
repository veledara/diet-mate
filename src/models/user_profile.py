from sqlalchemy import Column, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base
from enum import Enum as PyEnum


class Gender(PyEnum):
    MALE = "male"
    FEMALE = "female"

    @property
    def display_name(self):
        if self == Gender.MALE:
            return "Мужской"
        elif self == Gender.FEMALE:
            return "Женский"


class ActivityLevel(PyEnum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTRA_ACTIVE = "extra_active"

    @property
    def display_name(self):
        if self == ActivityLevel.SEDENTARY:
            return "Минимальная активность"
        elif self == ActivityLevel.LIGHTLY_ACTIVE:
            return "Небольшая активность"
        elif self == ActivityLevel.MODERATELY_ACTIVE:
            return "Умеренная активность"
        elif self == ActivityLevel.VERY_ACTIVE:
            return "Высокая активность"
        elif self == ActivityLevel.EXTRA_ACTIVE:
            return "Экстремальная активность"


class Goal(PyEnum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN_WEIGHT = "maintain_weight"
    GAIN_WEIGHT = "gain_weight"

    @property
    def display_name(self):
        if self == Goal.LOSE_WEIGHT:
            return "Похудеть"
        elif self == Goal.MAINTAIN_WEIGHT:
            return "Поддерживать вес"
        elif self == Goal.GAIN_WEIGHT:
            return "Набрать вес"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    gender = Column(Enum(Gender), nullable=False)
    height = Column(Integer, nullable=False)  # в сантиметрах
    weight = Column(Float, nullable=False)  # в килограммах
    age = Column(Integer, nullable=False)  # в годах
    activity_level = Column(Enum(ActivityLevel), nullable=False)
    goal = Column(Enum(Goal), nullable=False)
    target_weight = Column(Float, nullable=True) # в килограммах

    user = relationship("User", back_populates="profile")
    nutrition = relationship(
        "UserNutrition", uselist=False, back_populates="user_profile"
    )
