from datetime import datetime

from src.services.logic.user_food_log_service import get_food_logs_by_telegram_user_id


async def get_and_calculate_daily_intake(
    telegram_user_id: int, day_start: datetime
) -> dict:
    """
    Получает и считает сумму калорий и макронутриентов за день, возвращает вместе
    со списком приемов пищи.
    """
    food_logs = await get_food_logs_by_telegram_user_id(telegram_user_id, day_start)
    result = _calculate_daily_intake(food_logs)
    result["food_logs"] = food_logs
    return result


def create_progress_bar(current, total, length=10) -> str:
    """
    Создает графическое представление прогресса в виде полосы из эмодзи.
    """
    if total > 0:
        proportion = float(current) / float(total)
    else:
        proportion = 0

    filled_length = int(length * min(proportion, 1))
    bar = "🟩" * filled_length + "⬜️" * (length - filled_length)

    if proportion > 1:
        over_proportion = proportion - 1
        over_length = int(length * over_proportion)
        if over_length > length:
            over_length = length
        bar = "🟥" * over_length + bar[over_length:]
    percentage = int(proportion * 100)
    return f"{bar} {percentage}%"


def _calculate_daily_intake(food_logs: list) -> dict:
    total_calories = sum(fl.calories * fl.amount / 100 for fl in food_logs)
    total_proteins = sum(fl.proteins * fl.amount / 100 for fl in food_logs)
    total_fats = sum(fl.fats * fl.amount / 100 for fl in food_logs)
    total_carbs = sum(fl.carbohydrates * fl.amount / 100 for fl in food_logs)
    return {
        "calories": round(total_calories, 2),
        "proteins": round(total_proteins, 2),
        "fats": round(total_fats, 2),
        "carbohydrates": round(total_carbs, 2),
    }
