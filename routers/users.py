from fastapi import APIRouter
from service import users_service

user_router = APIRouter(prefix = '/users', tags = ['Users'])
@user_router.get('')
def get_all_users():

    data = users_service.get_users()#response_model=List[schemas.User]

    return data