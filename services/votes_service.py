from data.models import VoteResult
from data.database import  update_query, read_query, insert_query


def vote(reply_id, user_id, vote: VoteResult):
    check = read_query(
        '''SELECT * FROM votes WHERE user_id = ? AND reply_id = ?''',
        (user_id, reply_id)
    )
    
    if check:
        existing_vote_value = check[0][2]
        
        if existing_vote_value == vote.vote_value:
            return f"The vote is already {vote.vote}"
        
        result = update_query(
            '''UPDATE votes SET vote = ? WHERE user_id = ? AND reply_id = ?''',
            (vote.vote_value, user_id, reply_id)
        )

        return f'Vote changed to {vote.vote}'

    else:
        result = insert_query(
            '''INSERT INTO votes(user_id, reply_id, vote) VALUES (?, ?, ?)''',
            (user_id, reply_id, vote.vote_value)
        )
    
        return f'You voted with {vote.vote}'