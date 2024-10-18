from fastapi import APIRouter
from services import topics_service
from common.responses import NotFound
topics_router = APIRouter(prefix="/topics", tags=["Topics"])


@topics_router.get('')
def get_all_topics():

    data = topics_service.get_topics()

    return data


@topics_router.get('/{id}')
def get_topic_by_id(id: int):
    topic = topics_service.get_by_id(id)
    replies = topics_service.view_replies(id)

    if topic is None:
        return NotFound()
    else:
        return {
            "topic": topic,
            "replies": replies
        }


@topics_router.post('')
def create_topic(category_id: int, user_id: int, topic_name: str):
    topic = topics_service.create(category_id, user_id, topic_name)

    return topic


@topics_router.put('/lock/{id}')
def lock_topic(id: int):
    result = topics_service.lock(id)
    return result


@topics_router.put('/unlock/{id}')
def unlock_topic(id: int):
    result = topics_service.unlock(id)
    return result


@topics_router.put('/{topic_id}/best_reply/{reply_id}')
def choose_best_reply(topic_id: int, reply_id: int):

    result = topics_service.make_best_reply(topic_id, reply_id)
    return result
