from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Financial Workflow Assistant"
    APP_ENV: str = "development"

    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()