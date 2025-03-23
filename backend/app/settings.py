from os import environ


def env(env_name, default_value = None, prefix = "GALERA_BACKEND"):
    """
    This function retrieves the environment variable value with a
    constant prefix and presumed default value in a more succinct manner.
    """
    return environ.get(prefix + "_" + env_name, default_value)


class Database:
    url = env("DATABASE_URL", "sqlite:///cloud_removal.db")


class JWT:
    secret = env("JWT_SECRET", "invalid-secret")
    algorithm = env("JWT_ALGORITHM", "HS256")