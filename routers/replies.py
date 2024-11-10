from fastapi import APIRouter, Header
from common.responses import BadRequest, Unauthorized, NotFound
from services import replies_service, topics_service, categories_service, users_service
from data.models import ReplyText, Reply
from typing import Annotated

replies_router = APIRouter(prefix="/replies", tags=["Replies"])


@replies_router.post('/')
def create_reply(reply: ReplyText, token: Annotated[str, Header()]):

    """
    Creates a new reply for a specific topic. Validates the topic's existence and reply content.

    Args:
        reply (ReplyText): The reply content, including the associated topic ID and reply text.
        token (Annotated[str, Header()]): The JWT token for authentication.

    Returns:
        Union[Dict[str, Any], BadRequest, NotFound, Unauthorized]: A success message if the reply is created, or an error response if validation fails.
    """
    user = users_service.authenticate_user(token)
    topic = topics_service.get_by_id(reply.topic_id)
    if not topic:
        return NotFound(content="Topic not found.")

    cat_id = topics_service.check_category(reply.topic_id)

    if categories_service.check_if_locked(cat_id):
        return Unauthorized(content="This category is locked.")

    if not users_service.is_admin(user['is_admin']):
        if categories_service.check_if_private(cat_id):
            if categories_service.check_user_access(user['user_id'], cat_id) is None:
                return Unauthorized(content="Category is private.")
            if categories_service.check_user_access(user['user_id'], cat_id) == 0:
                return Unauthorized(content="You have only read access.")



    if topics_service.check_if_locked(reply.topic_id):
        return Unauthorized(content="This topic is locked.")

    if not reply.text.strip():
        return BadRequest(content="Reply text cannot be empty.")

    if len(reply.text) > 200:
        return BadRequest(content="Reply text cannot be more than 200 characters.")


    result = replies_service.create(reply, token)

    return result or Unauthorized

