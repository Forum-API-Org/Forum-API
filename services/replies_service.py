from data.models import Reply
from data.database import insert_query
from datetime import datetime


def create(reply: Reply):
    generated_id = insert_query(
        'INSERT INTO replies(topic_id, user_id, reply_date, reply_text) VALUES (?, ?, ?, ?)',
        (reply.topic_id, reply.user_id, datetime.now(), reply.reply_text)
    )
    reply.id = generated_id

    return reply


