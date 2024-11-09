from data.models import Message, MessageText, UserResponseChats, MessageOutput
from data.database import insert_query, read_query
from services.users_service import authenticate_user


def create(msg: MessageText, token):

    """
    Creates a new message from the authenticated user to the specified receiver.

    Args:
        msg (MessageText): The message content, including receiver ID and text.
        token (str): The JWT token for user authentication.

    Returns:
        Union[MessageText, dict]: The created message content if successful, or an error dictionary 
                                  if the receiver does not exist.
    """

    user = authenticate_user(token)
    if user:
        
        receiver_exists = read_query('SELECT id FROM users WHERE id = ?', (msg.receiver_id,))
        if not receiver_exists:
            return {"error": "Receiver does not exist"}

        _  = insert_query(
            '''INSERT INTO messages(sender_id, receiver_id, message_date, message_text) VALUES (?, ?, now(), ?)''',
            (user['user_id'], msg.receiver_id, msg.text)
        )

        return msg

def all_messages(receiver_id: int, token) -> list[MessageOutput]:

    """
    Retrieves the conversation between the authenticated user and the specified receiver.

    Args:
        receiver_id (int): The ID of the receiver for the conversation.
        token (str): The JWT token for user authentication.

    Returns:
        list[MessageOutput]: A list of `MessageOutput` objects representing messages exchanged 
                             between the user and the receiver, ordered by message date.
    """

    user = authenticate_user(token)
    if user:
        messages = read_query(
            ''' SELECT sender_id, message_date, message_text 
                FROM messages 
                WHERE (sender_id = ? or sender_id = ?)
                AND (receiver_id = ? or receiver_id = ?)
                ORDER BY message_date ASC''',
            (user['user_id'], receiver_id, user['user_id'], receiver_id)
        )

        data = [MessageOutput.from_query_result(*row) for row in messages]

        return data

def all_conversations(token) -> list[UserResponseChats]:

    """
    Retrieves a list of users with whom the authenticated user has exchanged messages.

    Args:
        token (str): The JWT token for user authentication.

    Returns:
        list[UserResponseChats]: A list of `UserResponseChats` objects representing users involved in 
                                 conversations with the authenticated user.
    """

    user = authenticate_user(token)

    user_id = user['user_id']

    if user:
        conversations = read_query('''
            SELECT DISTINCT u.id, u.username
            FROM messages m
            JOIN users u ON (u.id = m.sender_id OR u.id = m.receiver_id)
            WHERE (m.sender_id = ? OR m.receiver_id = ?)
            AND u.id != ?
        ''', 
        (user_id, user_id, user_id))


        return [UserResponseChats.from_query_result(*row) for row in conversations]

