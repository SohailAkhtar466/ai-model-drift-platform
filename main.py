from fastapi import FastAPI

from app.api.routes import router

from app.services.scheduler_service import (
    start_scheduler,
    stop_scheduler,
)



# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="AI Model Drift Detection Platform",
    description=(
        "ML monitoring platform for detecting "
        "data and prediction drift."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

app.include_router(
    router
)

# =========================================================
# Startup
# =========================================================

@app.on_event("startup")
def startup_event():

    # Start automated monitoring every 60 minutes

    start_scheduler(
        interval_minutes=60
    )


# =========================================================
# Shutdown
# =========================================================

@app.on_event("shutdown")
def shutdown_event():

    stop_scheduler()


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "message": (
            "AI Model Drift Detection Platform"
        ),
        "status": "running",
        "version": "1.0.0",
    }