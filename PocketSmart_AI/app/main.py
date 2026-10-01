from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .db import init_db
from .db import Base, engine
from .routers import auth, pages, planners


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables automatically
    Base.metadata.create_all(bind=engine)

    yield


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "PocketSmart AI - "
        "Budget-aware Generative AI recommendation assistant"
    ),
    lifespan=lifespan,
)
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


app.include_router(pages.router)

app.include_router(
    auth.router,
    prefix="/api",
)

app.include_router(
    planners.router,
    prefix="/api",
)


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": settings.app_name,
        "model": settings.gemini_model,
        "gemini_configured": bool(
            settings.gemini_api_key
        ),
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
