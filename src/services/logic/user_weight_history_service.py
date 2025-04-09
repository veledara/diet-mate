from src.services.db.user_repository import get_user_by_telegram_id
from src.services.db.user_weight_history_repository import (
    create_weight_record,
    get_weight_history_by_user_id,
)


async def create_weight_record_by_telegram_id(telegram_id: int, new_weight: float):
    """
    Сохраняет новый вес пользователя, создавает запись в user_weight_history.
    """
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise ValueError("Пользователь с таким telegram_id не найден")
    record = await create_weight_record(user.id, new_weight)
    return record


async def get_weight_history_by_telegram_id(telegram_id: int, limit: int = 10):
    """
    Возвращает список последних изменений веса по telegram_id.
    """
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise ValueError("Пользователь с таким telegram_id не найден")
    return await get_weight_history_by_user_id(user.id, limit=limit)
