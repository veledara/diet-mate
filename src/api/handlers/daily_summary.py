from fastapi import Query
from datetime import datetime, timezone

from src.api.schemas.daily_summary import DailySummaryResponse, FoodLogOut
from src.services.logic.nutrition_service import get_user_nutrition_by_telegram_id
from src.services.logic.daily_intake_service import get_and_calculate_daily_intake


async def daily_summary(
    telegram_id: int = Query(..., description="Telegram user ID")
) -> DailySummaryResponse:
    """
    Возвращает суммарную информацию (Сумму КБЖУ и приемы пищи) за сегодняшний день.
    """
    today = datetime.now(timezone.utc)
    day_start = datetime(today.year, today.month, today.day)

    calculation = await get_and_calculate_daily_intake(telegram_id, day_start)

    total_calories = calculation["calories"]
    total_proteins = calculation["proteins"]
    total_fats = calculation["fats"]
    total_carbohydrates = calculation["carbohydrates"]
    food_logs = calculation["food_logs"]

    food_logs_out = [FoodLogOut.model_validate(fl) for fl in food_logs]

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

    return DailySummaryResponse(
        total_calories=total_calories,
        total_proteins=total_proteins,
        total_fats=total_fats,
        total_carbohydrates=total_carbohydrates,
        food_logs=food_logs_out,
        user_nutrition=user_nutrition_dict,
    )
