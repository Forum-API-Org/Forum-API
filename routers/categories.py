from fastapi import APIRouter, Header
from services.users_service import *
from data.models import CategoryResponse, CategoryCreation
from common.responses import NotFound, BadRequest
from services import categories_service
from typing import Annotated, List

cat_router = APIRouter(prefix="/categories", tags=["Categories"])


@cat_router.get('/', response_model=List[CategoryResponse])
def get_all_categories(token: Annotated[str, Header()]):

    """
    Get all categories from the database.

    :param token:  JWT token for authentication.
    :return:  List of CategoryResponse objects.
    """

    authenticate_user(token)

    data = categories_service.get_categories()

    return data


@cat_router.get('/{id}', response_model=CategoryResponse)
def get_category_by_id(id: int, token: Annotated[str, Header()]):

    """
    Get a category by its ID.

    :param id:  The ID of the category. Must exist in the database.
    :param token:  JWT token for authentication.
    :return:  CategoryResponse object.
    """

    user = authenticate_user(token)

    if not categories_service.exists(id):
        return NotFound('Category not found')

    if categories_service.check_if_private(id):
        access = categories_service.check_user_access(user['user_id'], id)

        if access is None and not is_admin(user['is_admin']):
            return Forbidden('Category is private')

    category = categories_service.get_by_id(id)

    return category


@cat_router.post('/')
def create_category(name: CategoryCreation, token: Annotated[str, Header()]):

    """
    Create a new category. Only admins can create categories.

    :param name:  The name of the category. Can't be empty. Should be unique.
    :param token:  JWT token for authentication.
    :return:  The created CategoryResponse object.
    """

    user = authenticate_user(token)

    if not name.cat_name:
        return BadRequest('Category name cannot be empty')

    if categories_service.cat_name_exists(name.cat_name):
        return BadRequest('Category name already exists')

    if not is_admin(user['is_admin']):
        return Forbidden('Only admins can create categories')

    category = categories_service.create(name.cat_name, user['user_id'])

    return category


@cat_router.put('/lock/{id}')
def lock_category(id: int, token: Annotated[str, Header()]):

    """
    Lock a category. Only admins can lock categories. Category must exist. Category must not be locked.

    :param id:  The ID of the category.
    :param token:  JWT token for authentication.
    :return: CategoryResponse object.
    """

    user = authenticate_user(token)

    if not is_admin(user['is_admin']):
        return Forbidden('Only admins can lock categories')

    if not categories_service.exists(id):
        return NotFound('Category not found')

    result = categories_service.lock(id)

    return result


@cat_router.put('/make_private/{id}')
def make_category_private(id: int, token: Annotated[str, Header()]):

    """
    Make a category private. Only admins can make categories private. Category must exist. Category must not be private.

    :param id:  The ID of the category.
    :param token:  JWT token for authentication.
    :return:  CategoryResponse object.
    """

    user = authenticate_user(token)

    if not is_admin(user['is_admin']):
        return Forbidden('Only admins can make categories private')

    if not categories_service.exists(id):
        return NotFound('Category not found')

    result = categories_service.make_private(id)

    return result


@cat_router.put('/unlock/{id}')
def unlock_category(id: int, token: Annotated[str, Header()]):

    """
    Unlock a category. Only admins can unlock categories. Category must exist. Category must be locked.

    :param id:  The ID of the category.
    :param token:  JWT token for authentication.
    :return:  CategoryResponse object.
    """

    user = authenticate_user(token)

    if not is_admin(user['is_admin']):
        return Forbidden('Only admins can unlock categories')

    if not categories_service.exists(id):
        return NotFound('Category not found')

    result = categories_service.unlock(id)

    return result


@cat_router.put('/make_public/{id}')
def make_category_public(id: int, token: Annotated[str, Header()]):

    """
    Make a category public.
    Only admins can make categories public. Category must exist. Category must be private. Remove all private access.

    :param id:  The ID of the category.
    :param token:  JWT token for authentication.
    :return:  CategoryResponse object.
    """

    user = authenticate_user(token)

    if not is_admin(user['is_admin']):
        return Forbidden('Only admins can make categories public')

    if not categories_service.exists(id):
        return NotFound('Category not found')

    result = categories_service.make_public(id)

    return result
