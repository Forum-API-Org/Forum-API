from typing import Annotated
from fastapi import APIRouter, Header, HTTPException
from starlette import status

from services import users_service, categories_service
from data.models import User, UserResponse, TEmail, TUsername, TPassword, TName, LoginData, UserCategoryAccess, UserAccessResponse
from common.responses import BadRequest, Forbidden, Unauthorized, NotFound

user_router = APIRouter(prefix='/users', tags=['Users'])


@user_router.get('/', response_model=list[UserResponse])
def get_all_users(token: Annotated[str, Header()]):
    """
    Retrieves a list of all users. Only accessible by admins.

    Args:
        token (Annotated[str, Header()]): The JWT token for authentication.

    Returns:
        List[UserResponse]: A list of UserResponse objects representing all users.
    """
    user_data = users_service.authenticate_user(token)

    if users_service.is_admin(user_data['is_admin']):
        data = users_service.get_users()#response_model=List[schemas.User]
        return data

    return Forbidden('Only admins can access this endpoint')


@user_router.post('/', response_model=User,
                  response_model_exclude={'password', 'is_admin'},
                  status_code=status.HTTP_201_CREATED)
def register_user(user: User):
    """
    Registers a new user with the provided details.

    Args:
        user (User): The user details.

    Returns:
        User: The created User object.
    """
    user = users_service.create_user(user.email,
                                     user.username,
                                     user.password,
                                     user.first_name,
                                     user.last_name)

    return user

@user_router.post('/login')
def login_user(login_data: LoginData):
    """
    Authenticates a user with the provided login data and returns a JWT token if successful.

    Args:
        login_data (LoginData): The login data containing username and password.

    Returns:
        Dict[str, str]: A dictionary containing the JWT token if authentication is successful.
    """
    user_data = users_service.login_user(login_data)

    if user_data:
        token = users_service.create_token(user_data)
        return {'token': token}
    else:
        return Unauthorized('Invalid username or password!')

@user_router.post('/logout')
def logout_user(token: Annotated[str, Header()]):
    """
    Logs out a user by blacklisting the provided JWT token.

    Args:
        token (Annotated[str, Header()]): The JWT token to blacklist.

    Returns:
        Dict[str, str]: A message indicating the user has been logged out.
    """
    try:
        result = users_service.blacklist_user(token)
        return {'message': result}
    except HTTPException as e:
        return BadRequest(e.detail)

@user_router.put('/read_access')
def give_user_read_access(user_category_id: UserCategoryAccess, token: Annotated[str, Header()]): # 0 write, 1 read
    """
    Grants read access to a user for a specific category. Only accessible by admins.

    Args:
        user_category_id (UserCategoryAccess): The user and category details.
        token (Annotated[str, Header()]): The JWT token for authentication.

    Returns:
        Union[str, BadRequest, Forbidden]: A message indicating the access change, or an error response.
    """
    #if UserCategoryAccess.user_id == 1:
    #    return BadRequest('User is admin so he already has read/write access by default!')
    if not categories_service.exists(user_category_id.category_id):
        return NotFound('Category does not exist!')

    if not categories_service.check_if_private(user_category_id.category_id):
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
    """
    Grants write access to a user for a specific category. Only accessible by admins.

    Args:
        user_category_id (UserCategoryAccess): The user and category details.
        token (Annotated[str, Header()]): The JWT token for authentication.

    Returns:
        Union[str, BadRequest, Forbidden]: A message indicating the access change, or an error response.
    """
    if not categories_service.exists(user_category_id.category_id):
        return NotFound('Category does not exist!')

    if not categories_service.check_if_private(user_category_id.category_id):
        return BadRequest(f'Category {user_category_id.category_id} is not private.')

    if not users_service.user_id_exists(user_category_id.user_id):
        return NotFound(f'User with id {user_category_id.user_id} does not exist!')

    user_data = users_service.authenticate_user(token)

    if users_service.is_admin(user_data['is_admin']):
        data = users_service.give_user_w_access(user_category_id.user_id, user_category_id.category_id)#response_model=List[schemas.User]
        return data or BadRequest(f'User with id {user_category_id.user_id} already has write access for category with id {user_category_id.category_id}!')

    return Forbidden('Only admins can access this endpoint')

@user_router.delete('/revoke_access', status_code=status.HTTP_204_NO_CONTENT)
def revoke_user_access(token: Annotated[str, Header()],
                       user_category_id: UserCategoryAccess
                       ):
    """
    Revokes access for a user from a specific category. Only accessible by admins.

    Args:
        token (Annotated[str, Header()]): The JWT token for authentication.
        user_category_id (UserCategoryAccess): The user and category details.
        status_code (int, optional): The status code to return. Defaults to status.HTTP_204_NO_CONTENT.

    Returns:
        Union[NoContent, BadRequest, Forbidden]: A message indicating the access revocation, or an error response.
    """
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
    """
    Retrieves a list of users with access to a specific category. Only accessible by admins.

    Args:
        token (Annotated[str, Header()]): The JWT token for authentication.
        category_id (int): The category ID.

    Returns:
        List[UserAccessResponse]: A list of UserAccessResponse objects representing users with access to the category.
    """
    if not categories_service.exists(category_id):
        return NotFound('Category does not exist!')

    if not users_service.check_if_private(category_id):
        return BadRequest(f'Category {category_id} is not private.')

    user_data = users_service.authenticate_user(token)

    if users_service.is_admin(user_data['is_admin']):
        data = users_service.view_privileged_users(category_id)
        return data

    return Forbidden('Only admins can access this endpoint')

