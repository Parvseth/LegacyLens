from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Project, SourceFile, Dependency
from app.schemas import DependencyGraph, GraphNode, GraphEdge
from app.dependencies import get_authenticated_project

router = APIRouter()


@router.get("/{project_id}/graph", response_model=DependencyGraph)
def get_graph(
    project: Project = Depends(get_authenticated_project),
    db: Session = Depends(get_db),
) -> DependencyGraph:
    """Retrieve the dependency graph nodes and edges for a project."""
    files = db.query(SourceFile).filter(SourceFile.project_id == project.id).all()
    deps = db.query(Dependency).filter(Dependency.project_id == project.id).all()

    nodes = [
        GraphNode(
            id=f.id,
            label=f.relative_path.split("/")[-1],
            risk_score=f.risk_score,
            risk_level=f.risk_level.value if f.risk_level else "Low",
            language=f.language,
            loc=f.loc,
            num_functions=f.num_functions,
            num_classes=f.num_classes,
        )
        for f in files
    ]

    edges = [
        GraphEdge(
            id=d.id,
            source=d.source_file_id,
            target=d.target_file_id,
            dep_type=d.dep_type,
        )
        for d in deps
    ]

    return DependencyGraph(nodes=nodes, edges=edges)

