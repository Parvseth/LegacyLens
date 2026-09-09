# LegacyLens — API Reference

All endpoints are prefixed with `/api`. The interactive OpenAPI documentation is available at `/api/docs` when the backend is running.

---

## Authentication

All protected endpoints require a `Bearer` token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

### Register

```
POST /api/auth/register
```

**Body**
```json
{ "email": "user@example.com", "password": "your-password" }
```

**Response `200`**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": { "id": "...", "email": "...", "created_at": "..." }
}
```

---

### Login

```
POST /api/auth/login
```

Same body and response shape as register.

---

## Projects

### Upload ZIP

```
POST /api/projects
Content-Type: multipart/form-data
```

**Form fields**
| Field | Type | Description |
|---|---|---|
| `file` | `.zip` file | The repository archive (max 100 MB) |

**Response `200`** — `ProjectOut` object with `status: "pending"`.  
Analysis runs asynchronously; poll `GET /api/projects/:id` until `status == "complete"`.

---

### Clone GitHub Repository

```
POST /api/projects/github
```

**Body**
```json
{ "url": "https://github.com/owner/repo" }
```

---

### List Projects

```
GET /api/projects
```

**Response `200`**
```json
{ "projects": [...], "total": 5 }
```

---

### Get Project

```
GET /api/projects/:id
```

Returns a `ProjectOut` with aggregate scores and current `status`.

---

### Delete Project

```
DELETE /api/projects/:id
```

---

## Analysis

### Get Dashboard Summary

```
GET /api/projects/:id/dashboard
```

**Response `200`** — `DashboardSummary`
```json
{
  "project": { ... },
  "risk_distribution": { "low": 10, "medium": 5, "high": 3, "critical": 1 },
  "top_risky_files": [...],
  "top_debt_files": [...]
}
```

---

### List All Files

```
GET /api/projects/:id/files?page=1&per_page=50
```

Returns paginated `SourceFileOut` records with all metrics.

---

## Dependency Graph

```
GET /api/projects/:id/graph
```

**Response `200`** — `DependencyGraph`
```json
{
  "nodes": [{ "id": "...", "label": "...", "risk_score": 72.4, "risk_level": "High", ... }],
  "edges": [{ "id": "...", "source": "...", "target": "...", "dep_type": "import" }]
}
```

---

## Technical Debt

```
GET /api/projects/:id/debt
```

**Response `200`** — `DebtSummary`
```json
{
  "overall_debt_score": 38.5,
  "items": [...],
  "by_category": { "god_class": 2, "long_method": 7, "circular_dep": 1 }
}
```

---

## Security

```
GET /api/projects/:id/security
```

**Response `200`** — `SecuritySummary`
```json
{
  "overall_security_score": 81.0,
  "total_findings": 4,
  "findings": [...],
  "by_type": { "hardcoded_secret": 2, "hardcoded_api_key": 2 },
  "by_severity": { "Critical": 1, "High": 3 }
}
```

---

## Migration Roadmap

```
GET /api/projects/:id/roadmap
```

**Response `200`** — `MigrationRoadmap`
```json
{
  "project_id": "...",
  "phases": [
    { "phase_number": 1, "name": "Foundation", "description": "...", "files": [...], "estimated_complexity": "Low" }
  ],
  "narrative": null
}
```

---

## AI Features

### Generate File Recommendations

```
POST /api/projects/:id/recommendations
```

**Body**
```json
{
  "project_id": "...",
  "api_key": "sk-...",
  "provider": "openai"   // openai | groq | mistral | together | anthropic
}
```

**Response `200`**
```json
{ "updated": 5, "recommendations": [{ "file_id": "...", "path": "...", "recommendation": "..." }] }
```

---

### Generate Roadmap Narrative

```
POST /api/projects/:id/roadmap-narrative
```

Same body shape as recommendations.

**Response `200`**
```json
{ "narrative": "The XYZ codebase is moderately prepared for migration..." }
```

---

## Export

### Export PDF Report

```
POST /api/projects/:id/export/pdf
```

**Body**
```json
{ "project_id": "...", "format": "pdf", "api_key": "", "provider": "openai" }
```

Returns a `application/pdf` binary stream.

---

### Export DOCX Report

```
POST /api/projects/:id/export/docx
```

Same body, returns `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.

---

## Health

```
GET /api/health
```

**Response `200`**
```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Error Responses

All errors return a consistent JSON envelope:

```json
{
  "success": false,
  "error": "Human-readable message",
  "status_code": 404
}
```

| Status | Meaning |
|---|---|
| `400` | Bad request / validation error |
| `401` | Missing or invalid auth token |
| `403` | Access denied (project belongs to another user) |
| `404` | Project or resource not found |
| `422` | Pydantic validation failure (details included) |
| `500` | Internal server error |
