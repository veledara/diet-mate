from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class GenerateAIReportRequest(BaseModel):
    telegram_id: int
    report_type: str
    limit: int = 10


class AIReportResponse(BaseModel):
    id: int
    report_type: str
    created_at: datetime
    report: str = Field(..., alias="content")

    model_config = ConfigDict(from_attributes=True)
