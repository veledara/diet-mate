from typing import List
from sqlalchemy import select

from src.models.achievement import Achievement
from src.services.db.database import async_session


async def get_all_achievements() -> List[Achievement]:
    """
    Возвращает все достижения из таблицы achievements.
    """
    async with async_session() as session:
        result = await session.execute(select(Achievement))
        return result.scalars().all()
