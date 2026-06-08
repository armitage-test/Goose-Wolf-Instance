from datetime import datetime
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    completed: bool | None = None


class TaskOut(TaskBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ShirtTrendOut(BaseModel):
    id: int
    name: str
    category: str
    score: float
    trend_direction: str
    suggested_action: str
    source: str
    fetched_at: datetime

    model_config = {"from_attributes": True}


class TrendSummaryOut(BaseModel):
    total: int
    top_trend: str | None
    top_score: float | None
    last_fetched: datetime | None
    by_action: dict[str, int]
