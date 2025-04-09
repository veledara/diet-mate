from typing import Optional

from src.services.db.user_repository import get_user_by_telegram_id
from src.services.db.user_profile_repository import (
    get_user_profile_by_user_id,
    create_or_update_profile_by_user_id,
)
from src.services.db.user_nutrition_repository import (
    get_nutrition_by_profile_id,
    create_or_update_nutrition_by_profile_id,
)
from src.models.user_nutrition import UserNutrition


async def get_user_profile_by_telegram_id(
    telegram_user_id: int,
) -> Optional[UserNutrition]:
    """
    Сервисная функция: находит профиль по user_id,
    затем возвращает его профиль (параметры пользователя).
    """
    user = await get_user_by_telegram_id(telegram_user_id)
    if not user:
        return None

    profile = await get_user_profile_by_user_id(user.id)
    return profile


async def get_user_nutrition_by_telegram_id(
    telegram_user_id: int,
) -> Optional[UserNutrition]:
    """
    Сервисная функция: находит профиль по user_id,
    затем возвращает его суточную норму по profile_id.
    """
    user = await get_user_by_telegram_id(telegram_user_id)
    if not user:
        return None

    profile = await get_user_profile_by_user_id(user.id)
    if not profile:
        return None

    user_nutrition = await get_nutrition_by_profile_id(profile.id)
    return user_nutrition


async def create_or_update_profile_and_nutrition_by_telegram_id(
    telegram_id: int, profile_data: dict, nutrition_data: dict
) -> None:
    """
    Создает/обновляет пользовательский профиль и норму калорий по telegram_id
    """
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise ValueError("Пользователь не найден.")

    user_profile = await create_or_update_profile_by_user_id(
        user_id=user.id, profile_data=profile_data
    )

    await create_or_update_nutrition_by_profile_id(user_profile.id, nutrition_data)
