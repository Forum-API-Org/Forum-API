from data.models import Message, MessageText, UserResponse
from data.database import insert_query, read_query
from services.users_service import authorise_user


def create(receiver_id, msg: MessageText, token):

    user = authorise_user(token)
    if user:
        
        receiver_exists = read_query('SELECT id FROM users WHERE id = ?', (receiver_id,))
        if not receiver_exists:
            return {"error": "Receiver does not exist"}

        _  = insert_query(
            '''INSERT INTO messages(sender_id, receiver_id, message_date, message_text) VALUES (?, ?, now(), ?)''',
            (user['user_id'], receiver_id, msg.text)
        )

        return msg.text

def all_messages(receiver_id: int, token):

    user = authorise_user(token)
    if user:
        messages = read_query(
            ''' SELECT * 
                FROM messages 
                WHERE (sender_id = ? or sender_id = ?)
                AND (receiver_id = ? or receiver_id = ?)
                ORDER BY message_date ASC''',
            (user['user_id'], receiver_id, user['user_id'], receiver_id)
        )

        data = [Message.from_query_result(*row) for row in messages]

        return data

def all_conversations(token):

    user = authorise_user(token)
    user_id = user['user_id']

    if user:
        conversations = read_query('''
            SELECT DISTINCT u.id, u.email, u.username, u.first_name, u.last_name, u.is_admin
            FROM messages m
            JOIN users u ON (u.id = m.sender_id OR u.id = m.receiver_id)
            WHERE (m.sender_id = ? OR m.receiver_id = ?)
            AND u.id != ?
        ''', 
        (user_id, user_id, user_id))

        а=3

        return [UserResponse.from_query_result(*row) for row in conversations]

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0MiwiaXNfYWRtaW4iOjF9.-zB-FszpE7Wu-qhNpxjHJGimtXlUlHMNpzFa2Jyk1Rc