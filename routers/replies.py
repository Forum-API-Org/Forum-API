from fastapi import APIRouter
from services import replies_service
from data.models import Reply

replies_router = APIRouter(prefix = "replies", tags = ["Replies"])

@replies_router.post('/{topic_id}')
def create_reply(reply: Reply ,topic_id: int):

    #if user validation

    reply.topic_id = topic_id

    return replies_service.create(reply)

