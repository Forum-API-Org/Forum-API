from data.models import VoteResult
from data.database import  update_query, read_query, insert_query
from services.users_service import authenticate_user


def vote(reply_id, vote: VoteResult, token):

    """
    Casts or updates a vote for a specific reply. Checks if the user has already voted and updates or inserts the vote accordingly.

    Args:
        reply_id (int): The ID of the reply to vote on.
        vote (VoteResult): The vote data, containing the vote value.
        token (str): The JWT token for user authentication.

    Returns:
        str: A message indicating the result of the voting action, such as confirmation of the new vote, or information that the vote has been updated.
    """

    user = authenticate_user(token)
    if user:
        check = read_query(
            '''SELECT * FROM votes WHERE user_id = ? AND reply_id = ?''',
            (user['user_id'], reply_id)
        )
        
        if check:
            existing_vote_value = check[0][2]
            
            if existing_vote_value == vote.vote_value:
                return f"The vote is already {vote.vote}"
            
            _ = update_query(
                '''UPDATE votes SET vote = ? WHERE user_id = ? AND reply_id = ?''',
                (vote.vote_value, user['user_id'], reply_id)
            )

            return f'Vote changed to {vote.vote}'

        else:
            _ = insert_query(
                '''INSERT INTO votes(user_id, reply_id, vote) VALUES (?, ?, ?)''',
                (user['user_id'], reply_id, vote.vote_value)
            )
        
            return f'You voted with {vote.vote}'