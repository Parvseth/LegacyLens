# LegacyLens — System Architecture

## Overview

LegacyLens is a full-stack, containerised web application consisting of three primary services: a React/Vite frontend, a FastAPI backend, and a PostgreSQL database. In production, Nginx reverse-proxies the frontend and forwards `/api/` traffic to the backend container.

---

## High-Level Component Diagram

```mermaid
graph TB
    subgraph Client["Browser (Client)"]
        UI["React 18 + Vite SPA"]
        LS["localStorage (API keys only)"]
    end

    subgraph Frontend["Frontend Container (Nginx)"]
        NGINX["Nginx — Port 80\nCSP · HSTS · XFO headers"]
        STATIC["Static JS/CSS/HTML (Vite build)"]
    end

    subgraph Backend["Backend Container (FastAPI)"]
        APP["FastAPI App — Port 8000"]
        MW["Middleware Stack\nCORS · SecurityHeaders · RequestTiming"]
        ROUTERS["Routers\nauth · projects · analysis · graph\ndebt · security · roadmap · ai · export"]
        SERVICES["Services\nRiskEngine · DebtEngine · SecurityEngine\nRoadmapEngine · AIService · ExportService"]
        PARSERS["Parsers\nPythonParser · JavaParser"]
    end

    subgraph DB["Database"]
        PG["PostgreSQL / SQLite (SQLAlchemy ORM)"]
    end

    subgraph External["External (Optional)"]
        LLM["LLM Providers\nOpenAI · Groq · Mistral · Together"]
    end

    UI -->|HTTP/REST| NGINX
    NGINX -->|Serve static| STATIC
    NGINX -->|Proxy /api/| APP
    UI -->|Stores keys| LS
    APP --> MW --> ROUTERS --> SERVICES
    SERVICES --> PARSERS
    SERVICES -->|SQLAlchemy| PG
    SERVICES -->|API key from client| LLM
```

---

## Data Flow — File Analysis Pipeline

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant F as Frontend (React)
    participant B as FastAPI Backend
    participant P as Parser Service
    participant E as Analysis Engines
    participant D as Database

    U->>F: Upload .zip file
    F->>B: POST /api/projects (multipart/form-data)
    B->>D: Create Project record (status=PENDING)
    B-->>F: { project_id, status: "pending" }
    B->>B: Extract ZIP to workspace/
    B->>P: Parse Python/Java files (AST)
    P-->>B: SourceFile metrics[]
    B->>E: RiskEngine.score(metrics)
    B->>E: DebtEngine.detect(metrics)
    B->>E: SecurityEngine.scan(metrics)
    B->>E: RoadmapEngine.plan(files)
    E-->>B: Scored SourceFile[]
    B->>D: Persist SourceFile records
    B->>D: Update Project (status=COMPLETE, aggregate scores)
    F->>B: GET /api/projects/:id/dashboard
    B-->>F: DashboardSummary
    F-->>U: Render Dashboard, Graph, Debt, Security tabs
```

---

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB

    U->>F: POST /register (email + password)
    F->>B: POST /api/auth/register
    B->>B: bcrypt.hash(password, rounds=12)
    B->>DB: INSERT user
    B-->>F: JWT access_token + UserOut
    F->>F: Store token in localStorage

    U->>F: Navigate to protected route
    F->>B: GET /api/projects (Authorization: Bearer token)
    B->>B: JWT.decode -> get user_id
    B->>DB: Verify user exists
    B-->>F: ProjectList
```

---

## Security Model

| Layer | Control |
|---|---|
| **Transport** | HTTPS in production (HSTS enabled in nginx.conf) |
| **Frontend headers** | CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy |
| **Backend headers** | Same headers as defence-in-depth via `SecurityHeadersMiddleware` |
| **Authentication** | JWT tokens, bcrypt password hashing (cost 12) |
| **API key handling** | Keys stored only in browser `localStorage`, never persisted to DB |
| **Secret redaction** | `_redact_secrets()` strips 16+ char tokens before sending to LLM |
| **No raw code** | Raw source code is never sent externally — only structured metric summaries |
| **Input validation** | Pydantic v2 schemas validate all incoming requests |
| **Slow request logging** | `RequestTimingMiddleware` logs requests > 500 ms |

---

## Directory Structure

```
LegacyLens/
├── .github/workflows/ci.yml       # CI: lint · typecheck · security scan · test · coverage
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app, middleware stack, lifespan
│   │   ├── config.py              # pydantic-settings (env vars)
│   │   ├── database.py            # SQLAlchemy engine + session factory
│   │   ├── dependencies.py        # JWT auth dependency, project ownership check
│   │   ├── models/models.py       # ORM models: User, Project, SourceFile, DebtItem, SecurityFinding
│   │   ├── schemas/schemas.py     # Pydantic request/response schemas
│   │   ├── routers/               # One router per feature domain
│   │   └── services/
│   │       ├── risk_engine.py     # Weighted metric scoring formula
│   │       ├── debt_engine.py     # God class / long method / circular dep detection
│   │       ├── security_engine.py # Regex + AST secret/API key detection
│   │       ├── roadmap_engine.py  # Topological phase planning
│   │       ├── ai_service.py      # Multi-provider LLM integration (OpenAI SDK)
│   │       ├── export_service.py  # PDF (ReportLab) + DOCX report generation
│   │       └── parsers/
│   │           ├── python_parser.py   # Python ast module
│   │           └── java_parser.py     # Regex-based Java parser
│   └── tests/                     # pytest suite (auth, engines, parsers, API lifecycle)
├── frontend/
│   ├── nginx.conf                 # Reverse proxy + security headers + gzip compression
│   └── src/
│       ├── App.tsx                # Routes + React.lazy + Suspense (code-splitting)
│       ├── api/client.ts          # Axios instance + typed API call functions
│       ├── context/AuthContext.tsx
│       ├── types/index.ts         # Shared TypeScript interfaces
│       ├── pages/                 # LandingPage · ProjectsPage · AnalysisPage · SettingsPage
│       └── components/
│           ├── Dashboard/         # DashboardSummary (overview cards)
│           ├── DebtDashboard/     # TDR formula card + CSV export
│           ├── DependencyGraph/   # ReactFlow + click-to-highlight + inspect panel
│           ├── Roadmap/           # RoadmapView with ReactFlow layout
│           ├── SecurityDashboard/ # Security findings table + charts
│           └── shared/            # Navbar · ScoreGauge · RiskBadge · ProtectedRoute
├── docs/
│   ├── ARCHITECTURE.md            # This file — system diagrams
│   └── API.md                     # API endpoint reference
├── docker-compose.yml
└── README.md
```

