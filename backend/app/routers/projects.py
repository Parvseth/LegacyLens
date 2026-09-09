import os
import shutil
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models.models import Project, ProjectStatus, SourceType, User
from app.schemas import ProjectOut, ProjectList
from app.services.analysis_service import extract_zip, clone_github_repo, run_analysis
from app.dependencies import get_current_user, get_authenticated_project
from app.config import settings

router = APIRouter()


def _workspace_path(project_id: str) -> str:
    return os.path.join(settings.WORKSPACE_DIR, project_id)


def _run_analysis_bg(project_id: str, workspace_path: str, db_factory):
    """Run analysis in a background thread with its own DB session."""
    db = db_factory()
    try:
        run_analysis(project_id, workspace_path, db)
    finally:
        db.close()


@router.get("", response_model=ProjectList)
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectList:
    """List all projects belonging to current user."""
    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return ProjectList(projects=projects, total=len(projects))


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project: Project = Depends(get_authenticated_project),
) -> Project:
    """Retrieve details of a single project."""
    return project


@router.post("/upload", response_model=ProjectOut)
async def upload_zip(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    """Upload a ZIP archive for analysis."""
    filename = file.filename or "upload.zip"
    if not filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported")

    project_id = str(uuid.uuid4())
    project_name = name or os.path.splitext(filename)[0]

    workspace = _workspace_path(project_id)
    os.makedirs(workspace, exist_ok=True)

    zip_path = os.path.join(workspace, "upload.zip")
    content = await file.read()
    with open(zip_path, "wb") as f:
        f.write(content)

    try:
        extracted = extract_zip(zip_path, os.path.join(workspace, "src"))
    except Exception as e:
        shutil.rmtree(workspace, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f"Failed to extract ZIP: {e}")

    project = Project(
        id=project_id,
        user_id=current_user.id,
        name=project_name,
        source_type=SourceType.ZIP,
        source_url=filename,
        workspace_path=extracted,
        status=ProjectStatus.ANALYZING,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    background_tasks.add_task(_run_analysis_bg, project_id, extracted, SessionLocal)
    return project


@router.post("/github", response_model=ProjectOut)
async def clone_repo(
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    name: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    """Clone a public GitHub repository for analysis."""
    if not url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Only public GitHub URLs are supported")

    project_id = str(uuid.uuid4())
    repo_name = name or url.rstrip("/").split("/")[-1]

    workspace = _workspace_path(project_id)
    os.makedirs(workspace, exist_ok=True)
    src_dir = os.path.join(workspace, "src")

    project = Project(
        id=project_id,
        user_id=current_user.id,
        name=repo_name,
        source_type=SourceType.GITHUB,
        source_url=url,
        workspace_path=src_dir,
        status=ProjectStatus.INGESTING,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    try:
        clone_github_repo(url, src_dir)
    except Exception as e:
        project.status = ProjectStatus.FAILED
        project.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Failed to clone repo: {e}")

    project.status = ProjectStatus.ANALYZING
    db.commit()

    background_tasks.add_task(_run_analysis_bg, project_id, src_dir, SessionLocal)
    return project


@router.delete("/{project_id}")
def delete_project(
    project: Project = Depends(get_authenticated_project),
    db: Session = Depends(get_db),
):
    """Delete a project and its workspace artifacts."""
    workspace = _workspace_path(project.id)
    shutil.rmtree(workspace, ignore_errors=True)
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}

