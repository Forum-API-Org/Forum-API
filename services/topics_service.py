from data.database import insert_query, read_query, update_query
from data.models import Category, Topic, Reply
import datetime
from common.responses import BadRequest


def get_topics():
    data = read_query('select * from topics order by id')

    return (Topic(id=id,
                  top_name=top_name,
                  category_id=category_id,
                  user_id=user_id,
                  topic_date=str(topic_date),
                  is_locked=is_locked,
                  best_reply_id=best_reply_id)
            for id, top_name, category_id, user_id, topic_date, is_locked, best_reply_id in data)


def view_replies(id: int):
    data = read_query('select * from replies where topic_id = ?', (id,))

    return next((Reply(id=id,
                       topic_id=topic_id,
                       user_id=user_id,
                       reply_date=str(reply_date),  # date
                       reply_text=reply_text,
                       replies_reply_id=replies_reply_id)
                 for id, topic_id, user_id, reply_date, reply_text, replies_reply_id in data), None)


def get_by_id(id: int):
    data = read_query('select * from topics where id = ?', (id,))

    return next(Topic(id=id,
                      top_name=top_name,
                      category_id=category_id,
                      user_id=user_id,
                      topic_date=str(topic_date),
                      is_locked=is_locked,
                      best_reply_id=best_reply_id)
                for id, top_name, category_id, user_id, topic_date, is_locked, best_reply_id in data)


# def exists(id: int):
#     return any(
#         read_query(
#             'select id, name from categories where id = ?',
#             (id,)))
#

def create(category_id, user_id, top_name):
    generated_id = insert_query(
        'insert into topics(category_id, user_id, top_name, topic_date) values(?,?,?,now())',
        (category_id, user_id, top_name))
    return get_by_id(generated_id)


def check_if_locked(id: int):
    data = read_query('select is_locked from topics where id = ?', (id,))
    return bool(is_locked for _ in data for is_locked in _)


def lock(id: int):
    if check_if_locked(id):
        return BadRequest('Topic is already locked.')
    update_query('update topics set is_locked = 1 where id = ?', (id,))
    return get_by_id(id)


def unlock(id: int):
    if check_if_locked(id):
        return BadRequest('Topic is already unlocked.')
    update_query('update topics set is_locked = 0 where id = ?', (id,))
    return get_by_id(id)


def make_best_reply(topic_id: int, reply_id: int):
    update_query('update topics set best_reply_id = ? where id = ?', (reply_id, topic_id))
    return get_by_id(topic_id)
