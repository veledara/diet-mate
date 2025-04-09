from typing import Optional, List
from pydantic import BaseModel


class AchievementOut(BaseModel):
    code: str
    name: str
    description: str
    icon_url: Optional[str]
    unlocked_at: Optional[str]


class AchievementsResponse(BaseModel):
    achievements: List[AchievementOut]
