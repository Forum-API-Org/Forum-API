from fastapi import APIRouter, Header
from services.users_service import *
from data.models import CategoryResponse, TopicResponse, CategoryCreation
from common.responses import NotFound, BadRequest
from services import categories_service
from typing import Annotated, List

cat_router = APIRouter(prefix="/categories", tags=["Categories"])


@cat_router.get('/', response_model=List[CategoryResponse])
def get_all_categories(token: Annotated[str, Header()]):

    authenticate_user(token)

    data = categories_service.get_categories()

    return data


@cat_router.get('/{id}', response_model=CategoryResponse)
def get_category_by_id(id: int, token: Annotated[str, Header()]):

    user = authenticate_user(token)

    if not categories_service.exists(id):
        return BadRequest('Category not found')

    if categories_service.check_if_private(id):
        access = categories_service.check_user_access(user['user_id'], id)

        if access is None and not is_admin(user['is_admin']):
            return BadRequest('Category is private')

    category = categories_service.get_by_id(id)

    return category


@cat_router.post('/')
def create_category(name: CategoryCreation, token: Annotated[str, Header()]):

    user = authenticate_user(token)

    if categories_service.cat_name_exists(name.cat_name):
        return BadRequest('Category name already exists')

    if not is_admin(user['is_admin']):
        return BadRequest('Only admins can create categories')

    category = categories_service.create(name.cat_name, user['user_id'])

    return category


@cat_router.put('/lock/{id}')
def lock_category(id: int, token: Annotated[str, Header()]):

    user = authenticate_user(token)

    if not is_admin(user['is_admin']):
        return BadRequest('Only admins can lock categories')

    if not categories_service.exists(id):
        return NotFound('Category not found')

    result = categories_service.lock(id)

    return result


@cat_router.put('/make_private/{id}')
def make_category_private(id: int, token: Annotated[str, Header()]):

    user = authenticate_user(token)

    if not is_admin(user['is_admin']):
        return BadRequest('Only admins can make categories private')

    if not categories_service.exists(id):
        return NotFound('Category not found')

    result = categories_service.make_private(id)

    return result


@cat_router.put('/unlock/{id}')
def unlock_category(id: int, token: Annotated[str, Header()]):

    user = authenticate_user(token)

    if not is_admin(user['is_admin']):
        return BadRequest('Only admins can unlock categories')

    if not categories_service.exists(id):
        return NotFound('Category not found')

    result = categories_service.unlock(id)

    return result


@cat_router.put('/make_public/{id}')
def make_category_public(id: int, token: Annotated[str, Header()]):

    user = authenticate_user(token)

    if not is_admin(user['is_admin']):
        return BadRequest('Only admins can make categories public')

    if not categories_service.exists(id):
        return NotFound('Category not found')

    result = categories_service.make_public(id)

    return result
