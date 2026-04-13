from fastapi import FastAPI
from app.api import interview_routes
from app.services.scheduler_service import start_schedule

app = FastAPI(
    title = "AI Interview Platform", 
    version = "1.0.0"
)

app.include_router(interview_routes.router, prefix = "/api")

@app.on_event("startup")
def startup_event():
    print("Starting AI Interview Platform")
    start_schedule()










