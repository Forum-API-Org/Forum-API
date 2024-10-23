from typing import Annotated

from fastapi import APIRouter, Header
from starlette import status

from services import users_service
from data.models import User, UserResponse, TEmail, TUsername, TPassword, TName
from common.responses import BadRequest, Forbidden, Unauthorized

user_router = APIRouter(prefix = '/users', tags = ['Users'])
@user_router.get('', response_model= list[UserResponse])
def get_all_users(token: Annotated[str, Header()]):
    user_data = users_service.authenticate_user(token)

    if users_service.is_admin(user_data['is_admin']):
        data = users_service.get_users()#response_model=List[schemas.User]
        return data

    return Forbidden('Only admins can access this endpoint')

@user_router.post('/', response_model=User,
                  response_model_exclude={'password', 'is_admin'})
                  # status_code=status.HTTP_201_CREATED)
def register_user(email: TEmail,
                  username: TUsername,
                  password: TPassword,
                  first_name: TName,
                  last_name: TName):

    user = users_service.create_user(email, username, password, first_name, last_name)

    return user or BadRequest(f'Username "{username}" and or email "{email}" is already taken.')

@user_router.post('/login')
def login_user(username: str, password: str):
    user_data = users_service.login_user(username, password)

    if user_data:
        token = users_service.create_token(user_data)
        return {'token': token}
    else:
        return Unauthorized('Invalid username or password!')

@user_router.post('/logout')
def logout_user(token: Annotated[str, Header()]):

    result = users_service.blacklist_user(token)

    return result or BadRequest('Invalid token!')
