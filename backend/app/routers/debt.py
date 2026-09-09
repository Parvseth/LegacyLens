from collections import defaultdict
from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Project, SourceFile, DebtItem
from app.schemas import DebtSummary, DebtItemOut
from app.dependencies import get_authenticated_project

router = APIRouter()


@router.get("/{project_id}/debt", response_model=DebtSummary)
def get_debt(
    project: Project = Depends(get_authenticated_project),
    db: Session = Depends(get_db),
) -> DebtSummary:
    """Retrieve technical debt items and breakdown for a project."""
    files = db.query(SourceFile).filter(SourceFile.project_id == project.id).all()
    file_map = {f.id: f.relative_path for f in files}

    items = (
        db.query(DebtItem)
        .join(SourceFile, DebtItem.file_id == SourceFile.id)
        .filter(SourceFile.project_id == project.id)
        .all()
    )

    by_category: Dict[str, int] = defaultdict(int)
    for item in items:
        by_category[item.category] += 1

    out_items = [
        DebtItemOut(
            id=item.id,
            file_id=item.file_id,
            file_path=file_map.get(item.file_id, ""),
            category=item.category,
            description=item.description,
            severity=item.severity,
        )
        for item in items
    ]

    return DebtSummary(
        overall_debt_score=project.overall_debt_score,
        items=out_items,
        by_category=dict(by_category),
    )

