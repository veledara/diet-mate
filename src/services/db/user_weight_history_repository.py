from typing import List
from sqlalchemy import select, desc

from src.services.db.database import async_session
from src.models.user_weight_history import UserWeightHistory


async def create_weight_record(user_id: int, weight: float) -> UserWeightHistory:
    """
    Создаёт новую запись изменения веса для пользователя user_id.
    Возвращает созданный объект.
    """
    async with async_session() as session:
        record = UserWeightHistory(user_id=user_id, weight=weight)
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


async def get_weight_history_by_user_id(
    user_id: int, limit: int = 10
) -> List[UserWeightHistory]:
    """
    Возвращает последние limit записей изменения веса для данного user_id,
    отсортированные по дате (самые свежие – первыми).
    """
    async with async_session() as session:
        stmt = (
            select(UserWeightHistory)
            .where(UserWeightHistory.user_id == user_id)
            .order_by(desc(UserWeightHistory.date_added))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()


async def get_first_record(user_id: int):
    """
    Возвращает самый первый зафиксированный вес пользователя, или None, если записей нет.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserWeightHistory)
            .where(UserWeightHistory.user_id == user_id)
            .order_by(UserWeightHistory.date_added.asc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        if row:
            return row.weight
        return None
