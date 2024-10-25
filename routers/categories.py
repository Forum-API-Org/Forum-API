from fastapi import APIRouter, Header
from services.users_service import *
from data.models import CategoryResponse, TopicResponse
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
    authenticate_user(token)

    category_response = categories_service.get_by_id(id)

    if category_response is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return category_response


@cat_router.post('/')
def create_category(cat_name: str, token: Annotated[str, Header()]):
    user = authenticate_user(token)
    category = categories_service.create(cat_name, user['user_id'])

    return category


@cat_router.put('/lock/{id}')
def lock_category(id: int, token: Annotated[str, Header()]):
    user = authenticate_user(token)
    if not (is_admin(user['is_admin']) or categories_service.is_owner(user['user_id'], id)):
        return BadRequest('Only admins and category owners can lock categories')
    result = categories_service.lock(id)
    return result


@cat_router.put('/make_private/{id}')
def make_category_private(id: int, token: Annotated[str, Header()]):
    user = authenticate_user(token)
    if not (is_admin(user['is_admin']) or categories_service.is_owner(user['user_id'], id)):
        return BadRequest('Only admins and category owners can make categories private')
    result = categories_service.make_private(id)
    return result


@cat_router.put('/unlock/{id}')
def unlock_category(id: int, token: Annotated[str, Header()]):
    user = authenticate_user(token)
    if not (is_admin(user['is_admin']) or categories_service.is_owner(user['user_id'], id)):
        return BadRequest('Only admins and category owners can unlock categories')
    result = categories_service.unlock(id)
    return result


@cat_router.put('/make_public/{id}')
def make_category_public(id: int, token: Annotated[str, Header()]):
    user = authenticate_user(token)
    if not (is_admin(user['is_admin']) or categories_service.is_owner(user['user_id'], id)):
        return BadRequest('Only admins and category owners can make categories public')
    result = categories_service.make_public(id)
    return result
