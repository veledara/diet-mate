from fastapi import APIRouter

from src.api.handlers.last_ai_report import last_ai_report
from src.api.handlers.generate_ai_report import generate_ai_report
from src.api.schemas.ai_report import AIReportResponse


router = APIRouter(prefix="/analytics", tags=["Аналитика"])

router.post("/generate-ai-report", response_model=AIReportResponse)(generate_ai_report)
router.get("/last-ai-report", response_model=AIReportResponse)(last_ai_report)
