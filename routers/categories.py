from fastapi import APIRouter

from common.responses import NotFound, BadRequest
from services import categories_service

cat_router = APIRouter(prefix="/categories", tags=["Categories"])


@cat_router.get('/')
def get_all_categories():

    data = categories_service.get_categories()

    return data


@cat_router.get('/{id}')
def get_category_by_id(id: int):
    category = categories_service.get_by_id(id)
    topics = categories_service.view_topics(id)

    if category is None:
        return NotFound()
    else:
        return {
            "category": category,
            "topics": topics
        }


@cat_router.post('/')
def create_category(cat_name: str, creator_id: int):
    category = categories_service.create(cat_name, creator_id)

    return category


@cat_router.put('/lock/{id}')
def lock_category(id: int):
    result = categories_service.lock(id)
    return result


@cat_router.put('/make_private/{id}')
def make_category_private(id: int):
    result = categories_service.make_private(id)
    return result


@cat_router.put('/unlock/{id}')
def unlock_category(id: int):
    result = categories_service.unlock(id)
    return result


@cat_router.put('/make_public/{id}')
def make_category_public(id: int):
    result = categories_service.make_public(id)
    return result

