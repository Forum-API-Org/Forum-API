from fastapi import APIRouter, Header
from services import topics_service
from common.responses import NotFound, BadRequest
from typing import Annotated
from services.users_service import authenticate_user, is_admin
topics_router = APIRouter(prefix="/topics", tags=["Topics"])


@topics_router.get('')
def get_all_topics(token: Annotated[str, Header()]):
    authenticate_user(token)
    data = topics_service.get_topics()

    return data


@topics_router.get('/{id}')
def get_topic_by_id(id: int, token: Annotated[str, Header()]):
    authenticate_user(token)
    topic = topics_service.get_by_id(id)
    replies = topics_service.view_replies(id)

    if topic is None:
        return NotFound()
    else:
        return {
            "topic": topic,
            "replies": replies
        }


@topics_router.post('/')
def create_topic(category_id: int, topic_name: str, token: Annotated[str, Header()]):
    user = authenticate_user(token)
    topic = topics_service.create(category_id, user['user_id'], topic_name)

    return topic


@topics_router.put('/lock/{id}')
def lock_topic(id: int, token: Annotated[str, Header()]):
    user = authenticate_user(token)
    if not is_admin(user['is_admin']):
        return BadRequest('Only admins can lock topics')
    result = topics_service.lock(id)
    return result


@topics_router.put('/unlock/{id}')
def unlock_topic(id: int, token: Annotated[str, Header()]):
    user = authenticate_user(token)
    if not is_admin(user['is_admin']):
        return BadRequest('Only admins can unlock topics')
    result = topics_service.unlock(id)
    return result


@topics_router.put('/{topic_id}/best_reply/{reply_id}')
def choose_best_reply(topic_id: int, reply_id: int, token: Annotated[str, Header()]):
    user = authenticate_user(token)
    if not topics_service.is_owner(user['user_id'], topic_id) or not is_admin(user['is_admin']):
        return BadRequest('Only admins and topic owners can choose best replies')

    result = topics_service.make_best_reply(topic_id, reply_id)
    return result
