from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    CLIENT_ID: str
    CLIENT_SECRET: str
    TENANT_ID: str

    # Microsoft Graph
    GRAPH_BASE_URL: str 
    GRAPH_SCOPE: str 

    # Teams / Calendar
    TEAMS_ORGANIZER_EMAIL: str
    default_timezone: str = "UTC"

    # Bot Service
    BOT_SERVICE_URL: str

    # Database
    MONGO_URI: str
    database_name: str = "ai_interview"

    # AI
    GEMINI_API_KEY: str

    # Scheduler
    scheduler_timezone: str = "UTC"

    # App
    ENV: str = "development"
    API_PREFIX: str = "/api"
    APP_NAME: str = "AI Interview Platform"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()