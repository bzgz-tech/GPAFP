from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import engine
from app.models.base import Base
# Import all models to ensure they are registered with Base
from app.models import price, indicator, forecast, backtest, alert, user, task
from app.controllers import market, indicator, forecast, backtest, alert, auth, tasks
from app.tasks.scheduler import create_scheduler
import os

# Create tables (In production, use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# CORS
if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(market.router, prefix="/market", tags=["market"])
app.include_router(indicator.router, prefix="/indicator", tags=["indicator"])
app.include_router(forecast.router, prefix="/forecast", tags=["forecast"])
app.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
app.include_router(alert.router, prefix="/alert", tags=["alert"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

@app.get("/")
def root():
    return {"message": "Welcome to Gold Price Analysis & Prediction API"}

_scheduler = None

@app.on_event("startup")
def start_tasks():
    global _scheduler
    if os.environ.get("RUN_MAIN") == "true":
        return
    _scheduler = create_scheduler()
    _scheduler.start()
