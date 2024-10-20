from fastapi import APIRouter, Header
from data.models import MessageText
from common.responses import BadRequest
from services import messages_service
from typing import Annotated

message_router = APIRouter(prefix="/messages", tags=["Messages"])

@message_router.post('/{receiver_id}')
def create_message(receiver_id, msg: MessageText, token: Annotated[str, Header()]):

    #if user authorization

    if not msg.text.strip():
        return BadRequest (content="Message text cannot be empty.")
    
    if len(msg.text) > 500:
        return BadRequest (content="Reply text cannot be more than 500 characters.")

    result = messages_service.create(receiver_id, msg, token)

    return {"message": "Message sent successfully.", "content": result}


@message_router.get('/{receiver_id}')
def view_conversation(receiver_id: int, token: Annotated[str, Header()]):

    #if user authorization
    result = messages_service.all_messages(receiver_id, token)
    
    return {
        "conversation": [r.message_text for r in result],
        "message_count": len(result)
    }

@message_router.get('/{user_id}')
def view_conversations(token: Annotated[str, Header()]):

    return messages_service.all_conversations(token)