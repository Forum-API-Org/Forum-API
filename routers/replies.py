from fastapi import APIRouter, Header
from fastapi.responses import Response
from services import replies_service
from data.models import ReplyText
from typing import Annotated

replies_router = APIRouter(prefix = "/replies", tags = ["Replies"])


@replies_router.post('/{user_id}/{topic_id}')
def create_reply(user_id: int, topic_id: int, reply_text: ReplyText, token: Annotated[str, Header()]):

    #if user

    if not reply_text.text.strip():
        raise Response(content="Reply text cannot be empty.", status_code=400)
    
    if len(reply_text.text) > 200:
        raise Response(content="Reply text cannot be more than 200 characters.", status_code=400)


    result = replies_service.create(topic_id, user_id, reply_text, token)

    return result

