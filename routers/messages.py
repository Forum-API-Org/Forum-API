from fastapi import APIRouter, HTTPException 
from data.models import MessageText
from services import messages_service

message_router = APIRouter(prefix="/messages", tags=["Messages"])

@message_router.post('/{sender_id}/{receiver_id}')
def create_message(sender_id, receiver_id, msg: MessageText):

    #if user authorization

    if not msg.text.strip():
        raise HTTPException (content="Message text cannot be empty.", status_code=400)
    
    if len(msg.text) > 500:
        raise HTTPException (content="Reply text cannot be more than 500 characters.", status_code=400)

    result = messages_service.create(sender_id, receiver_id, msg)

    return {"message": "Message sent successfully.", "content": result}


@message_router.get('/{sender_id}/{receiver_id}')
def view_conversation(sender_id: int, receiver_id: int):

    #if user authorization
    result = messages_service.all_messages(sender_id, receiver_id)
    
    return {
        "conversation": [r.message_text for r in result],
        "message_count": len(result)
    }