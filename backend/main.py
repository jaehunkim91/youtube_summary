# backend/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.db.database import engine
from backend.db.models import Base
from backend.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _scheduler = None
    if not os.getenv("DISABLE_SCHEDULER"):
        from backend.scheduler import scheduler, run_fetch_job
        from apscheduler.triggers.interval import IntervalTrigger
        scheduler.add_job(run_fetch_job, IntervalTrigger(hours=3))
        scheduler.start()
        _scheduler = scheduler

    yield

    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)


app = FastAPI(title="주식 유튜버 분석", lifespan=lifespan)
app.include_router(router)

FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
