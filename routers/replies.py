from fastapi import APIRouter
from services import replies_service
from data.models import Reply

replies_router = APIRouter(prefix = "/replies", tags = ["Replies"])


@replies_router.post('')
def create_reply(topic_id: int, user_id: int, reply_text: str):
    result = replies_service.create(topic_id, user_id, reply_text)

    return result

