from functools import wraps
from jwt.exceptions import InvalidSignatureError, ExpiredSignatureError
from flask import request, jsonify
import jwt
from scripts.db_models import User


def check_token(secret_key):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            else:
                return jsonify({'response': 'No token here'}), 401

            try:
                token_data = jwt.decode(token, secret_key, algorithms=["HS256"])
            except InvalidSignatureError:
                return jsonify({'response': 'Wrong token'}), 401
            except ExpiredSignatureError:
                return jsonify({'response': 'Token expired'}), 401

            user = User.query.filter_by(login=token_data['login']).first()

            return function(user, *args, **kwargs)

        return wrapper
    return decorator
