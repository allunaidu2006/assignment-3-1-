from pydantic_settings import BaseSettings
from pathlib import Path

# Resolve paths relative to this file so the app works regardless of cwd
_BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

class Settings(BaseSettings):
    SECRET_KEY: str = "super-secret-jwt-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = f"sqlite:///{_BASE_DIR / 'data' / 'match_predictor.db'}"
    MODEL_PATH: str = str(_BASE_DIR / "models" / "match_predictor.joblib")
    MODEL_METADATA_PATH: str = str(_BASE_DIR / "models" / "model_metadata.json")

    class Config:
        env_file = ".env"

settings = Settings()
