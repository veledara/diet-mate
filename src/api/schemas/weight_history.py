from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class WeightRecordOut(BaseModel):
    date: datetime
    weight: float


class WeightHistoryResponse(BaseModel):
    records: List[WeightRecordOut]
    target_weight: Optional[float] = None
