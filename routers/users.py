from typing import Annotated
from fastapi import APIRouter, Header, HTTPException
from starlette import status

from services import users_service, categories_service
from data.models import User, UserResponse, TEmail, TUsername, TPassword, TName, LoginData, UserCategoryAccess, UserAccessResponse
from common.responses import BadRequest, Forbidden, Unauthorized, NotFound

user_router = APIRouter(prefix='/users', tags=['Users'])


@user_router.get('/', response_model=list[UserResponse])
def get_all_users(token: Annotated[str, Header()]):
    user_data = users_service.authenticate_user(token)

    if users_service.is_admin(user_data['is_admin']):
        data = users_service.get_users()#response_model=List[schemas.User]
        return data

    return Forbidden('Only admins can access this endpoint')


@user_router.post('/', response_model=User,
                  response_model_exclude={'password', 'is_admin'},
                  status_code=status.HTTP_201_CREATED)
def register_user(user: User):

    user = users_service.create_user(user.email,
                                     user.username,
                                     user.password,
                                     user.first_name,
                                     user.last_name)

    return user

@user_router.post('/login')
def login_user(login_data: LoginData):
    user_data = users_service.login_user(login_data)

    if user_data:
        token = users_service.create_token(user_data)
        return {'token': token}
    else:
        return Unauthorized('Invalid username or password!')

@user_router.post('/logout')
def logout_user(token: Annotated[str, Header()]):
    try:
        result = users_service.blacklist_user(token)
        return {'message': result}
    except HTTPException as e:
        return BadRequest(e.detail)

@user_router.put('/read_access')
def give_user_read_access(user_category_id: UserCategoryAccess, token: Annotated[str, Header()]): # 0 write, 1 read

    if not categories_service.exists(user_category_id.category_id):
        return NotFound('Category does not exist!')

    if not users_service.check_if_private(user_category_id.category_id):
        return BadRequest(f'Category {user_category_id.category_id} is not private.')

    if not users_service.user_id_exists(user_category_id.user_id):
        return NotFound(f'User with id {user_category_id.user_id} does not exist!')

    user_data = users_service.authenticate_user(token)

    if users_service.is_admin(user_data['is_admin']):
        data = users_service.give_user_r_access(user_category_id.user_id, user_category_id.category_id)#response_model=List[schemas.User]
        return data or BadRequest(f'User with id {user_category_id.user_id} already has read access for category with id {user_category_id.category_id}!')

    return Forbidden('Only admins can access this endpoint')

@user_router.put('/write_access')
def give_user_write_access(user_category_id: UserCategoryAccess, token: Annotated[str, Header()]): # 0 write, 1 read

    if not categories_service.exists(user_category_id.category_id):
        return NotFound('Category does not exist!')

    if not users_service.check_if_private(user_category_id.category_id):
        return BadRequest(f'Category {user_category_id.category_id} is not private.')

    if not users_service.user_id_exists(user_category_id.user_id):
        return NotFound(f'User with id {user_category_id.user_id} does not exist!')

    user_data = users_service.authenticate_user(token)

    if users_service.is_admin(user_data['is_admin']):
        data = users_service.give_user_w_access(user_category_id.user_id, user_category_id.category_id)#response_model=List[schemas.User]
        return data or BadRequest(f'User with id {user_category_id.user_id} already has write access for category with id {user_category_id.category_id}!')

    return Forbidden('Only admins can access this endpoint')

@user_router.delete('/revoke_access')
def revoke_user_access(token: Annotated[str, Header()],
                       user_category_id: UserCategoryAccess,
                       status_code = status.HTTP_204_NO_CONTENT):

    if not categories_service.exists(user_category_id.category_id):
        return NotFound('Category does not exist!')

    if not users_service.check_if_private(user_category_id.category_id):
        return BadRequest(f'Category {user_category_id.category_id} is not private.')

    if not users_service.user_id_exists(user_category_id.user_id):
        return NotFound(f'User with id {user_category_id.user_id} does not exist!')

    user_data = users_service.authenticate_user(token)

    if users_service.is_admin(user_data['is_admin']):
        data = users_service.revoke_access(user_category_id.user_id, user_category_id.category_id)#response_model=List[schemas.User]
        return data or BadRequest(f'User with id {user_category_id.user_id} has no existing access for category with id {user_category_id.category_id}!')

    return Forbidden('Only admins can access this endpoint')

@user_router.get('/privileges', response_model=list[UserAccessResponse],
                  response_model_exclude={'password', 'is_admin'})
def view_privileged_users(token: Annotated[str, Header()], category_id):

    if not categories_service.exists(category_id):
        return NotFound('Category does not exist!')

    if not users_service.check_if_private(category_id):
        return BadRequest(f'Category {category_id} is not private.')

    user_data = users_service.authenticate_user(token)

    if users_service.is_admin(user_data['is_admin']):
        data = users_service.view_privileged_users(category_id)
        return data

    return Forbidden('Only admins can access this endpoint')

