from app.services.parsers.base import FeatureVector
from app.services.risk_engine import compute_risk_score
from app.services.debt_engine import compute_debt_score
from app.services.security_engine import compute_file_security_score, compute_security_score
from app.services.roadmap_engine import generate_roadmap
from app.models.models import SourceFile, RiskLevel, DebtItem, SecurityFinding


def test_risk_engine_clean_file():
    fv = FeatureVector(file_path="clean.py", language="python")
    fv.loc = 50
    fv.cyclomatic_complexity = 2.0
    fv.max_nesting_depth = 2
    fv.import_count = 3
    fv.internal_dep_count = 1
    fv.external_dep_count = 2

    score, level, factors = compute_risk_score(fv)
    assert score <= 30.0
    assert level == RiskLevel.LOW
    assert "No significant issues detected" in factors


def test_risk_engine_critical_file():
    fv = FeatureVector(file_path="legacy_monster.py", language="python")
    fv.loc = 1500
    fv.cyclomatic_complexity = 35.0
    fv.max_nesting_depth = 8
    fv.import_count = 35
    fv.internal_dep_count = 20
    fv.has_god_class = True
    fv.has_circular_dep = True
    fv.has_hardcoded_secrets = True
    fv.has_long_methods = True
    fv.has_duplicate_code = True

    score, level, factors = compute_risk_score(fv)
    assert score >= 50.0
    assert len(factors) > 0


def test_debt_engine():
    file = SourceFile(
        id="f1",
        project_id="p1",
        relative_path="legacy.py",
        language="python",
    )
    item1 = DebtItem(id="d1", file_id="f1", category="god_class", description="God class", severity="critical")
    item2 = DebtItem(id="d2", file_id="f1", category="circular_dep", description="Cycle", severity="high")
    file.debt_items = [item1, item2]

    debt_score = compute_debt_score([file])
    assert debt_score > 0.0


def test_security_engine():
    # compute_file_security_score tests
    findings_clean = []
    assert compute_file_security_score(findings_clean) == 100.0

    findings_vuln = [
        ("hardcoded_secret", "critical", "Secret token found", 12, "token='xxx'"),
        ("api_key", "high", "AWS API Key", 45, "AKIA..."),
    ]
    assert compute_file_security_score(findings_vuln) < 100.0


def test_roadmap_engine():
    files = [
        SourceFile(
            id="1",
            project_id="p1",
            relative_path="utils.py",
            language="python",
            loc=40,
            risk_score=15.0,
            risk_level=RiskLevel.LOW,
            import_count=2,
            internal_dep_count=0,
            external_dep_count=1,
            debt_score=5.0,
        ),
        SourceFile(
            id="2",
            project_id="p1",
            relative_path="core.py",
            language="python",
            loc=600,
            risk_score=85.0,
            risk_level=RiskLevel.CRITICAL,
            import_count=20,
            internal_dep_count=5,
            external_dep_count=3,
            debt_score=75.0,
        ),
    ]

    phases = generate_roadmap(files)
    assert len(phases) > 0
    phase_names = [p["name"] for p in phases]
    assert any("Foundation" in name or "Core" in name or "Critical" in name for name in phase_names)

