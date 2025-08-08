from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5433"
    DB_NAME: str = "catalogue"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    PG_DATA_DIR: str = "D:\\DevTools\\PostgreSQL\\data"  # 默认值，会被.env覆盖

    class Config:
        env_file = ".env"

settings = Settings()
