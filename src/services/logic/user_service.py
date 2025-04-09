from src.services.db.user_repository import (
    get_user_by_telegram_id as repo_get_user_by_telegram_id,
    create_user as repo_create_user,
    accept_user_agreement_by_telegram_id as repo_accept_user_agreement_by_telegram_id,
)
from src.models.user import User


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    """
    Получает пользователя по telegram_id.
    """
    return await repo_get_user_by_telegram_id(telegram_id)


async def register_new_user(telegram_id: int, username: str) -> User:
    """
    Регистрирует пользователя по telegram_id.
    """
    existing_user = await repo_get_user_by_telegram_id(telegram_id)
    if existing_user:
        return existing_user
    new_user = await repo_create_user(telegram_id, username)
    return new_user


async def accept_user_agreement(telegram_id: int) -> bool:
    """
    Проверяет, принял ли пользователь соглашение.
    """
    return await repo_accept_user_agreement_by_telegram_id(telegram_id)
