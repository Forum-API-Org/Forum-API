from fastapi import APIRouter, Header
from services import votes_service, replies_service
from common.responses import NotFound
from data.models import VoteResult
from typing import Annotated

votes_router = APIRouter(prefix="/votes", tags=["Votes"])

@votes_router.put('/{reply_id}')
def put_vote(reply_id: int, vote: VoteResult, token: Annotated[str, Header()]):
    
    """
    Casts a vote on a specific reply. Verifies the existence of the reply before voting.

    Args:
        reply_id (int): The ID of the reply to vote on.
        vote (VoteResult): The vote data, containing details about the vote.
        token (Annotated[str, Header()]): The JWT token for authentication.

    Returns:
        Union[Dict[str, Any], NotFound]: A success message if the vote is cast successfully, or an error message if the reply is not found.
    """
    if not replies_service.reply_exists(reply_id):
        return NotFound(content="Reply is not found.")

    return votes_service.vote(reply_id, vote, token)
