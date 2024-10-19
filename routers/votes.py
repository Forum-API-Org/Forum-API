from fastapi import APIRouter, Header
from services import votes_service
from data.models import VoteResult
from typing import Annotated

votes_router = APIRouter(prefix="/votes", tags=["Votes"])

@votes_router.put('/{reply_id}/{user_id}')
def put_vote(reply_id, user_id, vote: VoteResult, token: Annotated[str, Header()]):

    return votes_service.vote(reply_id, user_id, vote, token)
