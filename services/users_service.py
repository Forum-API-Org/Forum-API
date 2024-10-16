from common.responses import BadRequest
from data.models import User, LoginData
from data.database import read_query, update_query, insert_query
import bcrypt
from mariadb import IntegrityError


def get_users():  # Internal to be deleted

    data = read_query('''select * from users''')

    return (User.from_query_result(*row) for row in data)


def create_user(email: str, username: str, password: str, first_name: str, last_name: str ) -> User:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # try:
    generated_id = insert_query(
        '''INSERT INTO users(email, username, user_pass, first_name, last_name) VALUES (?,?,?,?,?);''',
        (email, username, hashed_password, first_name, last_name))

    return User(email = email, username = username, password='', first_name = first_name, last_name = last_name)
    # except IntegrityError:
    #     # mariadb raises this error when a constraint is violated
    #     # in that case we have duplicate usernames
    #     return None

'$2b$12$K21Gv/2MWHvmUuVgXTYArudYiipHD5cM.Ts9fpy07Qr.YxN0eXKtG'