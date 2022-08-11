import hashlib

from constants import PWD_HASH_SALT, PWD_HASH_ITERATIONS
from dao.model.user import User


def get_hash(password):
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),  # Конвертирует пароль в бинарную строку
        PWD_HASH_SALT,
        PWD_HASH_ITERATIONS
    ).decode("utf-8", "ignore")


class UserDAO:
    def __init__(self, session):
        self.session = session

    def post_and_put_auth(self, username):
        return self.session.query(User).filter(User.username == username).first()

    def create(self, new_user):
        user = User(password=get_hash(new_user.get('password')),
                    username=new_user.get('username'),
                    role=new_user.get('role'))
        # user = User(**new_user)
        self.session.add(user)
        self.session.commit()
        return user
