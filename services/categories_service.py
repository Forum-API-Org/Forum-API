from data.database import insert_query, read_query, update_query
from data.models import CategoryResponse, TopicResponse
from common.responses import BadRequest


def get_categories():

    """
    Get all categories from the database.

    :return: List of CategoryResponse objects.
    """

    data = read_query('select cat_name, creator_id, is_locked, is_private from categories order by id')

    return [(CategoryResponse(cat_name=cat_name,
                              creator_id=creator_id,
                              is_locked=is_locked,
                              is_private=is_private))
            for cat_name,
            creator_id,
            is_locked,
            is_private
            in data]


def view_topics(id: int):

    """
    Get all topics for a category.

    :param id:  The ID of the category.
    :return:  List of TopicResponse objects.
    """

    data = read_query('''select top_name, user_id, topic_date, is_locked, best_reply_id
                             from topics
                             where category_id = ?''', (id,))

    if not data:
        return []

    return [(TopicResponse.from_query_result(top_name=top_name,
                                             user_id=user_id,
                                             topic_date=str(topic_date),
                                             is_locked=is_locked,
                                             best_reply_id=best_reply_id))
            for top_name, user_id, topic_date, is_locked, best_reply_id in data]


def get_by_id(id: int):

    """
    Get a category by its ID.

    :param id:  The ID of the category.
    :return:  CategoryResponse object.
    """

    data = read_query('select cat_name, creator_id, is_locked, is_private from categories where id = ?', (id,))

    if not data:
        return None

    cat_name, creator_id, is_locked, is_private = data[0]

    topics = view_topics(id)

    return (CategoryResponse(
        cat_name=cat_name,
        creator_id=creator_id,
        is_locked=is_locked,
        is_private=is_private,
        topics=topics
    ))


def exists(id: int):

    """
    Check if a category exists.

    :param id:  The ID of the category.
    :return:  True if the category exists, False otherwise.
    """

    return any(
        read_query(
            'select id, cat_name from categories where id = ?',
            (id,)))


def cat_name_exists(cat_name: str):

    """
    Check if a category name already exists.

    :param cat_name:  The name of the category.
    :return:  True if the category name exists, False otherwise.
    """

    return any(
        read_query(
            'select id, cat_name from categories where cat_name = ?',
            (cat_name,)))


def create(cat_name, creator_id):

    """
    Create a new category.

    :param cat_name:  The name of the category.
    :param creator_id:  The ID of the user who created the category.
    :return:  The created Category object.
    """

    generated_id = insert_query(
        'insert into categories(cat_name, creator_id) values(?,?)',
        (cat_name, creator_id))
    return get_by_id(generated_id)


def check_if_locked(id: int):

    """
    Check if a category is locked.

    :param id:  The ID of the category.
    :return:  True if the category is locked, False otherwise.
    """

    data = read_query('select is_locked from categories where id = ?', (id,))
    return bool(data[0][0])


def check_if_private(id: int):

    """
    Check if a category is private.

    :param id:  The ID of the category.
    :return:  True if the category is private, False otherwise.
    """

    data = read_query('select is_private from categories where id = ?', (id,))
    return bool(data[0][0])


def lock(id: int):

    """
    Lock a category. Must not be locked already.

    :param id:  The ID of the category.
    :return:  The locked Category object.
    """

    if check_if_locked(id):
        return BadRequest('Category is already locked.')
    update_query('update categories set is_locked = 1 where id = ?', (id,))
    return get_by_id(id)


def make_private(id: int):

    """
    Make a category private. Must not be private already.

    :param id:  The ID of the category.
    :return:  The private Category object.
    """

    if check_if_private(id):
        return BadRequest('Category is already private.')
    update_query('update categories set is_private = 1 where id = ?', (id,))
    return get_by_id(id)


def unlock(id: int):

    """
    Unlock a category. Must be locked already.

    :param id:  The ID of the category.
    :return:  The unlocked Category object.
    """

    if not check_if_locked(id):
        return BadRequest('Category is already unlocked.')
    update_query('update categories set is_locked = 0 where id = ?', (id,))
    return get_by_id(id)


def make_public(id: int):

    """
    Make a category public. Must not be public already. Remove all private access.

    :param id:  The ID of the category.
    :return:  The public Category object.
    """

    if not check_if_private(id):
        return BadRequest('Category is already public.')
    update_query('update categories set is_private = 0 where id = ?', (id,))
    insert_query('''delete from private_cat_access where category_id = ?''', (id,))
    return get_by_id(id)


def is_owner(user_id, category_id):

    """
    Check if a user is the owner of a category.

    :param user_id:  The ID of the user.
    :param category_id:  The ID of the category.
    :return:  True if the user is the owner, False otherwise.
    """

    data = read_query('select creator_id from categories where id = ?', (category_id,))
    return user_id == data[0][0]


def check_user_access(user_id, category_id):

    """
    Check if a user has access to a category.
    :param user_id:  The ID of the user.
    :param category_id:  The ID of the category.
    :return:  True if the user has access, False otherwise.
    """

    data = read_query('select access_type from private_cat_access where user_id = ? and category_id = ?',
                      (user_id, category_id))
    return data[0][0] if data else None
