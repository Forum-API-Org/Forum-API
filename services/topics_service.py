from data.database import insert_query, read_query, update_query
from data.models import Category, Topic, Reply, ReplyResponse, TopicResponse
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
    data = read_query('''select user_id, reply_date, reply_text
                         from replies
                         where topic_id = ?''', (id,))

    if not data:
        return []

    return [ReplyResponse.from_query_result(user_id=user_id,
                                            reply_date=reply_date,
                                            reply_text=reply_text)
            for user_id, reply_date, reply_text in data]


def get_by_id(id: int):
    data = read_query('''select 
                           category_id,
                           top_name,
                           user_id,
                           topic_date,
                           is_locked,
                           best_reply_id 
                         from topics where id = ?''', (id,))

    if not data:
        return None

    category_id, top_name, user_id, topic_date, is_locked, best_reply_id = data[0]

    replies = view_replies(id)

    return TopicResponse(
        top_name=top_name,
        user_id=user_id,
        topic_date=str(topic_date),
        is_locked=is_locked,
        best_reply_id=best_reply_id,
        replies=replies
    )


def exists(id: int):
    return any(
        read_query(
            'select id, top_name from topics where id = ?',
            (id,)))


def create(category_id, user_id, top_name):
    generated_id = insert_query(
        'insert into topics(category_id, user_id, top_name, topic_date) values(?,?,?,now())',
        (category_id, user_id, top_name))
    return get_by_id(generated_id)


def check_category(id: int):

    result = read_query(
            'select category_id from topics where id = ?',
            (id,))

    return result[0][0]


def top_name_exists(top_name: str):
    return any(
        read_query(
            'select id, top_name from topics where top_name = ?',
            (top_name,)))


def check_if_locked(id: int):
    data = read_query('select is_locked from topics where id = ?', (id,))
    return bool(data[0][0])


def lock(id: int):
    if check_if_locked(id):
        return BadRequest('Topic is already locked.')
    update_query('update topics set is_locked = 1 where id = ?', (id,))
    return get_by_id(id)


def unlock(id: int):
    if not check_if_locked(id):
        return BadRequest('Topic is already unlocked.')
    update_query('update topics set is_locked = 0 where id = ?', (id,))
    return get_by_id(id)


def reply_belongs_to_topic(reply_id: int, topic_id: int):
    data = read_query('select topic_id from replies where id = ?', (reply_id,))
    return topic_id == data[0][0]


def make_best_reply(topic_id: int, reply_id: int):
    update_query('update topics set best_reply_id = ? where id = ?', (reply_id, topic_id))
    return get_by_id(topic_id)


def is_owner(user_id, topic_id):
    data = read_query('select user_id from topics where id = ?', (topic_id,))
    return user_id == data[0][0]
