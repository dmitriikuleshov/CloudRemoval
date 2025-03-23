from os import environ


def env(env_name, default_value = None, prefix = "GALERA_TELEGRAM"):
    """
    This function retrieves the environment variable value with a
    constant prefix and presumed default value in a more succinct manner.
    """
    return environ.get(prefix + "_" + env_name, default_value)


class Microservices:
    ml_service = env("ML_URL", "ml-service")


class Credentials:
    api_key = env("API_KEY")