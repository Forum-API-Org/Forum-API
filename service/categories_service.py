from data.database import insert_query, read_query, update_query
from data.models import Category
from common.responses import BadRequest


def get_categories():
    data = read_query('select * from categories order by id')

    return (Category(id=id, cat_name=cat_name, creator_id=creator_id, is_locked=is_locked, is_private=is_private) for id, cat_name, creator_id, is_locked, is_private in data)


def get_by_id(id: int):
    data = read_query('select * from categories where id = ?', (id,))

    return next((Category(id=id, cat_name=cat_name, creator_id=creator_id, is_locked=is_locked, is_private=is_private)
                 for id, cat_name, creator_id, is_locked, is_private in data), None)


# def exists(id: int):
#     return any(
#         read_query(
#             'select id, name from categories where id = ?',
#             (id,)))
#

def create(cat_name, creator_id):
    generated_id = insert_query(
        'insert into categories(cat_name, creator_id) values(?,?)',
        (cat_name, creator_id))
    return get_by_id(generated_id)


def check_if_locked(id: int):
    data = read_query('select is_locked from categories where id = ?', (id,))
    return next((is_locked for is_locked, in data), None)


def check_if_private(id: int):
    data = read_query('select is_private from categories where id = ?', (id,))
    return next((is_private for is_private, in data), None)


def lock(id: int):
    if check_if_locked(id):
        return BadRequest('Category is already locked.')
    update_query('update categories set is_locked = 1 where id = ?', (id,))


def make_private(id: int):
    if check_if_private(id):
        return BadRequest('Category is already private.')
    update_query('update categories set is_private = 1 where id = ?', (id,))


def unlock(id: int):
    if not check_if_locked(id):
        return BadRequest('Category is already unlocked.')
    update_query('update categories set is_locked = 0 where id = ?', (id,))


def make_public(id: int):
    if not check_if_private(id):
        return BadRequest('Category is already public.')
    update_query('update categories set is_private = 0 where id = ?', (id,))