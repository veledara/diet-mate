from fastapi import HTTPException, Body

from src.services.logic.ai_report_service import create_ai_report
from src.models.user_report import UserReport
from src.api.schemas.ai_report import AIReportResponse, GenerateAIReportRequest


async def generate_ai_report(
    data: GenerateAIReportRequest = Body(...),
) -> AIReportResponse:
    """
    Генерирует новый AI отчет на основе параметров, переданных в теле запроса.
    """
    try:
        user_report: UserReport = await create_ai_report(
            telegram_id=data.telegram_id, report_type=data.report_type, limit=data.limit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not user_report:
        raise HTTPException(status_code=500, detail="Не удалось сгенерировать отчет.")
    
    return user_report
