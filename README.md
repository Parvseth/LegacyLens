# 👁️‍🗨️ LegacyLens — AI-Powered Legacy Code Migration Risk Analyzer

[![CI / QA Pipeline](https://github.com/itzzpriyal/LegacyLens/actions/workflows/ci.yml/badge.svg)](https://github.com/itzzpriyal/LegacyLens/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![React 18](https://img.shields.io/badge/react-18-61DAFB.svg?logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Live Demo:** [https://itzzpriyal-legacy-lens.vercel.app](https://itzzpriyal-legacy-lens.vercel.app)

Upload any **Java or Python** repository as a ZIP. Get a complete, production-grade migration readiness report in under a minute — with risk scores, dependency graphs, security findings, AI recommendations, and a PDF/DOCX export — all without sending your source code to any external service.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Deterministic Risk Scoring** | 0–100 score computed purely from code metrics — no LLM hallucinations |
| 🕸️ **Interactive Dependency Graph** | Zoomable, click-to-inspect ReactFlow visualization with node fading |
| 🔐 **Security Analysis** | Detects hardcoded secrets, API keys, and weak authentication patterns |
| 🤖 **Multi-Provider AI Recommendations** | OpenAI, Groq (Llama 3), Mistral, Together AI — plain-English remediation |
| 💸 **Technical Debt Dashboard** | God classes, long methods, circular deps, duplicate code — with TDR formula |
| 🗺️ **Migration Roadmap** | Phased plan from low-risk to critical modules with AI executive narrative |
| 📄 **One-Click Export** | PDF and DOCX executive reports with full analysis summary |
| 🔒 **Security-First** | CSP headers, rate limiting middleware, secrets redaction before any LLM call |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐     ┌──────────────────────────────────┐
│            Frontend                 │     │            Backend               │
│   React 18 + Vite + TypeScript      │────▶│   FastAPI + Python 3.11          │
│   React Router · Framer Motion      │     │   SQLAlchemy ORM                 │
│   ReactFlow · Recharts · Lucide     │◀────│   Pydantic v2 settings           │
│   Axios · react-hot-toast           │     │   JWT Auth · BCrypt              │
└────────────────┬────────────────────┘     └───────────────┬──────────────────┘
                 │ Nginx reverse proxy                       │
                 └───────────────────────────────────────────┘
                                    │
                     ┌──────────────▼──────────────┐
                     │       PostgreSQL / SQLite     │
                     └─────────────────────────────-┘
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full Mermaid system diagram.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** and `pip`
- **Node.js 20+** and `npm`
- *(Optional)* Docker & Docker Compose for one-command startup

### Option A — Docker Compose (Recommended)

```bash
git clone https://github.com/itzzpriyal/LegacyLens.git
cd LegacyLens
docker compose up --build
```

- Frontend: http://localhost  
- Backend API docs: http://localhost/api/docs

### Option B — Local Development

**Backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

---

## ⚙️ Environment Variables

Create `backend/.env`:

```env
DATABASE_URL=sqlite:///./legacylens.db   # or postgresql://user:pass@host/db
SECRET_KEY=change-me-in-production
JWT_SECRET_KEY=change-me-in-production
OPENAI_API_KEY=                          # optional server-side fallback key
WORKSPACE_DIR=./workspaces
MAX_UPLOAD_SIZE_MB=100
CORS_ORIGINS=http://localhost:5173,http://localhost
```

> **API keys are never required.** All risk, debt, and security scores are computed locally. An API key is only used for the optional AI recommendation and narrative features, and is stored exclusively in the browser's `localStorage`.

---

## 🧪 Running Tests

**Backend**
```bash
cd backend
pytest -v --cov=app --cov-report=term-missing
```

**Frontend**
```bash
cd frontend
npm run lint
npm run build
```

---

## 📁 Project Structure

```
LegacyLens/
├── backend/
│   ├── app/
│   │   ├── routers/          # FastAPI endpoint routers
│   │   ├── services/         # Analysis engines (risk, debt, security, AI)
│   │   │   └── parsers/      # Python & Java AST parsers
│   │   ├── models/           # SQLAlchemy ORM models
│   │   └── schemas/          # Pydantic request/response schemas
│   └── tests/                # pytest test suite
├── frontend/
│   └── src/
│       ├── components/       # Reusable UI components
│       ├── pages/            # Route-level page components
│       ├── api/              # Axios API client
│       ├── context/          # React auth context
│       └── types/            # TypeScript type definitions
├── docs/
│   ├── ARCHITECTURE.md       # System architecture diagrams
│   └── API.md                # API endpoint reference
├── docker-compose.yml
└── .github/workflows/ci.yml  # CI/CD pipeline
```

---

## 🛠️ Tech Stack

**Backend**: FastAPI · SQLAlchemy · Pydantic v2 · BCrypt · PyJWT · python-multipart · ReportLab · python-docx  
**Frontend**: React 18 · TypeScript · Vite · ReactFlow · Recharts · Framer Motion · Lucide Icons · Axios  
**Infrastructure**: Docker · Nginx · GitHub Actions CI/CD  
**Deployment**: Vercel (frontend) · Render (backend + PostgreSQL)

---

## 🤝 Contributing

1. Fork the repo and create your branch from `develop`
2. Run the full CI check locally: `pytest -v` + `npm run lint && npm run build`
3. Open a Pull Request — the CI pipeline will run automatically

---

## 📄 License

MIT © 2024 Priyal — see [LICENSE](LICENSE)

