from fastapi import APIRouter, Header
from data.models import MessageText
from common.responses import BadRequest, NotFound
from services import messages_service, users_service
from typing import Annotated

message_router = APIRouter(prefix="/messages", tags=["Messages"])

@message_router.post('/{receiver_id}')
def create_message(receiver_id, msg: MessageText, token: Annotated[str, Header()]):

    #if user authorization

    receiver = users_service.get_user_by_id(receiver_id)
    if not receiver:
        return NotFound(content="Receiver does not exist.")


    if not msg.text.strip():
        return BadRequest(content="Message text cannot be empty.")

    if len(msg.text) > 500:
        return BadRequest(content="Reply text cannot be more than 500 characters.")

    result = messages_service.create(receiver_id, msg, token)

    return {"message": "Message sent successfully.", "content": result}


@message_router.get('/{receiver_id}')
def view_conversation(receiver_id: int, token: Annotated[str, Header()]):



    receiver = users_service.get_user_by_id(receiver_id)
    if not receiver:
        return NotFound(content="Receiver does not exist.")

    result = messages_service.all_messages(receiver_id, token)

    if not result:
        return NotFound(content="No conversation found")

    return {
        "conversation": [(r.sender_id, r.message_text) for r in result],
        "message_count": len(result)
    }

@message_router.get('/')
def view_conversations(token: Annotated[str, Header()]):

    data = messages_service.all_conversations(token)

    if not data:
        return NotFound(content="No conversations found")

    return data