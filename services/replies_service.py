from data.models import Reply
from data.database import insert_query, read_query
from data.models import Reply
from services.users_service import authorise_user


def get_reply_by_id(id: int, token):

    user = authorise_user(token)
    if user:
        data = read_query('''select * from replies where id = ?''', (id,))
        return (Reply(id=id,
                    topic_id=topic_id,
                    user_id=user_id,
                    reply_date=str(reply_date),
                    reply_text=reply_text,
                    replies_reply_id=replies_reply_id)
                for id, topic_id, user_id, reply_date, reply_text, replies_reply_id in data)


def create(topic_id, user_id, reply_text, token):

    user = authorise_user(token)
    if user:
        generated_id = insert_query(
            '''INSERT INTO replies(topic_id, user_id, reply_date, reply_text) VALUES (?, ?, now(), ?)''',
            (topic_id, user_id, reply_text))
        return get_reply_by_id(generated_id, token)


