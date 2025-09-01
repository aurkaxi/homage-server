import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import DbDep
from app.models import ID

router = APIRouter(prefix="/project", tags=["project"])


class ProjectBase(BaseModel):
    # id: ID = Field(default_factory=uuid.uuid4) -> moved to Project
    last: datetime = Field(
        default_factory=lambda: datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    )
    longest_streak: int = 0
    name: str
    streak: int = 0
    url: str


class ProjectCreate(BaseModel):
    name: str
    url: str


class Project(ProjectBase):
    id: ID = Field(default_factory=uuid.uuid4)
    pass


@router.post("/")
async def create_project(db: DbDep, project: ProjectCreate):
    """
    Create a new project
    """
    exist = await db.query(
        "SELECT * FROM project WHERE name = $name OR url = $url",
        {"name": project.name, "url": project.url},
    )
    if exist:
        raise HTTPException(
            status_code=400,
            detail={"error": "Project with this name or URL already exists"},
        )

    db_obj = Project(**project.model_dump())
    await db.create("project", db_obj.model_dump())
    return db_obj
