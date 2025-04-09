from src.services.db.user_repository import get_user_by_telegram_id
from src.services.db.achievement_repository import get_all_achievements
from src.services.db.user_achievement_repository import (
    get_user_achievements,
    unlock_user_achievement,
)
from src.services.logic.achievement_checks import (
    has_started,
    has_discipline,
    has_halfway,
    has_winner,
)


async def check_and_unlock_achievements(telegram_id: int):
    """
    Проверяет получение пользователем достижений и возвращает их список.
    """
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        raise ValueError("Пользователь не найден")

    user_id = user.id

    achievements_list = await get_all_achievements()
    user_achievements = await get_user_achievements(user_id)
    unlocked_map = {
        user_achievement.achievement_id: user_achievement
        for user_achievement in user_achievements
    }

    checks = {}
    checks["start"] = await has_started(user_id)
    checks["discipline"] = await has_discipline(user_id)
    checks["halfway"] = await has_halfway(user_id)
    checks["winner"] = await has_winner(user_id)

    for ach in achievements_list:
        if ach.code in checks and checks[ach.code]:
            if ach.id not in unlocked_map:
                user_achievement = await unlock_user_achievement(user_id, ach.id)
                unlocked_map[ach.id] = user_achievement

    result = []
    for ach in achievements_list:
        user_achievement = unlocked_map.get(ach.id)
        if user_achievement:
            unlocked_at = user_achievement.unlocked_at.isoformat()
        else:
            unlocked_at = None
        result.append(
            {
                "code": ach.code,
                "name": ach.name,
                "description": ach.description,
                "icon_url": ach.icon_url,
                "unlocked_at": unlocked_at,
            }
        )
    return result
