from fastapi import APIRouter, Header, Query, HTTPException
from typing import Optional, List
from data.database import read_query
from data.models import Topic, TopicCreation, TopicResponse
from services import topics_service, categories_service, replies_service
from common.responses import NotFound, BadRequest, Forbidden, Unauthorized
from typing import Annotated
from services.users_service import authenticate_user, is_admin
topics_router = APIRouter(prefix="/topics", tags=["Topics"])


@topics_router.get("/", response_model=List[TopicResponse])
def get_topics(
    token: Annotated[str, Header()],
    search: Optional[str] = Query(None, description="Search by topic name"),
    sort_by: Optional[str] = Query("topic_date", description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order: 'asc' or 'desc'"),
    limit: int = Query(10, description="Number of topics to return"),
    offset: int = Query(0, description="Number of topics to skip")
):

    """
    Get all topics from the database. Only accessible by users with access to the category. Admins can access all topics.

    :param token:  JWT token for authentication.
    :param search:  Search by topic name. Default is None.
    :param sort_by:  Field to sort by. Default is 'topic_date'. Possible values: 'topic_date', 'top_name', 'category_id', 'user_id', 'is_locked'.
    :param sort_order:  Sort order: 'asc' or 'desc'. Default is 'asc'.
    :param limit:  Number of topics to return. Default is 10.
    :param offset:  Number of topics to skip. Default is 0.
    :return:  List of TopicResponse objects.
    """
    user = authenticate_user(token)
    query = "SELECT id, top_name, user_id, topic_date, is_locked, best_reply_id, category_id FROM topics"
    params = []

    if search:
        query += " WHERE top_name LIKE ?"
        params.append(f"%{search}%")

    if sort_by not in ["topic_date", "top_name", "category_id", "user_id", "is_locked"]:
        raise HTTPException(status_code=400, detail="Invalid sort field.")
    query += f" ORDER BY {sort_by} {sort_order.upper()}"

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    data = read_query(query, params)

    topics = [
        TopicResponse(
            top_name=row[1],
            user_id=row[2],
            topic_date=str(row[3]),
            is_locked=row[4],
            best_reply_id=row[5],
            replies=topics_service.view_replies(row[0])
        )
        for row in data
        if is_admin(user['is_admin']) or
        (categories_service.check_if_private(row[6]) is False) or
        (categories_service.check_user_access(user['user_id'], row[6]) is not None)
    ]
    return topics


@topics_router.get('/{id}')
def get_topic_by_id(id: int, token: Annotated[str, Header()]):

    """
    Get a topic by its ID. Only accessible by users with access to the category. Admins can access all topics.

    :param id:  The ID of the topic. Must exist in the database.
    :param token:  JWT token for authentication.
    :return:  TopicResponse object.
    """

    user = authenticate_user(token)

    if not topics_service.exists(id):
        return NotFound('Topic not found')

    topic = topics_service.get_by_id(id)

    if categories_service.check_if_private(topics_service.check_category(id)):

        access = categories_service.check_user_access(user['user_id'], topics_service.check_category(id))

        if access is None and not is_admin(user['is_admin']):
            return Unauthorized('Category is private')

    if topic is None:
        return NotFound('Topic not found')

    return topic


@topics_router.post('/', response_model=TopicResponse, response_model_exclude={"replies", "user_id"})
def create_topic(topic: TopicCreation, token: Annotated[str, Header()], ):

    """
    Create a new topic. Only accessible by users with write access to the category. Admins can create topics in any category.

    :param topic:  The topic details.
    :param token:  JWT token for authentication.
    :return:  TopicResponse object.
    """

    user = authenticate_user(token)

    if not categories_service.exists(topic.category_id):
        return NotFound('Category not found')

    if categories_service.check_if_private(topic.category_id):

        access = categories_service.check_user_access(user['user_id'], topic.category_id)

        if access is None and not is_admin(user['is_admin']):
            return Unauthorized('Category is private')

        if access == 0 and not is_admin(user['is_admin']):
            return Unauthorized('You have only read access to this category')

    if categories_service.check_if_locked(topic.category_id):
        return Forbidden('Category is locked')

    if topics_service.top_name_exists(topic.top_name):
        return BadRequest('Topic name already exists')

    topic = topics_service.create(topic.category_id, user['user_id'], topic.top_name)

    return topic


@topics_router.put('/lock/{id}')
def lock_topic(id: int, token: Annotated[str, Header()]):

    """
    Lock a topic. Only admins can lock topics.

    :param id:  The ID of the topic.
    :param token:  JWT token for authentication.
    :return:  TopicResponse object.
    """

    user = authenticate_user(token)
    if not topics_service.exists(id):
        return NotFound('Topic not found')

    if not is_admin(user['is_admin']):
        return Forbidden('Only admins can lock topics')

    result = topics_service.lock(id)

    return result


@topics_router.put('/unlock/{id}')
def unlock_topic(id: int, token: Annotated[str, Header()]):

    """
    Unlock a topic. Only admins can unlock topics.

    :param id:  The ID of the topic.
    :param token:  JWT token for authentication.
    :return:   TopicResponse object.
    """

    user = authenticate_user(token)

    if not topics_service.exists(id):
        return NotFound('Topic not found')

    if not is_admin(user['is_admin']):
        return Forbidden('Only admins can unlock topics')

    result = topics_service.unlock(id)

    return result


@topics_router.put('/{topic_id}/best_reply/{reply_id}')
def choose_best_reply(topic_id: int, reply_id: int, token: Annotated[str, Header()]):

    """
    Choose the best reply for a topic. Only the topic owner can choose the best reply.

    :param topic_id:  The ID of the topic.
    :param reply_id:  The ID of the reply.
    :param token:  JWT token for authentication.
    :return:  TopicResponse object.
    """

    user = authenticate_user(token)

    if not topics_service.exists(topic_id):
        return NotFound('Topic not found')

    if not replies_service.reply_exists(reply_id):
        return NotFound('Reply not found')

    if not topics_service.is_owner(user['user_id'], topic_id):
        return Forbidden('Only topic owners can choose best replies')

    if not topics_service.reply_belongs_to_topic(reply_id, topic_id):
        return BadRequest('Reply does not belong to topic')

    result = topics_service.make_best_reply(topic_id, reply_id)
    return result
