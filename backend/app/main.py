import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.models.database import init_db
from app.api.auth_routes import router as auth_router
from app.api.diagrams import router as diagrams_router
from app.api.lint import router as lint_router
from app.api.eval import router as eval_router
from app.api.llm_routes import router as llm_router
from app.api.audit import router as audit_router

def _read_version() -> str:
    try:
        version_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "VERSION"
        )
        with open(version_path) as f:
            return f.read().strip()
    except (FileNotFoundError, OSError):
        return "0.0.0"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield

def create_app() -> FastAPI:
    application = FastAPI(
        title="Vector Console",
        description="Editorial diagram design and AI coding agent evaluation console",
        version=_read_version(),
        lifespan=lifespan
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(auth_router)
    application.include_router(diagrams_router)
    application.include_router(lint_router)
    application.include_router(eval_router)
    application.include_router(llm_router)
    application.include_router(audit_router)

    @application.get("/health")
    async def healthcheck():
        return {
            "status": "ok",
            "environment": settings.ENVIRONMENT,
            "demo_mode": settings.DEMO_MODE,
            "service": "vector-console"
        }

    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error occurred", "path": request.url.path}
        )

    return application

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
