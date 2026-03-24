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
