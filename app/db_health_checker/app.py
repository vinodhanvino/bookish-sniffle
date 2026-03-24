"""FastAPI app that mounts the DB health route. Mount this or include router in your main app."""

from fastapi import FastAPI

from app.db_health_checker.health_check import router as health_router

app = FastAPI(title="Spirix Health")
app.include_router(health_router)
