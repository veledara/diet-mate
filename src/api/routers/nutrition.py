from fastapi import APIRouter

from src.api.handlers.periodic_summary import periodic_summary
from src.api.handlers.daily_summary import daily_summary
from src.api.schemas.daily_summary import DailySummaryResponse
from src.api.schemas.periodic_summary import PeriodicSummaryResponse


router = APIRouter(prefix="/nutrition", tags=["Питание"])

router.get("/daily-summary", response_model=DailySummaryResponse)(daily_summary)
router.get("/periodic-summary", response_model=PeriodicSummaryResponse)(
    periodic_summary
)
