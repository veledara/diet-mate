from fastapi import Response, Query
from datetime import datetime

from src.services.logic.nutrition_service import (
    get_user_nutrition_by_telegram_id,
    get_user_profile_by_telegram_id,
)
from src.services.logic.user_food_log_service import (
    get_last_food_logs_by_telegram_user_id,
)
from src.services.logic.user_weight_history_service import (
    get_weight_history_by_telegram_id,
)


async def user_report(
    telegram_id: int = Query(..., description="Telegram user ID")
) -> Response:
    """
    Генерирует текстовый отчёт, содержащий:
     - Профиль
     - Суточную норму
     - Список приемов пищи
     - Историю веса
    Возвращает файл .txt.
    """
    profile = await get_user_profile_by_telegram_id(telegram_id)

    nutrition = await get_user_nutrition_by_telegram_id(telegram_id)

    food_logs = await get_last_food_logs_by_telegram_user_id(telegram_id, limit=10)

    weight_records = await get_weight_history_by_telegram_id(telegram_id, limit=100)

    lines = []
    lines.append("Отчет:\n")

    if profile:
        lines.append("=== ПРОФИЛЬ ===")
        lines.append(f"Пол: {profile.gender.name}")
        lines.append(f"Рост: {profile.height} см")
        lines.append(f"Вес: {profile.weight} кг")
        lines.append(f"Возраст: {profile.age}")
        lines.append(f"Уровень активности: {profile.activity_level.name}")
        lines.append(f"Цель: {profile.goal.name}")
        if profile.target_weight:
            lines.append(f"Целевой вес: {profile.target_weight} кг")
        lines.append("")

    if nutrition:
        lines.append("=== РАСЧЁТНЫЕ ПАРАМЕТРЫ ПИТАНИЯ ===")
        lines.append(f"Калории: {nutrition.calories:.1f}")
        lines.append(f"Белки: {nutrition.proteins:.1f} г")
        lines.append(f"Жиры: {nutrition.fats:.1f} г")
        lines.append(f"Углеводы: {nutrition.carbohydrates:.1f} г")
        lines.append("")

    if food_logs:
        lines.append("=== ПРИЕМЫ ПИЩИ ===")
        for fl in food_logs:
            dt_str = fl.date_added.strftime("%Y-%m-%d %H:%M")
            lines.append(f"{dt_str} | {fl.food_name} | {fl.calories} ккал")
        lines.append("")

    if weight_records:
        lines.append("=== ИСТОРИЯ ВЕСА ===")
        for wr in weight_records:
            lines.append(
                f"{wr.date_added.strftime('%Y-%m-%d %H:%M')} -> {wr.weight} кг"
            )
        lines.append("")

    report_text = "\n".join(lines)

    filename = f"report_{telegram_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=report_text, media_type="text/plain", headers=headers)
