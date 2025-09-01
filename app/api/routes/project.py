import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from surrealdb import RecordID

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


@router.get("/{project_id}")
async def get_project(db: DbDep, project_id: ID):
    """
    Get a project by ID
    """
    project = await db.select(RecordID("project", str(project_id)))
    assert isinstance(project, dict) or project is None
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)


@router.get("/")
async def get_projects(db: DbDep):
    """
    Get all projects
    """
    projects = await db.select("project")
    return [Project(**proj) for proj in projects if isinstance(proj, dict)]

@router.patch("/{project_id}")
async def mark_used_today(db: DbDep, project_id: ID):
    """
    Mark a project as used today
    """
    record = RecordID("project", str(project_id))
    project = await db.select(record)
    assert isinstance(project, dict) or project is None
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    proj = Project(**project)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if proj.last == today:
        raise HTTPException(status_code=400, detail="Project already marked today")
    elif proj.last == today - timedelta(days=1):
        proj.streak += 1
        if proj.streak > proj.longest_streak:
            proj.longest_streak = proj.streak
    else:
        proj.streak = 1
    proj.last = today
    await db.update(record, proj.model_dump())
    return proj

@router.delete("/{project_id}")
async def delete_project(db: DbDep, project_id: ID):
    """
    Delete a project by ID
    """
    record = RecordID("project", str(project_id))
    project = await db.select(record)
    assert isinstance(project, dict) or project is None
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(record)
    return {"detail": "Project deleted"}