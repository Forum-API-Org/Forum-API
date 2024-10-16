from fastapi import APIRouter
from services import votes_service
from data.models import Vote

votes_router = APIRouter(prefix="/votes", tags=["Votes"])

@votes_router.put('/{reply_id}')
def put_vote(vote: Vote):

    return votes_service.vote(vote)
