from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Project, SourceFile
from app.schemas import MigrationRoadmap, RoadmapPhase
from app.services.roadmap_engine import generate_roadmap
from app.dependencies import get_authenticated_project

router = APIRouter()


@router.get("/{project_id}/roadmap", response_model=MigrationRoadmap)
def get_roadmap(
    project: Project = Depends(get_authenticated_project),
    db: Session = Depends(get_db),
) -> MigrationRoadmap:
    """Generate migration roadmap phases for a project."""
    files = db.query(SourceFile).filter(SourceFile.project_id == project.id).all()
    phases_data = generate_roadmap(files)

    phases = [
        RoadmapPhase(
            phase_number=p["phase_number"],
            name=p["name"],
            description=p["description"],
            files=p["files"],
            estimated_complexity=p["estimated_complexity"],
        )
        for p in phases_data
    ]

    return MigrationRoadmap(project_id=project.id, phases=phases)

