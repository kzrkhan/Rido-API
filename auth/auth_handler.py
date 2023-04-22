import time
from typing import Dict
import jwt
from decouple import config


JWT_SECRET = b'8a86818d58a8ec5ea97992c0011fc304695f37836da3e0b9'
JWT_ALGORITHM = "HS256"


def token_response(token: str):
    return token

def sign_JWT(user_id : str):
    payload = {
        "user_id" : user_id,
        "expires" : time.time() + 6000
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

def decode_JWT(token : str):
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}