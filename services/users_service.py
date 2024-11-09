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
    """
    Retrieves a list of all users.

    Returns:
        List[UserResponse]: A list of UserResponse objects representing all users.
    """
    data = read_query('''SELECT id, email, username, first_name, last_name, is_admin FROM users''')

    return (UserResponse.from_query_result(*row) for row in data)

def check_if_username_exists(attribute:str, message: str):
    """
    Checks if a username already exists in the database and raises an HTTPException if it does.

    Args:
        attribute (str): The username to check.
        message (str): The error message to include in the exception.

    Raises:
        HTTPException: If the username already exists.
    """
    if read_query('''select * from users where username = ?''', (attribute,)):
        raise HTTPException(status_code=400, detail=message)

def check_if_email_exists(attribute:str, message: str):
    """
    Checks if an email already exists in the database and raises an HTTPException if it does.

    Args:
        attribute (str): The email to check.
        message (str): The error message to include in the exception.

    Raises:
        HTTPException: If the email already exists.
    """
    if read_query('''select * from users where email = ?''', (attribute,)):
        raise HTTPException(status_code=400, detail=message)

def create_user(email: str, username: str, password: str, first_name: str, last_name: str )-> User:
    """
    Creates a new user with the provided details and returns the created User object.

    Args:
        email (str): The email of the user.
        username (str): The username of the user.
        password (str): The password of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.

    Returns:
        User: The created User object.
    """
    check_if_email_exists(email, 'Email already taken.')
    check_if_username_exists(username, 'Username already taken.')

    hashed_p = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # try:
    generated_id = insert_query(
        '''INSERT INTO users(email, username, user_pass, first_name, last_name) VALUES (?,?,?,?,?);''',
        (email, username, hashed_p, first_name, last_name))

    return User(id = generated_id, email = email, username = username, password = password, first_name = first_name, last_name = last_name)

    

def login_user(login_data):
    """
    Authenticates a user with the provided login data and returns the user data if successful.

    Args:
        login_data (LoginData): The login data containing username and password.

    Returns:
        Optional[User]: The authenticated user data if successful, None otherwise.
    """
    user_data = read_query('''SELECT id, username, user_pass, is_admin FROM users WHERE username = ?;''', (login_data.username,))



    if user_data and bcrypt.checkpw(login_data.password.encode('utf-8'), user_data[0][2].encode('utf-8')):
        return user_data
    else:
        return None

def create_token(user_data):
    """
    Creates a JWT token for the authenticated user.

    Args:
        user_data (User): The authenticated user data.

    Returns:
        str: The generated JWT token.
    """
    payload = {'user_id': user_data[0][0],
               'username': user_data[0][1],
           'is_admin': user_data[0][-1],
               'exp': datetime.now(timezone.utc) + timedelta(minutes=9000)} #за презентацията по-дълъг expiration да си подготвим от преди презентацията

    token = jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

    return token

def decode_token(token):
    """
    Decodes a JWT token and returns the payload.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Dict[str, Any]: The decoded payload.

    Raises:
        HTTPException: If the token is invalid.
    """
    try:
        return jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail='Invalid token')

def is_admin(num: int) -> bool:
    """
    Checks if a user is an admin based on the provided integer value.

    Args:
        num (int): The integer value representing admin status.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    return bool(num)

def authenticate_user(token: str):
    """
    Authenticates a user based on the provided token and returns the user data if successful.

    Args:
        token (str): The JWT token to authenticate.

    Returns:
        User: The authenticated user data.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    the_blacklist = read_query('''select * from tokens_blacklist where token = ?;''', (token,))

    if not the_blacklist:
        # try:
        user_data = decode_token(token)
        if user_exists(user_data):
            return user_data
        else:
            raise HTTPException(status_code=401, detail='Invalid user')
    else:
        raise HTTPException(status_code=401, detail='Invalid token')

def user_exists(user_data):
    """
    Checks if a user exists in the database based on the provided user data.

    Args:
        user_data (Dict[str, Any]): The user data containing user_id and username.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return any(read_query('''SELECT * from users where id = ? and username = ?''',
                          (user_data['user_id'], user_data['username'])))

def user_id_exists(user_id):
    """
    Checks if a user ID exists in the database.

    Args:
        user_id (int): The user ID to check.

    Returns:
        bool: True if the user ID exists, False otherwise.
    """
    return any(read_query('''SELECT * from users where id = ?''',
                          (user_id,)))

def get_user_by_id(id: int):
    """
    Checks if a user exists in the database based on the provided user ID.

    Args:
        id (int): The user ID to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return any(read_query('''SELECT * from users where id = ? ''',
                          (id,)))

load_dotenv()
secret_key = os.getenv('JWT_SECRET_KEY')

def blacklist_user(token: str):
    """
    Blacklists a token, effectively logging out the user.

    Args:
        token (str): The JWT token to blacklist.

    Returns:
        str: A message indicating the user has been logged out.

    Raises:
        HTTPException: If the token is invalid.
    """
    authorised_user = authenticate_user(token)

    if not isinstance(authorised_user, Unauthorized):
        insert_query('''insert into tokens_blacklist (tokens_blacklist.token) values (?);''', (token,))
        return f'User successfully logged out.'
    else:
        raise HTTPException(status_code=401, detail='Invalid token') #return False

def check_if_private(category_id):
    """
    Checks if a category is private based on the provided category ID.

    Args:
        category_id (int): The category ID to check.

    Returns:
        bool: True if the category is private, False otherwise.
    """
    return any(read_query('''select * from private_cat_access where category_id = ?''', (category_id,)))

def give_user_r_access(user_id, category_id):
    """
    Grants read access to a user for a specific category.

    Args:
        user_id (int): The user ID.
        category_id (int): The category ID.

    Returns:
        Optional[str]: A message indicating the access change, or None if the user already has read access.
    """
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
    """
    Grants write access to a user for a specific category.

    Args:
        user_id (int): The user ID.
        category_id (int): The category ID.

    Returns:
        Optional[str]: A message indicating the access change, or None if the user already has write access.
    """
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
    """
    Revokes access for a user from a specific category.

    Args:
        user_id (int): The user ID.
        category_id (int): The category ID.

    Returns:
        Optional[NoContent]: NoContent if the access was successfully revoked, None otherwise.
    """
    if any(read_query('''select user_id, category_id, access_type from private_cat_access
                            where user_id = ? and category_id = ? and (access_type = 1 or access_type = 0)''',
                (user_id, category_id))):
        insert_query('''delete from private_cat_access where user_id = ? and category_id = ? and (access_type = 1 or access_type = 0)''',
                (user_id, category_id))
        return NoContent()#f'Successfully delete access for user with id {user_id} for category with id {category_id}'
    else:
        return None

def view_privileged_users(category_id)-> list[UserAccessResponse]:
    """
    Retrieves a list of users with access to a specific category.

    Args:
        category_id (int): The category ID.

    Returns:
        List[UserAccessResponse]: A list of UserAccessResponse objects representing users with access to the category.
    """
    data = read_query('''select p.user_id, u.email, u.username, u.first_name, u.last_name, p.access_type 
                        from private_cat_access p
                        join users u on u.id = p.user_id
                        where category_id = ?;''', (category_id,))

    return [UserAccessResponse.from_query_result(*row) for row in data]