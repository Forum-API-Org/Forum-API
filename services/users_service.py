from common.responses import BadRequest, Unauthorized, Forbidden
from data.models import User, LoginData, UserResponse
from data.database import read_query, update_query, insert_query
import bcrypt
from mariadb import IntegrityError
import jwt
from dotenv import load_dotenv
import os

def get_users():  # Internal to be deleted

    data = read_query('''select id, email, username, first_name, last_name, is_admin from users''')

    return (UserResponse.from_query_result(*row) for row in data)

# def get_user(username: str):
#
#     data = read_query('''select id, username, password, is_admin from users where username = ?;''', (username,))
#
#     return data


def create_user(email: str, username: str, password: str, first_name: str, last_name: str ):
    # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    word = b"password"
    hashed = bcrypt.hashpw(word, bcrypt.gensalt())
    try:
        generated_id = insert_query(
            '''INSERT INTO users(email, username, user_pass, first_name, last_name) VALUES (?,?,?,?,?);''',
            (email, username, hashed, first_name, last_name))

        return User(id = generated_id, email = email, username = username, password = password, first_name = first_name, last_name = last_name)
    except IntegrityError:

        return None # може за всички валидации да се върне различно съобщение за грешка към BadRequest
    

def login_user(username: str, password: str):

    data = read_query('''select * from users where username = ?;''', (username,))

    if not data:
        return Unauthorized('Incorrect username or password!')

    # user_data = User.from_query_result(*data)
    x = data[0][0]
    y = data[0][-1]

    word = b"password"
    # hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if bcrypt.checkpw(word, data[0][3].encode('utf-8')):
        payload = {'user_id': data[0][0],
                   'is_admin': data[0][-1]}

        token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')
        return token

        # return User(id = user.id,
        #                     email = user.email,
        #                     username = user.username,
        #                     password = password,
        #                     first_name = user.first_name,
        #                     last_name = user.last_name,
        #                     is_admin = user.is_admin)



def authorise_user(token: str):

    the_blacklist = read_query('''select * from tokens_blacklist where token = ?;''', (token,))

    if not the_blacklist:
        return jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])

    return Forbidden('You do not have access or your token is invalid!')

load_dotenv()
secret_key = os.getenv('JWT_SECRET_KEY')

def blacklist_user(token: str):

    insert_query('''insert into tokens_blacklist (token) values '?';''', (token,))

    # return f'User successfully logged out.'