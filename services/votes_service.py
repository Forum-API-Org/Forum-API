from data.models import Vote
from data.database import  update_query, read_query, insert_query


def vote(vote: Vote):

    check = read_query(
        '''SELECT * FROM votes WHERE user_id = ? AND reply_id = ?''',
        (vote.user_id, vote.reply_id)
    )
    if check[0][2] == vote.vote:
        return f"The Vote is already {vote.vote}"
    
    if check:
        result = update_query(
            '''UPDATE votes SET vote = ? WHERE user_id = ? AND reply_id = ? ''',
            (vote.vote, vote.user_id, vote.reply_id )
        )
    else:
        result = insert_query(
            '''INSERT INTO votes(user_id, reply_id, vote) VALUES (?, ?, ?) ''',
            (vote.user_id, vote.reply_id, vote.vote)
        )

    return result
