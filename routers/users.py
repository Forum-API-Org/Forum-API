from fastapi import APIRouter
from services import users_service
# from data.models import User
from common.responses import BadRequest

user_router = APIRouter(prefix = '/users', tags = ['Users'])
@user_router.get('')
def get_all_users():

    data = users_service.get_users()#response_model=List[schemas.User]

    return data

@user_router.post('/register')
def register_user(email: str, username: str, password: str, first_name: str, last_name: str):
    #if email validation
    #if username validation
    # decide if password validation
    #first and last name validations (containt only strings)
    user = users_service.create_user(email, username, password, first_name, last_name)

    return user or BadRequest(f'Username "{username}" is already taken.')

@user_router.post('/login')
def login_user(username: str, password: str):
    user = users_service.login_user(username, password)

    return user or BadRequest('Invalid username or password.')