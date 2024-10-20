from fastapi import APIRouter, Header
from services import votes_service, replies_service
from common.responses import NotFound
from data.models import VoteResult
from typing import Annotated

votes_router = APIRouter(prefix="/votes", tags=["Votes"])

@votes_router.put('/{reply_id}')
def put_vote(reply_id, vote: VoteResult, token: Annotated[str, Header()]):

    if not replies_service.reply_exists(reply_id):
        return NotFound(content="Reply is not found.")

    return votes_service.vote(reply_id, vote, token)
