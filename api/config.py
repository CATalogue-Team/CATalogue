from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    DB_USER: str = "admin"
    DB_PASSWORD: str = "admin"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "catalogue"
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "catalogue"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5174"]
    PG_DATA_DIR: str = "./pgdata"  # 使用项目下的pgdata目录

    class Config:
        env_file = ".env"

settings = Settings()
