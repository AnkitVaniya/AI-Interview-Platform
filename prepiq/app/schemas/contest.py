from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ContestCreate(BaseModel):
    title: str
    question_ids: list[str]
    start_time: datetime
    end_time: datetime


class ContestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_time: datetime
    end_time: datetime


class ContestStatus(BaseModel):
    id: int
    title: str
    status: str  # "upcoming" | "live" | "ended"
    seconds_remaining: int | None  # None once ended
