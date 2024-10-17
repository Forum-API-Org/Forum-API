from common.responses import BadRequest
from data.models import User, LoginData, UserResponse
from data.database import read_query, update_query, insert_query
import bcrypt
from mariadb import IntegrityError
import jwt
from dotenv import load_dotenv
import os

def get_users():  # Internal to be deleted

    data = read_query('''select * from users''')

    return (User.from_query_result(*row) for row in data)


def create_user(email: str, username: str, password: str, first_name: str, last_name: str ):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        generated_id = insert_query(
            '''INSERT INTO users(email, username, user_pass, first_name, last_name) VALUES (?,?,?,?,?);''',
            (email, username, hashed_password, first_name, last_name))

        return User(id = generated_id, email = email, username = username, password = '', first_name = first_name, last_name = last_name)
    except IntegrityError as e:

        return None # може за всички валидации да се върне различно съобщение за грешка към BadRequest
    

def login_user(username: str, password: str) -> UserResponse:
    data = read_query('''select * from users where username = ?''', (username,))
    if not data:
        return None

    user = User.from_query_result(*data[0])

    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return UserResponse(id = user.id,
                            email = user.email,
                            username = user.username,
                            first_name = user.first_name,
                            last_name = user.last_name,
                            is_admin = user.is_admin)
    else:
        return None

load_dotenv()
secret_key = os.getenv('JWT_SECRET_KEY')
# Now endpoint token/login ? 

def create_token(data: dict):
    token = jwt.encode(data, secret_key, algorithm='HS256')
    return token