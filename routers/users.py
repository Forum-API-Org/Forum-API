from fastapi import APIRouter, Body
from starlette import status

from services import users_service
from data.models import User, UserResponse, TEmail, TUsername, TPassword, TName
from common.responses import BadRequest

user_router = APIRouter(prefix = '/users', tags = ['Users'])
@user_router.get('')
def get_all_users():

    data = users_service.get_users()#response_model=List[schemas.User]

    return data

@user_router.post('/', response_model=User,
                  response_model_exclude={'password', 'is_admin'},
                  status_code=201)
def register_user(email: TEmail,
                  username: TUsername,
                  password: TPassword,
                  first_name: TName,
                  last_name: TName):

    user = users_service.create_user(email, username, password, first_name, last_name)

    return user or BadRequest(f'Username "{username}" and or email "{email}" is already taken.')

@user_router.post('/login')
def login_user(username: str, password: str):
    user = users_service.login_user(username, password)

    return user or BadRequest('Invalid username or password.')