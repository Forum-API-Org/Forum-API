from data.models import Message, MessageText, UserResponse
from data.database import insert_query, read_query
from services.users_service import authorise_user


def create(sender_id, receiver_id, msg: MessageText, token):

    user = authorise_user(token)
    if user:
        sender_exists = read_query('SELECT id FROM users WHERE id = ?', (sender_id,))
        if not sender_exists:
            return {"error": "Sender does not exist"}

        receiver_exists = read_query('SELECT id FROM users WHERE id = ?', (receiver_id,))
        if not receiver_exists:
            return {"error": "Receiver does not exist"}

        _  = insert_query(
            '''INSERT INTO messages(sender_id, receiver_id, message_date, message_text) VALUES (?, ?, now(), ?)''',
            (sender_id, receiver_id, msg.text)
        )

        return msg.text

def all_messages(sender_id: int, receiver_id: int, token):

    user = authorise_user(token)
    if user:
        messages = read_query(
            ''' SELECT * 
                FROM messages 
                WHERE (sender_id = ? or sender_id = ?)
                AND (receiver_id = ? or receiver_id = ?);
                ORDER BY message_date ASC''',
            (sender_id, receiver_id, sender_id, receiver_id)
        )
        return [Message.from_query_result(*row) for row in messages]

def all_conversations(user_id: int, token):

    user = authorise_user(token)


    if user:
        conversations = read_query('''
            SELECT DISTINCT u.id, u.email, u.username, u.first_name, u.last_name
            FROM messages m
            JOIN users u ON (u.id = m.sender_id OR u.id = m.receiver_id)
            WHERE (m.sender_id = ? OR m.receiver_id = ?)
            AND u.id != ?
        ''', 
        (user_id, user_id, user_id))

        return [UserResponse.from_query_result(*row) for row in conversations]

