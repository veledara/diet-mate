from typing import List
from sqlalchemy import select
from datetime import datetime

from src.models.user_achievement import UserAchievement
from src.services.db.database import async_session


async def get_user_achievements(user_id: int) -> List[UserAchievement]:
    """
    Возвращает список достижений, которые получил пользователь.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
        )
        return result.scalars().all()


async def unlock_user_achievement(user_id: int, achievement_id: int) -> UserAchievement:
    """
    Создаёт запись о том, что пользователь получил достижение.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        new_ua = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=datetime.utcnow(),
        )
        session.add(new_ua)
        await session.commit()
        await session.refresh(new_ua)
        return new_ua
