from os import environ
from typing import Any


def env(parameter, default_value = None) -> Any:
    return environ.get(f"CLOUD_REMOVAL_{parameter}", default_value)


class Microservices:
    ml_service = env("ML_URL", "ml:8100")


class Credentials:
    class Sentinel:
        client_id = environ.get("SENTINEL_CLIENT_ID")
        client_secret = environ.get("SENTINEL_CLIENT_SECRET")

    class Telegram:
        api_key = env("TELEGRAM_API_KEY")


class Database:
    url = env("DATABASE_URL", "sqlite:///cloud_removal.db")


class JWT:
    secret = env("JWT_SECRET", "invalid-secret")
    algorithm = env("JWT_ALGORITHM", "HS256")


class S3:
    url = env("S3_URL")
    public_url = env("S3_PUBLIC_URL")
    region = env("S3_REGION", "us-east-1")
    access_key = env("S3_ACCESS_KEY")
    secret_key = env("S3_SECRET_KEY")
    bucket = env("S3_BUCKET")


class ML:
    enable_upscaling = int(env("ENABLE_UPSCALING", 0))
