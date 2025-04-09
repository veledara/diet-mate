from sqlalchemy import select

from src.models.user import User
from src.services.db.database import async_session


async def get_user_by_telegram_id(telegram_id: int) -> User:
    """
    Возвращает пользователя по его telegram_id.
    """
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def create_user(telegram_id: int, username: str) -> User:
    """
    Создает и возвращает пользователя.
    """
    async with async_session() as session:
        user = User(
            telegram_id=telegram_id, username=username, agreement_accepted=False
        )
        session.add(user)
        await session.commit()
        return user


async def accept_user_agreement_by_telegram_id(telegram_id: int) -> bool:
    """
    Переключает принятие пользовательского соглашения.
    """
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if user and not user.agreement_accepted:
            user.agreement_accepted = True
            await session.commit()
            return True
        return False
