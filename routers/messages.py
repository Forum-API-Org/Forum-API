from fastapi import APIRouter, Header
from data.models import MessageText, Message, UserResponse
from common.responses import BadRequest, NotFound
from services import messages_service, users_service
from typing import Annotated, List

message_router = APIRouter(prefix="/messages/users", tags=["Messages"])

@message_router.post('/')
def create_message(msg: MessageText, token: Annotated[str, Header()]):

    #if user authorization

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



    receiver = users_service.get_user_by_id(receiver_id)
    if not receiver:
        return NotFound(content="Receiver does not exist.")

    conversation = messages_service.all_messages(receiver_id, token)

    if not conversation:
        return NotFound(content="No conversation found")
    
    return conversation
    #return [message.dict(exclude={"id", "receiver_id"}) for message in result]
    # return {
    #     "conversation": [(r.sender_id, r.message_text) for r in result],
    #     "message_count": len(result)
    # }

@message_router.get('/')
def view_conversations(token: Annotated[str, Header()]):

    data = messages_service.all_conversations(token)

    if not data:
        return NotFound(content="No conversations found")

    return data