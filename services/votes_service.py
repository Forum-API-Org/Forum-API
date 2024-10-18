from data.models import Vote
from data.database import  update_query, read_query, insert_query


def vote(vote: Vote):
    check = read_query(
        '''SELECT * FROM votes WHERE user_id = ? AND reply_id = ?''',
        (vote.user_id, vote.reply_id)
    )
    
    if check:
        existing_vote_value = check[0][2]
        
        if existing_vote_value == vote.vote_value:
            return f"The vote is already {vote.vote}"
        
        result = update_query(
            '''UPDATE votes SET vote = ? WHERE user_id = ? AND reply_id = ?''',
            (vote.vote_value, vote.user_id, vote.reply_id)
        )
    else:
        result = insert_query(
            '''INSERT INTO votes(user_id, reply_id, vote) VALUES (?, ?, ?)''',
            (vote.user_id, vote.reply_id, vote.vote_value)
        )
    
    return result