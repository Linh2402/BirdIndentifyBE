from flask import request
import jwt
from my_app.config import SECRET_KEY


def current_user_is_admin():
    token = request.headers.get("Authorization")
    if token:
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            role = decoded_token.get("role")
            if role == 1:
                return True
        except jwt.InvalidTokenError:
            pass
    return False
