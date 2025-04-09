from src.models.user_report import UserReport
from src.services.db.user_nutrition_repository import get_nutrition_by_profile_id
from src.services.db.user_repository import get_user_by_telegram_id
from src.services.db.user_profile_repository import get_user_profile_by_user_id
from src.services.db.user_food_log_repository import get_last_food_logs
from src.services.db.user_report_repository import (
    get_last_user_report_by_type,
    сreate_user_report,
)
from src.services.logic.chat_gpt_service import ai_report


async def get_last_ai_report(telegram_id: int, report_type: str):
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise ValueError("Пользователь с таким telegram_id не найден")

    last_report = await get_last_user_report_by_type(user.id, report_type)

    return last_report


async def create_ai_report(
    telegram_id: int, report_type: str, limit: int = 10
) -> UserReport:
    """
    Сервисная функция, агрегирующая данные, необходимые для составления и генерации отчета.
    """
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise ValueError("Пользователь не найден.")

    user_profile = await get_user_profile_by_user_id(user.id)
    if not user_profile:
        raise ValueError("Не найден профиль пользователя")

    user_nutrition = await get_nutrition_by_profile_id(user_profile.id)
    if not user_nutrition:
        raise ValueError("Не найдена норма пользователя")

    food_logs = await get_last_food_logs(user.id, limit=15)
    if not food_logs:
        raise ValueError("У пользователя нет логов за последние 7 дней")

    food_logs = food_logs[:limit]

    report_content = await ai_report(
        user_profile=user_profile,
        user_nutrition=user_nutrition,
        food_logs=food_logs,
        report_type=report_type,
    )
    if not report_content:
        raise ValueError("Не удалось получить ответ от AI")

    saved_report = await сreate_user_report(
        user_id=user.id, report_type=report_type, content=report_content
    )

    return saved_report
