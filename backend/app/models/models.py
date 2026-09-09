import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, JSON, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    INGESTING = "ingesting"
    ANALYZING = "analyzing"
    SCORING = "scoring"
    AI_PROCESSING = "ai_processing"
    COMPLETE = "complete"
    FAILED = "failed"


class SourceType(str, enum.Enum):
    ZIP = "zip"
    GITHUB = "github"


class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    projects: Mapped[List["Project"]] = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # nullable for migration
    name: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[SourceType] = mapped_column(SAEnum(SourceType), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # GitHub URL or original filename
    status: Mapped[ProjectStatus] = mapped_column(SAEnum(ProjectStatus), default=ProjectStatus.PENDING)
    workspace_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_files: Mapped[int] = mapped_column(Integer, default=0)
    avg_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_debt_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_security_score: Mapped[float] = mapped_column(Float, default=0.0)
    migration_readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner: Mapped[Optional["User"]] = relationship("User", back_populates="projects")
    files: Mapped[List["SourceFile"]] = relationship("SourceFile", back_populates="project", cascade="all, delete-orphan")
    dependencies: Mapped[List["Dependency"]] = relationship("Dependency", back_populates="project", cascade="all, delete-orphan")


class SourceFile(Base):
    __tablename__ = "source_files"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    relative_path: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)  # "python" | "java"
    loc: Mapped[int] = mapped_column(Integer, default=0)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    num_classes: Mapped[int] = mapped_column(Integer, default=0)
    num_functions: Mapped[int] = mapped_column(Integer, default=0)
    cyclomatic_complexity: Mapped[float] = mapped_column(Float, default=0.0)
    max_nesting_depth: Mapped[int] = mapped_column(Integer, default=0)
    import_count: Mapped[int] = mapped_column(Integer, default=0)
    internal_dep_count: Mapped[int] = mapped_column(Integer, default=0)
    external_dep_count: Mapped[int] = mapped_column(Integer, default=0)
    has_duplicate_code: Mapped[bool] = mapped_column(Boolean, default=False)
    has_circular_dep: Mapped[bool] = mapped_column(Boolean, default=False)
    has_hardcoded_secrets: Mapped[bool] = mapped_column(Boolean, default=False)
    has_hardcoded_api_keys: Mapped[bool] = mapped_column(Boolean, default=False)
    has_god_class: Mapped[bool] = mapped_column(Boolean, default=False)
    has_long_methods: Mapped[bool] = mapped_column(Boolean, default=False)
    feature_vector: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_level: Mapped[RiskLevel] = mapped_column(SAEnum(RiskLevel), default=RiskLevel.LOW)
    risk_factors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)  # list of strings
    security_score: Mapped[float] = mapped_column(Float, default=100.0)
    debt_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="files")
    source_dependencies: Mapped[List["Dependency"]] = relationship("Dependency", foreign_keys="Dependency.source_file_id", back_populates="source_file", cascade="all, delete-orphan")
    target_dependencies: Mapped[List["Dependency"]] = relationship("Dependency", foreign_keys="Dependency.target_file_id", back_populates="target_file")
    security_findings: Mapped[List["SecurityFinding"]] = relationship("SecurityFinding", back_populates="file", cascade="all, delete-orphan")
    debt_items: Mapped[List["DebtItem"]] = relationship("DebtItem", back_populates="file", cascade="all, delete-orphan")


class Dependency(Base):
    __tablename__ = "dependencies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    source_file_id: Mapped[str] = mapped_column(String, ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False)
    target_file_id: Mapped[str] = mapped_column(String, ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False)
    dep_type: Mapped[str] = mapped_column(String, default="import")  # import | call | reference

    project: Mapped["Project"] = relationship("Project", back_populates="dependencies")
    source_file: Mapped["SourceFile"] = relationship("SourceFile", foreign_keys=[source_file_id], back_populates="source_dependencies")
    target_file: Mapped["SourceFile"] = relationship("SourceFile", foreign_keys=[target_file_id], back_populates="target_dependencies")


class SecurityFinding(Base):
    __tablename__ = "security_findings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id: Mapped[str] = mapped_column(String, ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False)
    finding_type: Mapped[str] = mapped_column(String, nullable=False)  # hardcoded_secret | api_key | weak_auth
    severity: Mapped[str] = mapped_column(String, nullable=False)  # critical | high | medium | low
    description: Mapped[str] = mapped_column(Text, nullable=False)
    line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # redacted snippet

    file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="security_findings")


class DebtItem(Base):
    __tablename__ = "debt_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id: Mapped[str] = mapped_column(String, ForeignKey("source_files.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)  # god_class | long_method | circular_dep | duplicate_code | hardcoded_value
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String, default="medium")

    file: Mapped["SourceFile"] = relationship("SourceFile", back_populates="debt_items")
