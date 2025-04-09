from datetime import datetime, timedelta
from sqlalchemy import func, select

from src.services.db.database import async_session
from src.models.user_food_log import UserFoodLog


async def create_food_log(
    user_id: int, nutrition_info: dict, message_id: int, entry_uuid: str
) -> None:
    """
    Создаёт запись в UserFoodLog.
    """
    async with async_session() as session:
        food_log = UserFoodLog(
            user_id=user_id,
            food_name=nutrition_info["food"],
            calories=nutrition_info["calories"],
            proteins=nutrition_info["proteins"],
            fats=nutrition_info["fats"],
            carbohydrates=nutrition_info["carbohydrates"],
            fiber=nutrition_info.get("fiber"),
            amount=100,
            date_added=datetime.now(),
            is_saved=False,
            message_id=message_id,
            entry_uuid=entry_uuid,
            rating=nutrition_info.get("rating"),
        )
        session.add(food_log)
        await session.commit()


async def count_food_logs_for_user(user_id: int) -> int:
    """
    Количество сохранённых в дневник (is_saved=True) приемов пищи у пользователя.
    """
    async with async_session() as session:
        result = await session.execute(
            select(func.count(UserFoodLog.id)).where(
                UserFoodLog.user_id == user_id, UserFoodLog.is_saved == True
            )
        )
        return result.scalar() or 0


async def get_unique_dates_with_logs(user_id: int):
    """
    Возвращает список дат, где у пользователя есть хотя бы 1 сохранённый прием пищи.
    """
    async with async_session() as session:
        result = await session.execute(
            select(func.date(UserFoodLog.date_added))
            .where(UserFoodLog.user_id == user_id, UserFoodLog.is_saved == True)
            .group_by(func.date(UserFoodLog.date_added))
            .order_by(func.date(UserFoodLog.date_added).asc())
        )
        dates = [row[0] for row in result.all()]
        return dates


async def get_food_logs_by_user_id_and_day(user_id: int, day_start: datetime):
    """
    Возвращает все сохранённые в дневник (is_saved=True) приемы пищи,
    за день, для конкретного user_id.
    """
    day_end = day_start + timedelta(days=1)
    async with async_session() as session:
        result = await session.execute(
            select(UserFoodLog).where(
                UserFoodLog.user_id == user_id,
                UserFoodLog.is_saved == True,
                UserFoodLog.date_added >= day_start,
                UserFoodLog.date_added < day_end,
            )
        )
        return result.scalars().all()


async def get_last_food_logs(user_id: int, limit: int = 10):
    """
    Возвращает последние limit сохранённых записей приемов пищи для заданного user_id.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserFoodLog)
            .where(UserFoodLog.user_id == user_id, UserFoodLog.is_saved == True)
            .order_by(UserFoodLog.date_added.desc())
            .limit(limit)
        )
        return result.scalars().all()


async def update_food_save_status(
    user_id: int, entry_uuid: str, action: str
) -> tuple[str, UserFoodLog]:
    """
    Переключает статус сохранения лога еды (is_saved). Добавление/удаление из дневника.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserFoodLog).where(
                UserFoodLog.entry_uuid == entry_uuid, UserFoodLog.user_id == user_id
            )
        )
        food_log = result.scalar_one_or_none()
        if not food_log:
            raise ValueError("Информация не найдена.")

        if action == "save_food":
            if not food_log.is_saved:
                food_log.is_saved = True
                await session.commit()
                return f"{food_log.food_name} добавлено в ваш дневник!", food_log
            else:
                return "Эта еда уже добавлена в ваш дневник.", food_log

        elif action == "remove_food":
            if food_log.is_saved:
                food_log.is_saved = False
                await session.commit()
                return f"{food_log.food_name} удалено из вашего дневника.", food_log
            else:
                return "Эта еда уже удалена из вашего дневника.", food_log

        else:
            raise ValueError("Неизвестное действие.")
