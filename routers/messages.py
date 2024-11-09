from fastapi import APIRouter, Header
from data.models import MessageText, Message, UserResponse
from common.responses import BadRequest, NotFound
from services import messages_service, users_service
from typing import Annotated, List

message_router = APIRouter(prefix="/messages/users", tags=["Messages"])


@message_router.post('/')
def create_message(msg: MessageText, token: Annotated[str, Header()]):

    """
    Sends a new message to a specified receiver. Validates the receiver's existence and message content.

    Args:
        msg (MessageText): The message content, including the receiver ID and text.
        token (Annotated[str, Header()]): The JWT token for authentication.

    Returns:
        Union[Dict[str, Any], BadRequest, NotFound]: A success message if the message is sent, or an error response if validation fails.
    """

    receiver = users_service.get_user_by_id(msg.receiver_id)
    if not receiver:
        return NotFound(content="Receiver does not exist.")

    if not msg.text.strip():
        return BadRequest(content="Message text cannot be empty.")

    if len(msg.text) > 500:
        return BadRequest(content="Reply text cannot be more than 500 characters.")

    message = messages_service.create(msg, token)

    return message

    # return {"message": "Message sent successfully.", "content": result}


@message_router.get('/{receiver_id}')
def view_conversation(receiver_id: int, token: Annotated[str, Header()]):

    """
    Retrieves the conversation history between the authenticated user and a specific receiver.

    Args:
        receiver_id (int): The ID of the receiver to view the conversation with.
        token (Annotated[str, Header()]): The JWT token for authentication.

    Returns:
        Union[List[Dict[str, Any]], NotFound]: A list of messages if the conversation exists, or an error response if no conversation is found.
    """

    receiver = users_service.get_user_by_id(receiver_id)
    if not receiver:
        return NotFound(content="Receiver does not exist.")

    conversation = messages_service.all_messages(receiver_id, token)

    if not conversation:
        return NotFound(content="No conversation found")

    return conversation
    # return [message.dict(exclude={"id", "receiver_id"}) for message in result]
    # return {
    #     "conversation": [(r.sender_id, r.message_text) for r in result],
    #     "message_count": len(result)
    # }


@message_router.get('/')
def view_conversations(token: Annotated[str, Header()]):

    """
    Retrieves a list of all conversations for the authenticated user.

    Args:
        token (Annotated[str, Header()]): The JWT token for authentication.

    Returns:
        Union[List[Dict[str, Any]], NotFound]: A list of conversation overviews if any exist, or an error response if no conversations are found.
    """

    data = messages_service.all_conversations(token)

    if not data:
        return NotFound(content="No conversations found")

    return data