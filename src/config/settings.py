import os
from pathlib import Path

from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent.parent

    LOGIN_TIME_DAYS: int = 7

    PATH_TO_EMAIL_TEMPLATES_DIR: str = str(BASE_DIR / "notifications" / "templates")
    ACTIVATION_EMAIL_TEMPLATE_NAME: str = "activation_request.html"
    ACTIVATION_COMPLETE_EMAIL_TEMPLATE_NAME: str = "activation_complete.html"
    PASSWORD_RESET_TEMPLATE_NAME: str = "password_reset_request.html"
    PASSWORD_RESET_COMPLETE_TEMPLATE_NAME: str = "password_reset_complete.html"
    COMMENT_REPLY_TEMPLATE_NAME: str = "comment_reply.html"
    COMMENT_LIKE_TEMPLATE_NAME: str = "comment_like.html"

    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "host")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", 25))
    EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "testuser")
    EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "test_password")
    EMAIL_USE_TLS: bool = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"
    MAILHOG_API_PORT: int = os.getenv("MAILHOG_API_PORT", 8025)

    REDIS_BROKER_URL: str = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")
    REDIS_BACKEND_URL: str = os.getenv("REDIS_BACKEND_URL", "redis://localhost:6379/1")

    S3_STORAGE_URL: str = os.getenv("MINIO_URL", "http://minio-cinema:9000")
    S3_STORAGE_ACCESS_KEY: str = os.getenv("MINIO_ROOT_USER", "minio_admin")
    S3_STORAGE_SECRET_KEY: str = os.getenv("MINIO_ROOT_PASSWORD", "password")
    S3_BUCKET_NAME: str = os.getenv("MINIO_STORAGE", "storage")

    AWS_REGION: str = os.getenv("AWS_REGION", "eu-south-2")

    @property
    def S3_STORAGE_ENDPOINT(self) -> str:
        return self.S3_STORAGE_URL


class Settings(BaseAppSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "test_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "test_password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "test_host")
    POSTGRES_DB_PORT: int = int(os.getenv("POSTGRES_DB_PORT", 5432))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "test_db")

    SECRET_KEY_ACCESS: str = os.getenv("SECRET_KEY_ACCESS", str(os.urandom(32)))
    SECRET_KEY_REFRESH: str = os.getenv("SECRET_KEY_REFRESH", str(os.urandom(32)))
    JWT_SIGNING_ALGORITHM: str = os.getenv("JWT_SIGNING_ALGORITHM", "HS256")
