from data.models import ReplyResponse , ReplyText
from data.database import insert_query, read_query
from services.users_service import authenticate_user


def get_reply_by_id(id: int, token) -> ReplyResponse:

    """
    Retrieves a specific reply by ID. Requires user authentication.

    Args:
        id (int): The ID of the reply to retrieve.
        token (str): The JWT token for user authentication.

    Returns:
        ReplyResponse: A `ReplyResponse` object containing the reply details, including user ID, reply date, and reply text.
    """

    user = authenticate_user(token)
    if user:
        data = read_query('''select user_id, reply_date, reply_text from replies where id = ?''', (id,))
        return (ReplyResponse(user_id=user_id,
                    reply_date=reply_date,
                    reply_text=reply_text,)
                for user_id, reply_date, reply_text in data)


def create(reply_text: ReplyText, token):

    """
    Creates a new reply for a specified topic. Requires user authentication.

    Args:
        reply_text (ReplyText): The reply content, including topic ID and text.
        token (str): The JWT token for user authentication.

    Returns:
        Union[ReplyResponse, bool]: The created `ReplyResponse` object if successful, or `False` if authentication fails.
    """

    user = authenticate_user(token)
    if user:
        generated_id = insert_query(
            '''INSERT INTO replies(topic_id, user_id, reply_date, reply_text) VALUES (?, ?, now(), ?)''',
            (reply_text.topic_id, user['user_id'], reply_text.text))
        return get_reply_by_id(generated_id, token)
    
    return False

def reply_exists(reply_id: int) -> bool:

    """
    Checks if a reply exists by its ID.

    Args:
        reply_id (int): The ID of the reply to check.

    Returns:
        bool: `True` if the reply exists, `False` otherwise.
    """

    result = read_query(
        '''SELECT id FROM replies WHERE id = ?''', (reply_id,)
    )

    return bool(result)
