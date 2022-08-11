from flask import request
from flask_restx import Namespace, Resource

from implemented import user_service

auth_ns = Namespace('auth')
user_ns = Namespace('users')


@auth_ns.route('/')
class AuthUserView(Resource):

    def post(self):
        return user_service.post_auth(request.json)  # авторизация пользователя

    def put(self):
        return user_service.put_auth(request.json)  # обновление токена


@user_ns.route('/')
class UserView(Resource):

    def post(self):
        user_service.create(request.json)  # создание пользователя
        return '', 201
