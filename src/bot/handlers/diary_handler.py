import logging
from datetime import datetime, timezone
from aiogram import Router, types

from src.services.logic.user_food_log_service import (
    update_food_save_status_by_telegram_user_id,
)
from src.services.logic.daily_intake_service import (
    get_and_calculate_daily_intake,
    create_progress_bar,
)
from src.services.logic.nutrition_service import get_user_nutrition_by_telegram_id
from src.bot.keyboards.inline import save_food_button


logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(
    lambda c: c.data.startswith("save_food") or c.data.startswith("remove_food")
)
async def toggle_food_in_log(callback_query: types.CallbackQuery):
    """
    Обрабатывает сохранение и удаление из дневника.
    """
    data = callback_query.data.split("|")
    action = data[0]
    entry_uuid = data[1]
    telegram_user_id = callback_query.from_user.id

    try:
        message_text, food_log = await update_food_save_status_by_telegram_user_id(
            telegram_user_id, entry_uuid, action
        )

        new_action = "remove" if action == "save_food" else "add"
        await callback_query.message.edit_reply_markup(
            reply_markup=save_food_button(entry_uuid=entry_uuid, action=new_action)
        )
        await callback_query.message.answer(message_text)
        today = datetime.now(timezone.utc)
        day_start = datetime(today.year, today.month, today.day)

        calculation = await get_and_calculate_daily_intake(telegram_user_id, day_start)
        total_calories = calculation["calories"]
        total_proteins = calculation["proteins"]
        total_fats = calculation["fats"]
        total_carbs = calculation["carbohydrates"]
        food_logs = calculation["food_logs"]
        user_nutrition = await get_user_nutrition_by_telegram_id(telegram_user_id)

        if user_nutrition:
            calories_bar = create_progress_bar(total_calories, user_nutrition.calories)
            proteins_bar = create_progress_bar(total_proteins, user_nutrition.proteins)
            fats_bar = create_progress_bar(total_fats, user_nutrition.fats)
            carbs_bar = create_progress_bar(total_carbs, user_nutrition.carbohydrates)

            food_list = "\n".join([f"- {log.food_name}" for log in food_logs])
            await callback_query.message.answer(
                f"Сегодня вы потребили:\n"
                f"Калорий: {total_calories:.1f} из {user_nutrition.calories:.1f} ккал \n{calories_bar}\n"
                f"Белков: {total_proteins:.1f} г из {user_nutrition.proteins:.1f} г \n{proteins_bar}\n"
                f"Жиров: {total_fats:.1f} г из {user_nutrition.fats:.1f} г \n{fats_bar}\n"
                f"Углеводов: {total_carbs:.1f} г из {user_nutrition.carbohydrates:.1f} г \n{carbs_bar}\n\n"
                f"Список продуктов за сегодня:\n{food_list}"
            )
        else:
            await callback_query.message.answer("У вас не задана дневная норма КБЖУ.")
    except Exception as e:
        logger.error(f"Ошибка при переключении лога еды: {str(e)}")
        await callback_query.message.answer(str(e))

    await callback_query.answer()
