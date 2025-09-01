import uuid
from datetime import date

from pydantic import BaseModel, Field

from app.models import ID


class ProjectBase(BaseModel):
    id: ID = Field(default_factory=uuid.uuid4)
    last: date = Field(default_factory=date.today)
    longest_streak: int = 0
    name: str
    streak: int = 0
    url: str
