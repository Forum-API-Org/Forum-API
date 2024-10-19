from fastapi import APIRouter
from fastapi.responses import Response
from services import replies_service
from data.models import ReplyText

replies_router = APIRouter(prefix = "/replies", tags = ["Replies"])


@replies_router.post('')
def create_reply(topic_id: int, user_id: int, reply_text: ReplyText):

    #if user

    if not reply_text.text.strip():
        raise Response(content="Reply text cannot be empty.", status_code=400)
    
    if len(reply_text.text) > 200:
        raise Response(content="Reply text cannot be more than 200 characters.", status_code=400)


    result = replies_service.create(topic_id, user_id, reply_text)

    return result

