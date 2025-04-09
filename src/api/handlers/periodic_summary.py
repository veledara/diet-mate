from fastapi import Query
from datetime import datetime, timedelta, timezone

from src.api.schemas.periodic_summary import PeriodicSummaryResponse, DaySummaryOut
from src.services.logic.nutrition_service import get_user_nutrition_by_telegram_id
from src.services.logic.daily_intake_service import get_and_calculate_daily_intake


async def periodic_summary(
    telegram_id: int = Query(..., description="Telegram user ID"),
    days: int = Query(7, description="Сколько дней взять (например, 7 или 30)"),
) -> PeriodicSummaryResponse:
    """
    Возвращает суммарную информацию (Сумму КБЖУ и приемы пищи) за каждый из выбранных дней.
    Также возвращает средние значения (по дням, где есть хотя бы одна отметка).
    """
    user_nutrition_obj = await get_user_nutrition_by_telegram_id(telegram_id)
    if user_nutrition_obj:
        user_nutrition_dict = {
            "calories": user_nutrition_obj.calories,
            "proteins": user_nutrition_obj.proteins,
            "fats": user_nutrition_obj.fats,
            "carbohydrates": user_nutrition_obj.carbohydrates,
        }
    else:
        user_nutrition_dict = None

    today = datetime.now(timezone.utc)
    days_array = []

    sum_calories = 0.0
    sum_proteins = 0.0
    sum_fats = 0.0
    sum_carbohydrates = 0.0
    count_non_zero_days = 0

    for i in range(days):
        day_dt = today - timedelta(days=i)
        day_start = datetime(day_dt.year, day_dt.month, day_dt.day)

        calc = await get_and_calculate_daily_intake(telegram_id, day_start)
        total_calories = calc["calories"]
        total_proteins = calc["proteins"]
        total_fats = calc["fats"]
        total_carbohydrates = calc["carbohydrates"]
        food_logs = calc["food_logs"]

        if total_calories > 0:
            count_non_zero_days += 1
            sum_calories += total_calories
            sum_proteins += total_proteins
            sum_fats += total_fats
            sum_carbohydrates += total_carbohydrates

        day_summary = DaySummaryOut(
            date=day_start.date(),
            total_calories=total_calories,
            total_proteins=total_proteins,
            total_fats=total_fats,
            total_carbohydrates=total_carbohydrates,
            food_logs=food_logs,
        )
        days_array.append(day_summary)

    days_array.sort(key=lambda x: x.date)

    if count_non_zero_days > 0:
        avg_calories = sum_calories / count_non_zero_days
        avg_proteins = sum_proteins / count_non_zero_days
        avg_fats = sum_fats / count_non_zero_days
        avg_carbohydrates = sum_carbohydrates / count_non_zero_days
    else:
        avg_calories = 0.0
        avg_proteins = 0.0
        avg_fats = 0.0
        avg_carbohydrates = 0.0

    return PeriodicSummaryResponse(
        days=days_array,
        user_nutrition=user_nutrition_dict,
        average_calories=avg_calories,
        average_proteins=avg_proteins,
        average_fats=avg_fats,
        average_carbohydrates=avg_carbohydrates,
    )
