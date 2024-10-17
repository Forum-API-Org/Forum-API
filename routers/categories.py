from fastapi import APIRouter
from services import categories_service
from common.responses import NotFound, BadRequest

cat_router = APIRouter(prefix="/categories", tags=["Categories"])


@cat_router.get('')
def get_all_categories():

    data = categories_service.get_categories()

    return data


@cat_router.get('/{id}')
def get_category_by_id(id: int):
    category = categories_service.get_by_id(id)

    if category is None:
        return NotFound()
    else:
        return category


@cat_router.post('')
def create_category(cat_name: str, creator_id: int):
    category = categories_service.create(cat_name, creator_id)

    return category


@cat_router.put('/lock/{id}')
def lock_category(id: int):
    categories_service.lock(id)
    return get_category_by_id(id) or BadRequest('Category is already locked.')


@cat_router.put('/make_private/{id}')
def make_category_private(id: int):
    categories_service.make_private(id)
    return get_category_by_id(id)


@cat_router.put('/unlock/{id}')
def unlock_category(id: int):
    categories_service.unlock(id)
    return get_category_by_id(id)


@cat_router.put('/make_public/{id}')
def make_category_public(id: int):
    categories_service.make_public(id)
    return get_category_by_id(id)

