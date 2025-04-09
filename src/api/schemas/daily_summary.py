from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class FoodLogOut(BaseModel):
    food_name: str
    calories: float
    proteins: float
    fats: float
    carbohydrates: float
    fiber: Optional[float] = None
    amount: int
    date_added: datetime
    is_saved: bool
    message_id: int
    entry_uuid: str
    rating: str

    model_config = ConfigDict(from_attributes=True)


class DailySummaryResponse(BaseModel):
    total_calories: float
    total_proteins: float
    total_fats: float
    total_carbohydrates: float
    food_logs: List[FoodLogOut]
    user_nutrition: Optional[dict]
