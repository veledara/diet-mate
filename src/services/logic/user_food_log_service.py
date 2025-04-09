from datetime import datetime

from src.services.db.user_repository import get_user_by_telegram_id
from src.services.db.user_food_log_repository import (
    create_food_log,
    get_last_food_logs,
    update_food_save_status,
    get_food_logs_by_user_id_and_day,
)
from src.models.user_food_log import UserFoodLog


async def create_food_log_by_telegram_user_id(
    telegram_user_id: int, nutrition_info: dict, message_id: int, entry_uuid: str
) -> None:
    """
    Создает запись о приеме пищи по telegram_id
    """
    user = await get_user_by_telegram_id(telegram_user_id)
    if not user:
        raise ValueError("Пользователь не найден")

    await create_food_log(
        user_id=user.id,
        nutrition_info=nutrition_info,
        message_id=message_id,
        entry_uuid=entry_uuid,
    )


async def update_food_save_status_by_telegram_user_id(
    telegram_user_id: int, entry_uuid: str, action: str
) -> tuple[str, UserFoodLog]:
    """
    Переключает статус (is_saved) записи приема пищи (сохранение/удаление в дневник).
    """
    user = await get_user_by_telegram_id(telegram_user_id)
    if not user:
        raise ValueError("Пользователь не найден.")

    return await update_food_save_status(user.id, entry_uuid, action)


async def get_food_logs_by_telegram_user_id(telegram_user_id: int, day_start: datetime):
    """
    1. Ищем пользователя по telegram_user_id.
    2. Если нет - ошибка.
    3. Если есть, возвращаем сохранённые логи за период.
    """
    user = await get_user_by_telegram_id(telegram_user_id)
    if not user:
        raise ValueError("Пользователь не найден.")

    return await get_food_logs_by_user_id_and_day(user.id, day_start)


async def get_last_food_logs_by_telegram_user_id(
    telegram_user_id: int, limit: int = 10
):
    """
    1. Ищем пользователя по telegram_user_id.
    2. Если нет - ошибка.
    3. Если есть, возвращаем последние сохранённые логи.
    """
    user = await get_user_by_telegram_id(telegram_user_id)
    if not user:
        raise ValueError("Пользователь не найден.")

    return await get_last_food_logs(user.id, limit)
