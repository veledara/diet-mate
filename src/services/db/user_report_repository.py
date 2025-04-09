from typing import Optional
from sqlalchemy import select

from src.models.user_report import UserReport
from src.services.db.database import async_session


async def сreate_user_report(
    user_id: int, report_type: str, content: str
) -> UserReport:
    """
    Создаёт новую запись отчёта пользователя и возвращает созданный объект UserReport.
    """
    async with async_session() as session:
        user_report = UserReport(
            user_id=user_id, report_type=report_type, content=content
        )
        session.add(user_report)
        await session.commit()
        await session.refresh(user_report)
        return user_report


async def get_last_user_report_by_type(
    user_id: int, report_type: str
) -> Optional[UserReport]:
    """
    Возвращает последний (по created_at) отчёт пользователя user_id с заданным report_type,
    или None, если таких нет.
    """
    async with async_session() as session:
        stmt = (
            select(UserReport)
            .where(UserReport.user_id == user_id)
            .where(UserReport.report_type == report_type)
            .order_by(UserReport.created_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
