from data.models import VoteResult
from data.database import  update_query, read_query, insert_query
from services.users_service import authenticate_user


def vote(reply_id, vote: VoteResult, token):

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