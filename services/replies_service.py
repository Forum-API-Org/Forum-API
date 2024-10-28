from data.models import ReplyResponse , ReplyText
from data.database import insert_query, read_query
from services.users_service import authenticate_user


def get_reply_by_id(id: int, token) -> ReplyResponse:

    user = authenticate_user(token)
    if user:
        data = read_query('''select user_id, reply_date, reply_text from replies where id = ?''', (id,))
        return (ReplyResponse(user_id=user_id,
                    reply_date=reply_date,
                    reply_text=reply_text,)
                for user_id, reply_date, reply_text in data)


def create(reply_text: ReplyText, token):

    user = authenticate_user(token)
    if user:
        generated_id = insert_query(
            '''INSERT INTO replies(topic_id, user_id, reply_date, reply_text) VALUES (?, ?, now(), ?)''',
            (reply_text.topic_id, user['user_id'], reply_text.text))
        return get_reply_by_id(generated_id, token)
    
    return False

def reply_exists(reply_id):

    result = read_query(
        '''SELECT id FROM replies WHERE id = ?''', (reply_id,)
    )

    return result
