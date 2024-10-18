from data.models import Message
from data.database import insert_query, read_query
from datetime import datetime


def create(msg: Message):

    generated_id = insert_query(
        '''INSERT INTO messages(sender_id, receiver_id, message_date, message_text) VALUES (?, ?, ?, ?)''',
        (msg.sender_id, msg.receiver_id, datetime.now(), msg.message_text)
    )

    msg.id = generated_id

    return msg.message_text

def all_messages(sender_id: int, receiver_id: int):
    messages = read_query(
        ''' SELECT * 
            FROM messages 
            WHERE (sender_id = ? or sender_id = ?)
            AND (receiver_id = ? or receiver_id = ?);
            ORDER BY message_date ASC''',
        (sender_id, receiver_id, sender_id, receiver_id)
    )
    return [Message.from_query_result(*row) for row in messages]

