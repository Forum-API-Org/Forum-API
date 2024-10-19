from fastapi import APIRouter, HTTPException, Header
from data.models import MessageText
from services import messages_service
from typing import Annotated

message_router = APIRouter(prefix="/messages", tags=["Messages"])

@message_router.post('/{sender_id}/{receiver_id}')
def create_message(sender_id, receiver_id, msg: MessageText, token: Annotated[str, Header()]):

    #if user authorization

    if not msg.text.strip():
        raise HTTPException (content="Message text cannot be empty.", status_code=400)
    
    if len(msg.text) > 500:
        raise HTTPException (content="Reply text cannot be more than 500 characters.", status_code=400)

    result = messages_service.create(sender_id, receiver_id, msg, token)

    return {"message": "Message sent successfully.", "content": result}


@message_router.get('/{sender_id}/{receiver_id}')
def view_conversation(sender_id: int, receiver_id: int, token: Annotated[str, Header()]):

    #if user authorization
    result = messages_service.all_messages(sender_id, receiver_id, token)
    
    return {
        "conversation": [r.message_text for r in result],
        "message_count": len(result)
    }

@message_router.get('/{user_id}')
def view_conversations(user_id, token: Annotated[str, Header()]):

    return messages_service.all_conversations(user_id, token)