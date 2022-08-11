from flask import request, abort
import jwt

from config import Config
from constants import ALGO


def auth_required(func):
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(401)
        data = request.headers['Authorization']
        token = data.split('Bearer ')[-1]
        try:
            jwt.decode(token, Config.SECRET_HERE, algotithms=[ALGO])
            return func(*args, **kwargs)
        except Exception as e:
            print('JWT Decode Exception', e)
            abort(401)
    return wrapper


def admin_required(func):
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(401)
        data = request.headers['Authorization']
        token_user = data.split('Bearer ')[-1]
        try:
            user = jwt.decode(token_user, Config.SECRET_HERE, algorithms=[ALGO])
            role = user['role']
            if role != 'admin':
                abort(403)
            return func(*args, **kwargs)
        except Exception as e:
            print('JWT Decode Exception', e)
            abort(401)

    return wrapper