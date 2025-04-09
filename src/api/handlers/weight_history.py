from fastapi import Query

from src.api.schemas.weight_history import WeightHistoryResponse, WeightRecordOut
from src.services.logic.nutrition_service import get_user_profile_by_telegram_id
from src.services.logic.user_weight_history_service import (
    get_weight_history_by_telegram_id,
)


async def weight_history(
    telegram_id: int = Query(..., description="Telegram user ID"),
    limit: int = Query(10, description="Сколько записей вернуть (по умолчанию 10)"),
) -> WeightHistoryResponse:
    """
    Возвращает последние limit записей веса пользователя (временная метка + вес)
    и его целевой вес (если есть).
    """
    records = await get_weight_history_by_telegram_id(telegram_id, limit=limit)
    records_out = []
    for r in records:
        records_out.append(WeightRecordOut(date=r.date_added, weight=r.weight))

    user_profile = await get_user_profile_by_telegram_id(telegram_id)
    target_weight = (
        user_profile.target_weight
        if (user_profile and user_profile.target_weight)
        else None
    )

    return WeightHistoryResponse(records=records_out, target_weight=target_weight)
