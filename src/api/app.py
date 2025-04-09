from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.api.routers import achievements, nutrition, analytics, users


def create_app() -> FastAPI:
    app = FastAPI(
        title="Diet Mate API",
        description="Backend-система приложения для интеллектуального контроля питания Diet Mate.",
        version="1.0.0",
        docs_url="/api/v1/docs",  # Swagger UI
        redoc_url="/api/v1/redoc",  # ReDoc
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/static", StaticFiles(directory="src/api/static"), name="static")

    app.include_router(users.router, prefix="/api/v1")
    app.include_router(nutrition.router, prefix="/api/v1")
    app.include_router(analytics.router, prefix="/api/v1")
    app.include_router(achievements.router, prefix="/api/v1")

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
