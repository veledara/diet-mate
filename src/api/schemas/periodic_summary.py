from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from src.api.schemas.daily_summary import FoodLogOut


class DaySummaryOut(BaseModel):
    date: date
    total_calories: float
    total_proteins: float
    total_fats: float
    total_carbohydrates: float
    food_logs: List[FoodLogOut]


class PeriodicSummaryResponse(BaseModel):
    days: List[DaySummaryOut]
    user_nutrition: Optional[dict] = None
    average_calories: float
    average_proteins: float
    average_fats: float
    average_carbohydrates: float
