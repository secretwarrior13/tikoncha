import uvicorn
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import config
from app.routers import (
    apps,
    auth,
    blocking,
    devices,
    locations,
    logs,
    parent_profile,
    preferences,
    register,
    schools,
    student_profile,
    users,
    websites,
)
from app.version import __version__

api_router = APIRouter()
api_router.include_router(apps.router)
api_router.include_router(auth.router)
api_router.include_router(register.router)
api_router.include_router(users.router)
api_router.include_router(student_profile.router)
api_router.include_router(parent_profile.router)
api_router.include_router(schools.router)
api_router.include_router(devices.router)
api_router.include_router(locations.router)
api_router.include_router(logs.router)
api_router.include_router(preferences.router)
api_router.include_router(websites.router)
api_router.include_router(blocking.router)


def create_app() -> FastAPI:
    app = FastAPI(
        title=config.PROJECT_NAME,
        # description=config.PROJECT_DESCRIPTION,
        version=__version__,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    if config.ENVIRONMENT == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=config.TRUSTED_HOSTS,
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3) Global security headers
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response

    # 4) Mount versioned API
    app.include_router(api_router)

    # 5) Health‐check
    @app.get("/", include_in_schema=False)
    async def health_check():
        return {
            "status": "ok",
            "project": config.PROJECT_NAME,
            "docs": "/docs",
        }

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        reload=config.RELOAD,
    )
