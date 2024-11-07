import math
import unittest
from unittest.mock import patch, Mock

from common.responses import Unauthorized, NoContent
from data.models import User
from services import users_service
from services.users_service import check_if_username_exists
from fastapi.exceptions import HTTPException
from datetime import timezone, timedelta, datetime
import os
import jwt


def fake_user():
    admin = Mock(spec=User)
    admin.is_admin = True
    return admin


def fake_admin():
    admin = Mock(spec=User)
    admin.is_admin = True
    return admin

@patch('services.users_service.read_query')
class UserServiceShould(unittest.TestCase):


    def test_checkIfUserExists_when_usernameExists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = True
                # Act
        with self.assertRaises(HTTPException) as context:
            check_if_username_exists('mock_username', 'Username already exists')
        #Assert
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'Username already exists')
        self.assertEqual(mock_read_query.call_count, 1)

    def test_checkIfUserExists_when_usernameDoesNotExists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = False
        # Act
        try:
            result = check_if_username_exists('nonexistent_username', 'Username does not exist')
        except HTTPException:
            self.fail("HTTPException was raised when it shouldn't have been.")
        #Assert
        self.assertIsNone(result)
        self.assertEqual(mock_read_query.call_count, 1)

    def test_checkIfUserExists_when_emailExists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = True
                # Act
        with self.assertRaises(HTTPException) as context:
            check_if_username_exists('mock_username', 'Email already taken.')
        #Assert
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, 'Email already taken.')
        self.assertEqual(mock_read_query.call_count, 1)

    def test_checkIfUserExists_when_emailDoesNotExists(self, mock_read_query):
        # Arrange
        mock_read_query.return_value = False
        # Act
        try:
            result = check_if_username_exists('nonexistent_username', 'Username does not exist')
        except HTTPException:
            self.fail("HTTPException was raised when it shouldn't have been.")
        #Assert
        self.assertIsNone(result)
        self.assertEqual(mock_read_query.call_count, 1)

    @patch('services.users_service.insert_query')
    @patch('bcrypt.hashpw')
    def test_createUser_returnsUser(self, mock_hashpw, mock_insert_query, mock_read_query):
        # Arrange
        mock_read_query.side_effect = [False, False]
        mock_hashpw.return_value = b'hashed_password'
        mock_insert_query.return_value = 1
        # Act
        result = users_service.create_user('test@email.com',
                                           'test',
                                           'password123.',
                                           'first-name',
                                           'last-name')

        self.assertEqual(mock_read_query.call_count, 2)
        mock_hashpw.assert_called_once()
        self.assertEqual(result.id, 1)
        self.assertEqual(result.username, 'test')
        self.assertEqual(result.email, 'test@email.com')
        self.assertEqual(result.password, 'password123.')
        self.assertEqual(result.first_name, 'first-name')
        self.assertEqual(result.last_name, 'last-name')


    @patch('bcrypt.checkpw')
    def test_loginUser_whenCredentialsValid(self, mock_checkpw, mock_read_query):
        # Arrange
        mock_user_data = [(1, 'test_user', 'hashed_pass', 0)]
        mock_read_query.return_value = mock_user_data
        mock_checkpw.return_value = True
        login_data = Mock()
        login_data.username = 'test_user'
        login_data.password = 'password123'

        # Act
        result = users_service.login_user(login_data)

        # Assert
        self.assertEqual(result, mock_user_data)
        mock_read_query.assert_called_once()
        mock_checkpw.assert_called_once()

    @patch('bcrypt.checkpw')
    def test_loginUser_whenUserDoesNotExist(self, mock_checkpw, mock_read_query):
        # Arrange
        mock_read_query.return_value = None
        login_data = Mock()
        login_data.username = 'nonexistent_user'
        login_data.password = 'password123'

        # Act
        result = users_service.login_user(login_data)

        # Assert
        self.assertIsNone(result)
        mock_read_query.assert_called_once()
        mock_checkpw.assert_not_called()

    
    @patch('bcrypt.checkpw')
    def test_loginUser_whenPasswordIncorrect(self, mock_checkpw, mock_read_query):
        # Arrange
        mock_user_data = [(1, 'test_user', 'hashed_pass', False)]
        mock_read_query.return_value = mock_user_data
        mock_checkpw.return_value = False
        login_data = Mock()
        login_data.username = 'test_user'
        login_data.password = 'wrong_password'

        # Act
        result = users_service.login_user(login_data)

        # Assert
        self.assertIsNone(result)
        mock_read_query.assert_called_once()
        mock_checkpw.assert_called_once()

   
    @patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret'}) # Temporary change my secret key for the test
    @patch('services.users_service.datetime')
    def test_createToken_returns_validToken(self, mock_datetime, mock_read_query):
        # Arrange
        today = datetime.now(timezone.utc)
        mock_datetime.now.return_value = today
        
        user_data = [(1, 'testuser', 'password', True)]  # Mock user data tuple
        expected_payload = {
            'user_id': 1,
            'username': 'testuser',
            'is_admin': True,
            'exp': today + timedelta(minutes=9000)
        }

        # Act
        token = users_service.create_token(user_data)
        
        # Assert
        decoded_token = jwt.decode(token, 'test_secret', algorithms=['HS256'])
        self.assertEqual(decoded_token['user_id'], expected_payload['user_id'])
        self.assertEqual(decoded_token['username'], expected_payload['username'])
        self.assertEqual(decoded_token['is_admin'], expected_payload['is_admin'])
        self.assertEqual(decoded_token['exp'], math.floor(expected_payload['exp'].timestamp()))

    @patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret'})  # Temporary change my secret key for the test
    def test_decodeToken_when_validToken(self, mock_ready_query):
        # Arrange
        payload = {'user_id': 1, 'username': 'testuser', 'is_admin': True}
        token = jwt.encode(payload, 'test_secret', algorithm='HS256')

        # Act
        decoded_payload = users_service.decode_token(token)

        # Assert
        self.assertEqual(decoded_payload['user_id'], payload['user_id'])
        self.assertEqual(decoded_payload['username'], payload['username'])
        self.assertEqual(decoded_payload['is_admin'], payload['is_admin'])

    @patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret'})  # Temporary change my secret key for the test
    def test_decodeToken_when_invalidToken(self, mock_read_query):
        # Arrange
        invalid_token = "invalid.token.here"

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            users_service.decode_token(invalid_token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, 'Invalid token')

        
    def test_isAdmin_when_Admin(self, mock_read_query):
        # Arrange
        admin_value = 1

        # Act
        result = users_service.is_admin(admin_value)

        # Assert
        self.assertTrue(result)

    def test_isAdmin_when_nonAdmin(self, mock_read_query):
        # Arrange
        non_admin_value = 0

        # Act
        result = users_service.is_admin(non_admin_value)

        # Assert
        self.assertFalse(result)
        
    @patch('services.users_service.decode_token')
    @patch('services.users_service.user_exists')
    @patch.dict(os.environ, {'JWT_SECRET_KEY': 'test_secret'})  # Temporary change my secret key for the test
    def test_authenticateUser_when_validToken(self, mock_user_exists, mock_decode_token, mock_read_query):
        # Arrange
        token = jwt.encode({'user_id': 1, 'username': 'testuser', 'is_admin': True}, 'test_secret', algorithm='HS256')
        mock_read_query.return_value = []
        mock_decode_token.return_value = {'user_id': 1, 'username': 'testuser', 'is_admin': True}
        mock_user_exists.return_value = True

        # Act
        user_data = users_service.authenticate_user(token)

        # Assert
        self.assertEqual(user_data['user_id'], 1)
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['is_admin'], True)
        mock_read_query.assert_called_once_with('''select * from tokens_blacklist where token = ?;''', (token,))
        mock_decode_token.assert_called_once_with(token)
        mock_user_exists.assert_called_once_with({'user_id': 1, 'username': 'testuser', 'is_admin': True})

    def test_authenticateUser_when_tokenInBlacklist(self, mock_read_query):
        # Arrange
        token = "some.token.here"
        mock_read_query.return_value = [token]

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            users_service.authenticate_user(token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, 'Invalid token')
        mock_read_query.assert_called_once_with('''select * from tokens_blacklist where token = ?;''', (token,))

    @patch('services.users_service.decode_token')
    def test_authenticateUser_when_invalidToken(self, mock_decode_token, mock_read_query):
        # Arrange
        token = "invalid.token.here"
        mock_read_query.return_value = []
        mock_decode_token.side_effect = HTTPException(status_code=401, detail='Invalid token')

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            users_service.authenticate_user(token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, 'Invalid token')
        mock_read_query.assert_called_once_with('''select * from tokens_blacklist where token = ?;''', (token,))
        mock_decode_token.assert_called_once_with(token)

    def test_userExists_when_userExists(self, mock_read_query):
            # Arrange
            user_data = {'user_id': 1, 'username': 'testuser'}
            mock_read_query.return_value = [(1, 'testuser')]

            # Act
            result = users_service.user_exists(user_data)

            # Assert
            self.assertTrue(result)
            mock_read_query.assert_called_once()

    def test_userExists_when_userDoesNotExist(self, mock_read_query):
        # Arrange
        user_data = {'user_id': 1, 'username': 'testuser'}
        mock_read_query.return_value = []

        # Act
        result = users_service.user_exists(user_data)

        # Assert
        self.assertFalse(result)
        mock_read_query.assert_called_once()

    @patch('services.users_service.decode_token')
    @patch('services.users_service.user_exists')
    def test_authenticateUser_when_userDoesNotExist(self, mock_user_exists, mock_decode_token, mock_read_query):
        # Arrange
        token = jwt.encode({'user_id': 1, 'username': 'testuser', 'is_admin': True}, 'test_secret', algorithm='HS256')
        mock_read_query.return_value = []
        mock_decode_token.return_value = {'user_id': 1, 'username': 'testuser', 'is_admin': True}
        mock_user_exists.return_value = False

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            users_service.authenticate_user(token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, 'Invalid user')
        mock_read_query.assert_called_once_with('''select * from tokens_blacklist where token = ?;''', (token,))
        mock_decode_token.assert_called_once_with(token)
        mock_user_exists.assert_called_once_with({'user_id': 1, 'username': 'testuser', 'is_admin': True})

    def test_userIdExists_when_userExists(self, mock_read_query):
        # Arrange
        user_id = 1
        mock_read_query.return_value = [(1,)]

        # Act
        result = users_service.user_id_exists(user_id)

        # Assert
        self.assertTrue(result)
        mock_read_query.assert_called_once()

    def test_userIdExists_when_userDoesNotExist(self, mock_read_query):
        # Arrange
        user_id = 1
        mock_read_query.return_value = []

        # Act
        result = users_service.user_id_exists(user_id)

        # Assert
        self.assertFalse(result)
        mock_read_query.assert_called_once()

    def test_getUserById_when_userExists(self, mock_read_query):
        # Arrange
        user_id = 1
        mock_read_query.return_value = [(1,)]

        # Act
        result = users_service.get_user_by_id(user_id)

        # Assert
        self.assertTrue(result)
        mock_read_query.assert_called_once()

    def test_getUserById_when_userDoesNotExist(self, mock_read_query):
        # Arrange
        user_id = 1
        mock_read_query.return_value = []

        # Act
        result = users_service.get_user_by_id(user_id)

        # Assert
        self.assertFalse(result)
        mock_read_query.assert_called_once()

    @patch('services.users_service.authenticate_user')
    @patch('services.users_service.insert_query')
    def test_blacklistUser_when_validToken(self, mock_insert_query, mock_authenticate_user, mock_read_query):
        # Arrange
        token = "valid.token.here"
        mock_authenticate_user.return_value = {'user_id': 1, 'username': 'testuser', 'is_admin': True}

        # Act
        result = users_service.blacklist_user(token)

        # Assert
        self.assertEqual(result, 'User successfully logged out.')
        mock_authenticate_user.assert_called_once_with(token)
        mock_insert_query.assert_called_once()

    @patch('services.users_service.authenticate_user')
    def test_blacklistUser_when_unauthorizedUser(self, mock_authenticate_user, mock_read_query):
        # Arrange
        token = "invalid.token.here"
        mock_authenticate_user.return_value = Mock(spec=Unauthorized)

        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            users_service.blacklist_user(token)

        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, 'Invalid token')
        mock_authenticate_user.assert_called_once_with(token)

    def test_checkIfPrivate_when_categoryIsPrivate(self, mock_read_query):
        # Arrange
        category_id = 1
        mock_read_query.return_value = [(1, 'some_data')]

        # Act
        result = users_service.check_if_private(category_id)

        # Assert
        self.assertTrue(result)
        mock_read_query.assert_called_once()

    def test_checkIfPrivate_when_categoryIsNotPrivate(self, mock_read_query):
        # Arrange
        category_id = 1
        mock_read_query.return_value = []

        # Act
        result = users_service.check_if_private(category_id)

        # Assert
        self.assertFalse(result)
        mock_read_query.assert_called_once()

    def test_giveUserRAccess_when_userHasReadAccess(self, mock_read_query):
        # Arrange
        user_id = 1
        category_id = 1
        mock_read_query.side_effect = [[(1, 1, 0)], []]  # First query returns data (read access exists)

        # Act
        result = users_service.give_user_r_access(user_id, category_id)

        # Assert
        self.assertIsNone(result)
        mock_read_query.assert_called_once()

    @patch('services.users_service.update_query')
    def test_giveUserRAccess_when_userHasWriteAccess(self, mock_update_query, mock_read_query):
        # Arrange
        user_id = 1
        category_id = 1
        mock_read_query.side_effect = [[], [(1, 1, 1)]]  # Second query returns data (write access exists)

        # Act
        result = users_service.give_user_r_access(user_id, category_id)

        # Assert
        self.assertEqual(result, f'Write access changed to read for user with id {user_id} for category with id {category_id}.')
        self.assertEqual(mock_read_query.call_count, 2)
        mock_update_query.assert_called_once()

    @patch('services.users_service.insert_query')
    def test_giveUserRAccess_when_userHasNoAccess(self, mock_insert_query, mock_read_query):
        # Arrange
        user_id = 1
        category_id = 1
        mock_read_query.side_effect = [[], []]  # Both queries return empty (no access exists)

        # Act
        result = users_service.give_user_r_access(user_id, category_id)

        # Assert
        self.assertEqual(result, f'Read access for category with id {category_id} has been given to user with id {user_id}.')
        self.assertEqual(mock_read_query.call_count, 2)
        mock_insert_query.assert_called_once()

    def test_giveUserWAccess_when_userHasWriteAccess(self, mock_read_query):
        # Arrange
        user_id = 1
        category_id = 1
        mock_read_query.side_effect = [[(1, 1, 1)], []]  # First query returns data (write access exists)

        # Act
        result = users_service.give_user_w_access(user_id, category_id)

        # Assert
        self.assertIsNone(result)
        mock_read_query.assert_called_once()

    @patch('services.users_service.update_query')
    def test_giveUserWAccess_when_userHasReadAccess(self, mock_update_query, mock_read_query):
        # Arrange
        user_id = 1
        category_id = 1
        mock_read_query.side_effect = [[], [(1, 1, 0)]]  # Second query returns data (read access exists)

        # Act
        result = users_service.give_user_w_access(user_id, category_id)

        # Assert
        self.assertEqual(result, f'Read access changed to write for user with id {user_id} for category with id {category_id}.')
        self.assertEqual(mock_read_query.call_count, 2)
        mock_update_query.assert_called_once()

    @patch('services.users_service.insert_query')
    def test_giveUserWAccess_when_userHasNoAccess(self, mock_insert_query, mock_read_query):
        # Arrange
        user_id = 1
        category_id = 1
        mock_read_query.side_effect = [[], []]  # Both queries return empty (no access exists)

        # Act
        result = users_service.give_user_w_access(user_id, category_id)

        # Assert
        self.assertEqual(result, f'Write access for category with id {category_id} has been given to user with id {user_id}.')
        self.assertEqual(mock_read_query.call_count, 2)
        mock_insert_query.assert_called_once()

    @patch('services.users_service.insert_query')
    def test_revokeAccess_when_accessExists(self, mock_insert_query, mock_read_query):
        # Arrange
        user_id = 1
        category_id = 1
        mock_read_query.return_value = [(1, 1, 1)]  # Access exists

        # Act
        result = users_service.revoke_access(user_id, category_id)

        # Assert
        self.assertIsInstance(result, NoContent)
        mock_read_query.assert_called_once()
        mock_insert_query.assert_called_once()

    def test_revokeAccess_when_accessDoesNotExist(self, mock_read_query):
        # Arrange
        user_id = 1
        category_id = 1
        mock_read_query.return_value = []  # No access exists

        # Act
        result = users_service.revoke_access(user_id, category_id)

        # Assert
        self.assertIsNone(result)
        mock_read_query.assert_called_once()

    def test_viewPrivilegedUsers_when_usersExist(self, mock_read_query):
        # Arrange
        category_id = 1
        mock_read_query.return_value = [
            (1, 'test@email.com', 'testuser', 'First', 'Last', 0),
            (2, 'test2@email.com', 'testuser2', 'First2', 'Last2', 1)
        ]

        # Act
        result = users_service.view_privileged_users(category_id)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].user_id, 1)
        self.assertEqual(result[0].email, 'test@email.com')
        self.assertEqual(result[0].username, 'testuser')
        self.assertEqual(result[0].first_name, 'First')
        self.assertEqual(result[0].last_name, 'Last')
        self.assertEqual(result[0].access_type, 0)
        mock_read_query.assert_called_once()

    def test_viewPrivilegedUsers_when_noUsers(self, mock_read_query):
        # Arrange
        category_id = 1
        mock_read_query.return_value = []

        # Act
        result = users_service.view_privileged_users(category_id)

        # Assert
        self.assertEqual(len(result), 0)
        self.assertEqual(result, [])
        mock_read_query.assert_called_once()