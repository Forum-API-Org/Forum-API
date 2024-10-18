from fastapi import APIRouter
from data.models import Message
from services import messages_service

message_router = APIRouter(prefix="/messages", tags=["Messages"])

@message_router.post('/{sender_id}/{receiver_id}')
def create_message(msg: Message):

    #if user authorization

    result = messages_service.create(msg)

    return {"message": "Message sent successfully.", "content": result}


@message_router.get('/{sender_id}/{receiver_id}')
def view_conversation(sender_id: int, receiver_id: int):

    #if user authorization
    result = messages_service.all_messages(sender_id, receiver_id)
    
    return {
        "conversation": [r.message_text for r in result],
        "message_count": len(result)
    }