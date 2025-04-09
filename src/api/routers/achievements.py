from fastapi import APIRouter

from src.api.handlers.achievements import achievements
from src.api.schemas.achievements import AchievementsResponse


router = APIRouter(prefix="/achievements", tags=["Достижения"])

router.get("/", response_model=AchievementsResponse)(achievements)
