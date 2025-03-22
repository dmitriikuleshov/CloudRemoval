from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

secret = "testing"
algorithm = "HS256"


def create_jwt(payload: dict, lifespan: int):
    to_encode = payload.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=lifespan)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, secret, algorithm=algorithm)



def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, secret, algorithm)
    except JWTError:
        return None
    
    if "user_id" not in payload:
        return None

    if payload.get("exp") - datetime.now(timezone.utc).timestamp() < 0:
        return None
    
    return payload