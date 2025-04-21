from os import environ


def env(parameter, default_value = None):
    return environ.get(f"CLOUD_REMOVAL_{parameter}", default_value)


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