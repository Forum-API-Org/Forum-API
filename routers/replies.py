from fastapi import APIRouter, Header
from common.responses import BadRequest, Unauthorized
from services import replies_service
from data.models import ReplyText
from typing import Annotated

replies_router = APIRouter(prefix = "/replies", tags = ["Replies"])


@replies_router.post('/{topic_id}')
def create_reply(topic_id: int, reply_text: ReplyText, token: Annotated[str, Header()]):

    #if user

    if not reply_text.text.strip():
        return BadRequest(content="Reply text cannot be empty.")
    
    if len(reply_text.text) > 200:
        return BadRequest(content="Reply text cannot be more than 200 characters.")


    result = replies_service.create(topic_id, reply_text, token)

    return result or Unauthorized

