from fastapi import Query, HTTPException

from src.models.user_report import UserReport
from src.api.schemas.ai_report import AIReportResponse
from src.services.logic.ai_report_service import get_last_ai_report


async def last_ai_report(
    telegram_id: int = Query(..., description="Telegram user ID"),
    report_type: str = Query(
        ..., description="Тип отчета: 'quality-report' или 'nutrition-report'"
    ),
) -> AIReportResponse:
    """
    Возвращает последний сохранённый AI-отчёт указанного типа, если он существует.
    """
    try:
        user_report: UserReport = await get_last_ai_report(telegram_id, report_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
    if not user_report:
        raise HTTPException(status_code=404, detail="Отчет не найден.")

    return user_report
