from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    API_KEY: str
    # allow fractional thresholds like 0.75
    ALERT_THRESHOLD: float

    class Config:
        env_file = ".env"


settings = Settings()