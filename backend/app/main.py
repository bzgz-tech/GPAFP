from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import engine
from app.models.base import Base
# Import all models to ensure they are registered with Base
from app.models import price, indicator, forecast, backtest, alert, user, task, news
from app.controllers import market, indicator, forecast, backtest, alert, auth, tasks, news as news_controller, analysis
from app.tasks.scheduler import create_scheduler
from app.core.db import SessionLocal
from app.dao.user_dao import UserDAO
from app.models.user import User
from app.core.security import hash_password, verify_password
from datetime import datetime
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
app.include_router(news_controller.router, prefix="/news", tags=["news"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])

@app.get("/")
def root():
    return {"message": "Welcome to Gold Price Analysis & Prediction API"}

_scheduler = None

def init_default_data():
    """Initialize default data like admin user"""
    db = SessionLocal()
    try:
        user_dao = UserDAO()
        admin = user_dao.find_by_username(db, "admin")
        if not admin:
            print("Creating default admin user...")
            new_admin = User(
                username="admin",
                hashed_password=hash_password("Admin123!"),
                email="admin@gpafp.com",
                is_active=True,
                created_at=datetime.utcnow()
            )
            user_dao.create(db, new_admin)
            print("Default admin user created: admin / Admin123!")
        else:
            # Verify password matches, if not update it
            if not verify_password("Admin123!", admin.hashed_password):
                print("Updating admin password...")
                admin.hashed_password = hash_password("Admin123!")
                db.add(admin)
                db.commit()
                print("Admin password updated.")
    except Exception as e:
        print(f"Error initializing default data: {e}")
    finally:
        db.close()

@app.on_event("startup")
def start_tasks():
    # Initialize DB data
    init_default_data()
    
    global _scheduler
    if os.environ.get("RUN_MAIN") == "true":
        return
    _scheduler = create_scheduler()
    _scheduler.start()
