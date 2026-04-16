import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .database import engine, Base, SessionLocal
from .routers import tasks as tasks_router
from .routers import trends as trends_router
from .trend_agent import run_trend_fetch

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

scheduler = AsyncIOScheduler()


def _scheduled_trend_fetch():
    """Background job: creates its own DB session and runs the trend fetch."""
    db = SessionLocal()
    try:
        run_trend_fetch(db)
    except Exception as exc:
        logger.error("Scheduled trend fetch failed: %s", exc)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        _scheduled_trend_fetch,
        trigger=IntervalTrigger(hours=6),
        id="shirt_trend_fetch",
        replace_existing=True,
        misfire_grace_time=300,
    )
    scheduler.start()
    logger.info("Shirt trend scheduler started (interval: 6 hours)")
    yield
    scheduler.shutdown(wait=False)
    logger.info("Shirt trend scheduler stopped")


app = FastAPI(title="Todo Manager", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router.router)
app.include_router(trends_router.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
