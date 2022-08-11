import calendar
import datetime
import hashlib
from config import Config
import jwt
from flask import abort

from constants import PWD_HASH_SALT, PWD_HASH_ITERATIONS, ALGO
from dao.user import UserDAO


class UserService:
    def __init__(self, dao: UserDAO):
        self.dao = dao

    def get_hash(self, password):
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),  # Конвертирует пароль в бинарную строку
            PWD_HASH_SALT,
            PWD_HASH_ITERATIONS
        ).decode("utf-8", "ignore")

    def create(self, new_user):
        return self.dao.create(new_user)

    def post_auth(self, data):
        input_username = data.get('username', None)
        input_password = data.get('password', None)
        if None in [input_username, input_password]:
            abort(400)
        user_database = self.dao.post_and_put_auth(input_username)
        if user_database is None:
            print(user_database)
            return {"error": "Неверные учётные данные"}, 401
        password = self.get_hash(input_password)  # хеш пароля sha256

        if password != user_database.password:
            print(password)
            print(user_database.password)
            return {"error": "Неверные учётные данные"}, 401

        data = {"username": user_database.username,
                "role": user_database.role  # заносим данные из таблицы в переменную
                }

        sec30 = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        data["exp"] = calendar.timegm(sec30.timetuple())
        access_token = jwt.encode(data, Config.SECRET_HERE, algorithm=ALGO)
        days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data["exp"] = calendar.timegm(days130.timetuple())
        refresh_token = jwt.encode(data, Config.SECRET_HERE, algorithm=ALGO)
        return {"access_token": access_token, "refresh_token": refresh_token}, 201

    def put_auth(self, req):
        refresh_token = req.get("refresh_token")
        if refresh_token is None:
            abort(400)
        elif not self.check_token(refresh_token):  # проверка токена
            abort(400)
        try:
            data = jwt.decode(jwt=refresh_token, key=Config.SECRET_HERE, algorithms=[ALGO])
        except:
            abort(400)

        username_database = data.get('username')

        username = self.dao.post_and_put_auth(username_database)  # получим фильтрацию из dao

        data = {"username": username.username,
                "role": username.role  # заносим данные из таблицы в переменную
                }

        sec30 = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
        data["exp"] = calendar.timegm(sec30.timetuple())
        access_token = jwt.encode(data, Config.SECRET_HERE, algorithm=ALGO)
        days130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data["exp"] = calendar.timegm(days130.timetuple())
        refresh_token = jwt.encode(data, Config.SECRET_HERE, algorithm=ALGO)
        return {"access_token": access_token, "refresh_token": refresh_token}, 201

    def check_token(self, refresh_token):
        try:
            jwt.decode(refresh_token, Config.SECRET_HERE, algorithms=[ALGO])
            return True
        except:
            return False