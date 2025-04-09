from fastapi import APIRouter

from src.api.handlers.weight_history import weight_history
from src.api.schemas.weight_history import WeightHistoryResponse
from src.api.handlers.user_report import user_report


router = APIRouter(prefix="/users", tags=["Пользователи"])

router.get("/weight-history", response_model=WeightHistoryResponse)(weight_history)
router.get("/user-report")(user_report)
