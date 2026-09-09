import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import projects, analysis, graph, debt, security, roadmap, ai, export, auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("legacylens")

# Create workspace directory
os.makedirs(settings.WORKSPACE_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: create tables and perform auto-migrations on startup."""
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            if engine.dialect.name == "sqlite":
                cols = [row[1] for row in conn.execute(text("PRAGMA table_info(projects)"))]
                if "user_id" not in cols:
                    conn.execute(text("ALTER TABLE projects ADD COLUMN user_id VARCHAR REFERENCES users(id)"))
                    conn.commit()
            elif engine.dialect.name == "postgresql":
                res = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='projects' AND column_name='user_id'"
                ))
                if not res.fetchone():
                    conn.execute(text("ALTER TABLE projects ADD COLUMN user_id VARCHAR REFERENCES users(id)"))
                    conn.commit()
    except Exception as e:
        logger.error("Migration error: %s", e)
    yield


app = FastAPI(
    title="LegacyLens API",
    description="AI-Powered Legacy Code Migration Risk Analyzer",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ── Security Headers Middleware ──────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every API response (defence-in-depth)."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


# ── Request Timing Middleware ─────────────────────────────────────────────
class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Log requests that take longer than 500 ms so slow endpoints are visible."""
    SLOW_THRESHOLD_MS = 500

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms > self.SLOW_THRESHOLD_MS:
            logger.warning(
                "SLOW REQUEST %s %s — %.0f ms",
                request.method,
                request.url.path,
                elapsed_ms,
            )
        return response


app.add_middleware(RequestTimingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# CORS — allow any frontend (crucial for Vercel deployments)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": "Validation error", "details": exc.errors()},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error processing request %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Internal server error occurred."},
    )


# Mount routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(analysis.router, prefix="/api/projects", tags=["Analysis"])
app.include_router(graph.router, prefix="/api/projects", tags=["Graph"])
app.include_router(debt.router, prefix="/api/projects", tags=["Debt"])
app.include_router(security.router, prefix="/api/projects", tags=["Security"])
app.include_router(roadmap.router, prefix="/api/projects", tags=["Roadmap"])
app.include_router(ai.router, prefix="/api/projects", tags=["AI"])
app.include_router(export.router, prefix="/api/projects", tags=["Export"])


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/")
def root():
    return {"message": "LegacyLens API — visit /api/docs for documentation"}

