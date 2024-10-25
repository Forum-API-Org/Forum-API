from fastapi import APIRouter, Header
from common.responses import BadRequest, Unauthorized, NotFound
from services import replies_service, topics_service
from data.models import ReplyText, Reply
from typing import Annotated

replies_router = APIRouter(prefix="/replies", tags=["Replies"])


@replies_router.post('/', response_model=Reply)
def create_reply(reply: ReplyText, token: Annotated[str, Header()]):

    #if user

    topic = topics_service.get_by_id(reply.topic_id)
    if not topic:
        return NotFound(content="Topic not found.")

    if not reply.text.strip():
        return BadRequest(content="Reply text cannot be empty.")

    if len(reply.text) > 200:
        return BadRequest(content="Reply text cannot be more than 200 characters.")


    result = replies_service.create(reply, token)

    return result or Unauthorized

