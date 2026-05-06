import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import CORS_ORIGINS, LOG_LEVEL
from backend.models.student import Base, engine
from backend.routers.health import router as health_router
from backend.routers.diagnose import router as diagnose_router
from backend.routers.exercise import router as exercise_router
from backend.routers.plan import router as plan_router
from backend.routers.rewards import router as rewards_router
from backend.routers.sprite import router as sprite_router
from backend.routers.parent import router as parent_router
from backend.routers.push import router as push_router
from backend.routers.llm import router as llm_router

logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Math Home Tutor",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(diagnose_router)
app.include_router(exercise_router)
app.include_router(plan_router)
app.include_router(rewards_router)
app.include_router(sprite_router)
app.include_router(parent_router)
app.include_router(push_router)
app.include_router(llm_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
