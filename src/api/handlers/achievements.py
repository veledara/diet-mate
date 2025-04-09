from fastapi import HTTPException, Query

from src.services.logic.achievements_service import check_and_unlock_achievements
from src.api.schemas.achievements import AchievementsResponse


async def achievements(
    telegram_id: int = Query(..., description="Telegram user ID")
) -> AchievementsResponse:
    """
    Возвращает список всех достижений с отметкой о том, какие из них пользователь разблокировал.
    """
    try:
        achievements_info = await check_and_unlock_achievements(telegram_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return AchievementsResponse(achievements=achievements_info)
