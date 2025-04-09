from typing import Optional
from sqlalchemy import select

from src.services.db.database import async_session
from src.models.user_nutrition import UserNutrition


async def get_nutrition_by_profile_id(profile_id: int) -> Optional[UserNutrition]:
    """
    Возвращает запись о суточной норме калорий UserNutrition по profile_id.
    Если не найдена, вернёт None.
    """
    async with async_session() as session:
        result_nutrition = await session.execute(
            select(UserNutrition).where(UserNutrition.user_profile_id == profile_id)
        )
        return result_nutrition.scalar_one_or_none()


async def create_or_update_nutrition_by_profile_id(
    profile_id: int, nutrition_data: dict
) -> UserNutrition:
    """
    Создаёт или обновляет суточную норму калорий по profile_id.
    Возвращает созданный/обновлённый UserNutrition.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserNutrition).where(UserNutrition.user_profile_id == profile_id)
        )
        existing_nutrition = result.scalar_one_or_none()

        if existing_nutrition:
            existing_nutrition.calories = nutrition_data["daily_calories"]
            existing_nutrition.proteins = nutrition_data["proteins"]
            existing_nutrition.fats = nutrition_data["fats"]
            existing_nutrition.carbohydrates = nutrition_data["carbohydrates"]

            await session.commit()
            await session.refresh(existing_nutrition)
            return existing_nutrition
        else:
            new_nutrition = UserNutrition(
                user_profile_id=profile_id,
                calories=nutrition_data["daily_calories"],
                proteins=nutrition_data["proteins"],
                fats=nutrition_data["fats"],
                carbohydrates=nutrition_data["carbohydrates"],
            )
            session.add(new_nutrition)
            await session.commit()
            await session.refresh(new_nutrition)
            return new_nutrition
