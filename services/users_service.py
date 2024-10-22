from fastapi import HTTPException
from logging import raiseExceptions

from starlette.responses import JSONResponse

from common.responses import BadRequest, Unauthorized, Forbidden
from data.models import User, LoginData, UserResponse
from data.database import read_query, update_query, insert_query
import bcrypt
from mariadb import IntegrityError
import jwt
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime, timezone
import time

def get_users(token):  # Internal to be deleted

    data = read_query('''SELECT id, email, username, first_name, last_name, is_admin FROM users''')

    return (UserResponse.from_query_result(*row) for row in data)



def create_user(email: str, username: str, password: str, first_name: str, last_name: str ):

    hashed_p = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        generated_id = insert_query(
            '''INSERT INTO users(email, username, user_pass, first_name, last_name) VALUES (?,?,?,?,?);''',
            (email, username, hashed_p, first_name, last_name))

        return User(id = generated_id, email = email, username = username, password = password, first_name = first_name, last_name = last_name)
    except IntegrityError:

        return None # може за всички валидации да се върне различно съобщение за грешка към BadRequest
    

def login_user(username: str, password: str):

    user_data = read_query('''SELECT id, username, user_pass, is_admin FROM users WHERE username = ?;''', (username,))

    hashed_pass_db = user_data[0][2]

    if user_data and bcrypt.checkpw(password.encode('utf-8'), hashed_pass_db.encode('utf-8')):
        return user_data
    else:
        return None #Unauthorized('Incorrect username or password!')

def create_token(user_data):
    payload = {'user_id': user_data[0][0],
               'username': user_data[0][1],
           'is_admin': user_data[0][-1],
               'exp': datetime.now(timezone.utc) + timedelta(minutes=90)}

    token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

    return token

def decode_token(token):
    try:
        return jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail='Invalid token')

def is_admin(num: int):
    return True if num == 1 else False

def authenticate_user(token: str):

    the_blacklist = read_query('''select * from tokens_blacklist where token = ?;''', (token,))

    if not the_blacklist:
        # try:
            user_data =  decode_token(token)
            if user_exists(user_data):
                return user_data
            else:
                raise HTTPException(status_code=401, detail='Invalid user')
        # except jwt.InvalidTokenError as e:
        #     raise HTTPException(status_code=401, detail='Invalid token')

    raise HTTPException(status_code=401, detail='Invalid token')

def user_exists(user_data):
    return any(read_query('''SELECT * from users where id = ? and username = ?''',
                          (user_data['user_id'], user_data['username'] )))

load_dotenv()
secret_key = os.getenv('JWT_SECRET_KEY')

def blacklist_user(token: str):

    authorised_user = authenticate_user(token)

    if not isinstance(authorised_user, Unauthorized):

        insert_query('''insert into tokens_blacklist (tokens_blacklist.token) values (?);''', (token,))

        return f'User successfully logged out.'
    else:
        return False

# def get_user(username: str):
#
#     data = read_query('''select id, username, password, is_admin from users where username = ?;''', (username,))
#
#     return data


# def authorise_user(token: str):

#     # Check if token is in the blacklist
#     the_blacklist = read_query('''SELECT * FROM tokens_blacklist WHERE token = ?;''', (token,))

#     if the_blacklist:
#         # Token is in blacklist, raise Unauthorized exception
#         raise HTTPException(status_code=401, detail="Token is blacklisted")

#     try:
#         # Attempt to decode the JWT
#         return jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
#     except jwt.ExpiredSignatureError:
#         # Token has expired
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except jwt.InvalidTokenError:
#         # Token is invalid (signature or format error)
#         raise HTTPException(status_code=401, detail="Invalid token")
#     # except jwt.PyJWTError:
#     #     raise HTTPException(status_code=401, detail='Invalid token')
#     # the_blacklist = read_query('''select * from tokens_blacklist where token = ?;''', (token,))
#     #
#     # if not len(the_blacklist) > 0:
#     #     try:
#     #         return jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
#     #     except jwt.InvalidSignatureError as e:
#     #         raise HTTPException(status_code = 401)
#     # return False
#     # return Forbidden('You do not have access or your token is invalid!')