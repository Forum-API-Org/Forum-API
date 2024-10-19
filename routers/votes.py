from fastapi import APIRouter
from services import votes_service
from data.models import VoteResult

votes_router = APIRouter(prefix="/votes", tags=["Votes"])

@votes_router.put('/{reply_id}/{user_id}')
def put_vote(reply_id, user_id, vote: VoteResult):

    return votes_service.vote(reply_id, user_id, vote)
