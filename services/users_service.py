from fastapi import HTTPException
from logging import raiseExceptions
from starlette.responses import JSONResponse
from common.responses import BadRequest, Unauthorized, Forbidden, NoContent
from data.models import User, LoginData, UserResponse, UserCategoryAccess, UserAccessResponse
from data.database import read_query, update_query, insert_query
import bcrypt
# from mariadb import IntegrityError
import jwt
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime, timezone
import time

def get_users():  # Internal to be deleted

    data = read_query('''SELECT id, email, username, first_name, last_name, is_admin FROM users''')

    return (UserResponse.from_query_result(*row) for row in data)

def check_if_username_exists(attribute:str, message: str):
    if read_query('''select * from users where username = ?''', (attribute,)):
        raise HTTPException(status_code=400, detail=message)

def check_if_email_exists(attribute:str, message: str):
    if read_query('''select * from users where email = ?''', (attribute,)):
        raise HTTPException(status_code=400, detail=message)

def create_user(email: str, username: str, password: str, first_name: str, last_name: str )-> User:

    check_if_email_exists(email, 'Email already taken.')
    check_if_username_exists(username, 'Username already taken.')

    hashed_p = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # try:
    generated_id = insert_query(
        '''INSERT INTO users(email, username, user_pass, first_name, last_name) VALUES (?,?,?,?,?);''',
        (email, username, hashed_p, first_name, last_name))

    return User(id = generated_id, email = email, username = username, password = password, first_name = first_name, last_name = last_name)
    # except IntegrityError:
    #
    #     return None # може за всички валидации да се върне различно съобщение за грешка към BadRequest
    

def login_user(login_data):
    # try:
    user_data = read_query('''SELECT id, username, user_pass, is_admin FROM users WHERE username = ?;''', (login_data.username,))

    # hashed_pass_db = user_data[0][2]

    if user_data and bcrypt.checkpw(login_data.password.encode('utf-8'), user_data[0][2].encode('utf-8')):
        return user_data
    else:
        return None #HTTPException(status_code=401, detail='Incorrect login data!')
    # except IndexError as e: #redo =>
    #     raise HTTPException(status_code=401, detail='Incorrect login data!')

def create_token(user_data):
    payload = {'user_id': user_data[0][0],
               'username': user_data[0][1],
           'is_admin': user_data[0][-1],
               'exp': datetime.now(timezone.utc) + timedelta(minutes=9000)} #за презентацията по-дълъг expiration да си подготвим от преди презентацията

    token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

    return token

def decode_token(token):
    try:
        return jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail='Invalid token')

def is_admin(num: int) -> bool:
    return bool(num)

def authenticate_user(token: str):

    the_blacklist = read_query('''select * from tokens_blacklist where token = ?;''', (token,))

    if not the_blacklist:
        # try:
        user_data = decode_token(token)
        if user_exists(user_data):
            return user_data
        else:
            raise HTTPException(status_code=401, detail='Invalid user')
        # except jwt.InvalidTokenError as e:
        #     raise HTTPException(status_code=401, detail='Invalid token')
    else:
        raise HTTPException(status_code=401, detail='Invalid token')

def user_exists(user_data):
    return any(read_query('''SELECT * from users where id = ? and username = ?''',
                          (user_data['user_id'], user_data['username'])))

def user_id_exists(user_id):
    return any(read_query('''SELECT * from users where id = ?''',
                          (user_id,)))

def get_user_by_id(id: int):
    return any(read_query('''SELECT * from users where id = ? ''',
                          (id,)))

load_dotenv()
secret_key = os.getenv('JWT_SECRET_KEY')

def blacklist_user(token: str):

    authorised_user = authenticate_user(token)

    if not isinstance(authorised_user, Unauthorized):
        insert_query('''insert into tokens_blacklist (tokens_blacklist.token) values (?);''', (token,))
        return f'User successfully logged out.'
    else:
        raise HTTPException(status_code=401, detail='Invalid token') #return False

def check_if_private(category_id):
    return any(read_query('''select * from private_cat_access where category_id = ?''', (category_id,)))

def give_user_r_access(user_id, category_id):

    if any(read_query('''select user_id, category_id, access_type from private_cat_access
                             where user_id = ? and category_id = ? and access_type = 0''',
                   (user_id, category_id))):
        return None
    
    elif any(read_query('''select user_id, category_id, access_type from private_cat_access
                        where user_id = ? and category_id = ? and access_type = 1''',
            (user_id, category_id))):
        update_query('''update private_cat_access set access_type = 0
                     where user_id = ? and category_id = ?''',
                (user_id, category_id))
        return f'Write access changed to read for user with id {user_id} for category with id {category_id}.'
    else:
        insert_query('''insert into private_cat_access (private_cat_access.user_id, private_cat_access.category_id, private_cat_access.access_type) 
                            values(?,?, 0)''',
                    (user_id, category_id))

        return f'Read access for category with id {category_id} has been given to user with id {user_id}.'

def give_user_w_access(user_id, category_id):


    if any(read_query('''select user_id, category_id, access_type from private_cat_access
                             where user_id = ? and category_id = ? and access_type = 1''',
                   (user_id, category_id))):
        return None

    elif any(read_query('''select user_id, category_id, access_type from private_cat_access
                            where user_id = ? and category_id = ? and access_type = 0''',
                (user_id, category_id))):
        update_query('''update private_cat_access set access_type = 1
                     where user_id = ? and category_id = ?''',
                (user_id, category_id))
        return f'Read access changed to write for user with id {user_id} for category with id {category_id}.'
    
    else:
        insert_query('''insert into private_cat_access (private_cat_access.user_id, private_cat_access.category_id, private_cat_access.access_type) 
                            values(?,?, 0)''',
                    (user_id, category_id))

        return f'Write access for category with id {category_id} has been given to user with id {user_id}.'

def revoke_access(user_id, category_id):

    if any(read_query('''select user_id, category_id, access_type from private_cat_access
                            where user_id = ? and category_id = ? and (access_type = 1 or access_type = 0)''',
                (user_id, category_id))):
        insert_query('''delete from private_cat_access where user_id = ? and category_id = ? and (access_type = 1 or access_type = 0)''',
                (user_id, category_id))
        return NoContent()#f'Successfully delete access for user with id {user_id} for category with id {category_id}'
    else:
        return None

def view_privileged_users(category_id)-> list[UserAccessResponse]:

    data = read_query('''select p.user_id, u.email, u.username, u.first_name, u.last_name, p.access_type 
                        from private_cat_access p
                        join users u on u.id = p.user_id
                        where category_id = ?;''', (category_id,))

    return [UserAccessResponse.from_query_result(*row) for row in data]