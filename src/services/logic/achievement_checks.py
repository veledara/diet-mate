from src.services.db.user_food_log_repository import (
    count_food_logs_for_user,
    get_unique_dates_with_logs,
)
from src.services.db.user_profile_repository import get_user_profile_by_user_id
from src.services.db.user_weight_history_repository import get_first_record


async def has_started(user_id: int) -> bool:
    """
    Проверка достижения на первый фуд лог.
    """
    cnt = await count_food_logs_for_user(user_id)
    return cnt > 0


async def has_discipline(user_id: int) -> bool:
    """
    Проверка достижения на использование 7 дней подряд.
    """
    dates = await get_unique_dates_with_logs(user_id)
    if len(dates) < 7:
        return False
    for start_idx in range(len(dates) - 6):
        chain = dates[start_idx : start_idx + 7]
        if _check_consecutive_7_days(chain):
            return True
    return False


def _check_consecutive_7_days(dates_list) -> bool:
    """
    Возвращает True, если dates_list из 7 дат подряд.
    """
    for i in range(6):
        if (dates_list[i + 1] - dates_list[i]).days != 1:
            return False
    return True


async def has_halfway(user_id: int) -> bool:
    """
    Проверка достижения на прохождение 50% пути к целевому весу.
    """
    profile = await get_user_profile_by_user_id(user_id)
    if not profile or not profile.target_weight:
        return False

    initial_weight = await get_first_record(user_id)
    if not initial_weight:
        return False

    current_w = float(profile.weight)
    target_w = float(profile.target_weight)

    if abs(initial_weight - target_w) < 0.01:
        return False

    if initial_weight > target_w:
        total_diff = initial_weight - target_w
        done_diff = initial_weight - current_w
        return done_diff >= 0.5 * total_diff
    else:
        total_diff = target_w - initial_weight
        done_diff = current_w - initial_weight
        return done_diff >= 0.5 * total_diff


async def has_winner(user_id: int) -> bool:
    """
    Проверка на достижения целевого веса.
    """
    profile = await get_user_profile_by_user_id(user_id)
    if not profile or not profile.target_weight:
        return False

    initial_weight = await get_first_record(user_id)
    if not initial_weight:
        return False

    current_w = float(profile.weight)
    target_w = float(profile.target_weight)

    if initial_weight > target_w:
        return current_w <= target_w
    elif initial_weight < target_w:
        return current_w >= target_w
    else:
        return False
