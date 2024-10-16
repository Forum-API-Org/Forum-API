from data.models import User
from data.database import read_query,update_query, insert_query


def get_users():

    data = read_query('''select * from users''')

    return (User.from_query_result(*row) for row in data)


