import unittest
from unittest.mock import Mock, patch
from fastapi.exceptions import HTTPException
from common.responses import BadRequest, Unauthorized, NotFound, Forbidden
from routers import users as users_router
from data.models import User, LoginData, UserCategoryAccess, UserAccessResponse


def fake_user():
    admin = Mock(spec=User)
    admin.id=1,
    admin.email="test@example.com",
    admin.username="testuser",
    admin.password="password123!",
    admin.first_name="Test",
    admin.last_name="User",
    admin.is_admin=False
        
    return admin

def fake_admin():
    admin = Mock(spec=User)
    admin.is_admin = True
    return admin

class UsersRouter_Should(unittest.TestCase):

    @patch('services.users_service.create_user')
    def test_register_user(self, mock_create_user):
        # Arrange
        user_info = User(
            email="test@example.com",
            username="testuser",
            password="password123!",
            first_name="Test",
            last_name="User"
        )
        
        mock_create_user.return_value = fake_user()

        # Act
        result = users_router.register_user(user_info)

        # Assert
        self.assertEqual(result.id, fake_user().id)
        self.assertEqual(result.email, fake_user().email)
        self.assertEqual(result.username, fake_user().username)
        self.assertEqual(result.first_name, fake_user().first_name)
        self.assertEqual(result.last_name, fake_user().last_name)
        mock_create_user.assert_called_once()

    @patch('services.users_service.create_token')
    @patch('services.users_service.login_user')
    def test_login_user_when_validCredentials(self, mock_login_user, mock_create_token):
        # Arrange
        login_data = LoginData(username="testuser", password="password123!")
        user_data = Mock(
            id=1,
            username="testuser",
            password="hashed_password",
            is_admin=False
        )
        mock_login_user.return_value = user_data
        mock_create_token.return_value = "fake_token"

        # Act
        result = users_router.login_user(login_data)

        # Assert
        self.assertEqual(result, {'token': 'fake_token'})
        mock_login_user.assert_called_once_with(login_data)
        mock_create_token.assert_called_once_with(user_data)

    @patch('services.users_service.login_user')
    def test_login_user_when_invalidCredentials(self, mock_login_user):
        # Arrange
        login_data = LoginData(username="invaliduser", password="wrongpassword")
        mock_login_user.return_value = None

        # Act
        result = users_router.login_user(login_data)

        # Assert
        self.assertIsInstance(result, Unauthorized)
        self.assertEqual(result.status_code, 401)
        self.assertEqual(result.body, b'Invalid username or password!')
        mock_login_user.assert_called_once_with(login_data)

    @patch('services.users_service.blacklist_user')
    def test_logout_user_when_validToken(self, mock_blacklist_user):
        # Arrange
        token = "valid.token.here"
        mock_blacklist_user.return_value = "User successfully logged out."

        # Act
        result = users_router.logout_user(token)

        # Assert
        self.assertEqual(result, {'message': 'User successfully logged out.'})
        mock_blacklist_user.assert_called_once_with(token)

    @patch('services.users_service.blacklist_user')
    def test_logout_user_when_invalidToken(self, mock_blacklist_user):
        # Arrange
        token = "invalid.token.here"
        mock_blacklist_user.side_effect = HTTPException(status_code=401, detail='Invalid token')

        # Act
        result = users_router.logout_user(token)

        # Assert
        self.assertIsInstance(result, BadRequest)
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.body, b'Invalid token')
        mock_blacklist_user.assert_called_once_with(token)

    @patch('routers.users.categories_service.exists')
    def test_giveUserReadAccess_when_categoryDoesNotExist(self, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=999)
        token = "valid.token"
        mock_exists.return_value = False

        # Act
        result = users_router.give_user_read_access(user_category, token)

        # Assert
        self.assertIsInstance(result, NotFound)
        self.assertEqual(result.body, b'Category does not exist!')
        mock_exists.assert_called_once_with(user_category.category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    def test_giveUserReadAccess_when_categoryNotPrivate(self, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = False

        # Act
        result = users_router.give_user_read_access(user_category, token)

        # Assert
        self.assertIsInstance(result, BadRequest)
        self.assertEqual(result.body, f'Category {user_category.category_id} is not private.'.encode())
        mock_check_private.assert_called_once_with(user_category.category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    def test_giveUserReadAccess_when_userDoesNotExist(self, mock_user_exists, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=999, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = False

        # Act
        result = users_router.give_user_read_access(user_category, token)

        # Assert
        self.assertIsInstance(result, NotFound)
        self.assertEqual(result.body, f'User with id {user_category.user_id} does not exist!'.encode())
        mock_user_exists.assert_called_once_with(user_category.user_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    def test_giveUserReadAccess_when_notAdmin(self, mock_is_admin, mock_auth, mock_user_exists, 
                                            mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = True
        mock_auth.return_value = {'is_admin': False}
        mock_is_admin.return_value = False

        # Act
        result = users_router.give_user_read_access(user_category, token)

        # Assert
        self.assertIsInstance(result, Forbidden)
        self.assertEqual(result.body, b'Only admins can access this endpoint')

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    @patch('routers.users.users_service.give_user_r_access')
    def test_giveUserReadAccess_when_adminSuccess(self, mock_give_access, mock_is_admin, mock_auth, 
                                                mock_user_exists, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = True
        mock_auth.return_value = {'is_admin': True}
        mock_is_admin.return_value = True
        mock_give_access.return_value = "Read access granted"

        # Act
        result = users_router.give_user_read_access(user_category, token)

        # Assert
        self.assertEqual(result, "Read access granted")
        mock_give_access.assert_called_once_with(user_category.user_id, user_category.category_id)

    @patch('routers.users.categories_service.exists')
    def test_giveUserWriteAccess_when_categoryDoesNotExist(self, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=999)
        token = "valid.token"
        mock_exists.return_value = False

        # Act
        result = users_router.give_user_write_access(user_category, token)

        # Assert
        self.assertIsInstance(result, NotFound)
        self.assertEqual(result.body, b'Category does not exist!')
        mock_exists.assert_called_once_with(user_category.category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    def test_giveUserWriteAccess_when_categoryNotPrivate(self, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = False

        # Act
        result = users_router.give_user_write_access(user_category, token)

        # Assert
        self.assertIsInstance(result, BadRequest)
        self.assertEqual(result.body, f'Category {user_category.category_id} is not private.'.encode())
        mock_check_private.assert_called_once_with(user_category.category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    def test_giveUserWriteAccess_when_userDoesNotExist(self, mock_user_exists, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=999, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = False

        # Act
        result = users_router.give_user_write_access(user_category, token)

        # Assert
        self.assertIsInstance(result, NotFound)
        self.assertEqual(result.body, f'User with id {user_category.user_id} does not exist!'.encode())
        mock_user_exists.assert_called_once_with(user_category.user_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    def test_giveUserWriteAccess_when_notAdmin(self, mock_is_admin, mock_auth, mock_user_exists, 
                                            mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = True
        mock_auth.return_value = {'is_admin': False}
        mock_is_admin.return_value = False

        # Act
        result = users_router.give_user_write_access(user_category, token)

        # Assert
        self.assertIsInstance(result, Forbidden)
        self.assertEqual(result.body, b'Only admins can access this endpoint')

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    @patch('routers.users.users_service.give_user_w_access')
    def test_giveUserWriteAccess_when_adminSuccess(self, mock_give_access, mock_is_admin, mock_auth, 
                                                mock_user_exists, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = True
        mock_auth.return_value = {'is_admin': True}
        mock_is_admin.return_value = True
        mock_give_access.return_value = "Write access granted"

        # Act
        result = users_router.give_user_write_access(user_category, token)

        # Assert
        self.assertEqual(result, "Write access granted")
        mock_give_access.assert_called_once_with(user_category.user_id, user_category.category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    @patch('routers.users.users_service.give_user_w_access')
    def test_giveUserWriteAccess_when_userAlreadyHasAccess(self, mock_give_access, mock_is_admin, 
                                                        mock_auth, mock_user_exists, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = True
        mock_auth.return_value = {'is_admin': True}
        mock_is_admin.return_value = True
        mock_give_access.return_value = None

        # Act
        result = users_router.give_user_write_access(user_category, token)

        # Assert
        self.assertIsInstance(result, BadRequest)
        self.assertEqual(result.body, 
            f'User with id {user_category.user_id} already has write access for category with id {user_category.category_id}!'.encode())
        
    @patch('routers.users.categories_service.exists')
    def test_revokeUserAccess_when_categoryDoesNotExist(self, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=999)
        token = "valid.token"
        mock_exists.return_value = False

        # Act
        result = users_router.revoke_user_access(token, user_category)

        # Assert
        self.assertIsInstance(result, NotFound)
        self.assertEqual(result.body, b'Category does not exist!')
        mock_exists.assert_called_once_with(user_category.category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    def test_revokeUserAccess_when_categoryNotPrivate(self, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = False

        # Act
        result = users_router.revoke_user_access(token, user_category)

        # Assert
        self.assertIsInstance(result, BadRequest)
        self.assertEqual(result.body, f'Category {user_category.category_id} is not private.'.encode())
        mock_check_private.assert_called_once_with(user_category.category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    def test_revokeUserAccess_when_userDoesNotExist(self, mock_user_exists, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=999, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = False

        # Act
        result = users_router.revoke_user_access(token, user_category)

        # Assert
        self.assertIsInstance(result, NotFound)
        self.assertEqual(result.body, f'User with id {user_category.user_id} does not exist!'.encode())
        mock_user_exists.assert_called_once_with(user_category.user_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    def test_revokeUserAccess_when_notAdmin(self, mock_is_admin, mock_auth, mock_user_exists, 
                                            mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = True
        mock_auth.return_value = {'is_admin': False}
        mock_is_admin.return_value = False

        # Act
        result = users_router.revoke_user_access(token, user_category)

        # Assert
        self.assertIsInstance(result, Forbidden)
        self.assertEqual(result.body, b'Only admins can access this endpoint')

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    @patch('routers.users.users_service.revoke_access')
    def test_revokeUserAccess_when_adminSuccess(self, mock_revoke_access, mock_is_admin, mock_auth, 
                                                mock_user_exists, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = True
        mock_auth.return_value = {'is_admin': True}
        mock_is_admin.return_value = True
        mock_revoke_access.return_value = "Access revoked"

        # Act
        result = users_router.revoke_user_access(token, user_category)

        # Assert
        self.assertEqual(result, "Access revoked")
        mock_revoke_access.assert_called_once_with(user_category.user_id, user_category.category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.user_id_exists')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    @patch('routers.users.users_service.revoke_access')
    def test_revokeUserAccess_when_userHasNoAccess(self, mock_revoke_access, mock_is_admin, 
                                                   mock_auth, mock_user_exists, mock_check_private, mock_exists):
        # Arrange
        user_category = UserCategoryAccess(user_id=1, category_id=1)
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_user_exists.return_value = True
        mock_auth.return_value = {'is_admin': True}
        mock_is_admin.return_value = True
        mock_revoke_access.return_value = None

        # Act
        result = users_router.revoke_user_access(token, user_category)

        # Assert
        self.assertIsInstance(result, BadRequest)
        self.assertEqual(result.body, 
            f'User with id {user_category.user_id} has no existing access for category with id {user_category.category_id}!'.encode())
        
    @patch('routers.users.categories_service.exists')
    def test_viewPrivilegedUsers_when_categoryDoesNotExist(self, mock_exists):
        # Arrange
        category_id = 999
        token = "valid.token"
        mock_exists.return_value = False

        # Act
        result = users_router.view_privileged_users(token, category_id)

        # Assert
        self.assertIsInstance(result, NotFound)
        self.assertEqual(result.body, b'Category does not exist!')
        mock_exists.assert_called_once_with(category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    def test_viewPrivilegedUsers_when_categoryNotPrivate(self, mock_check_private, mock_exists):
        # Arrange
        category_id = 1
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = False

        # Act
        result = users_router.view_privileged_users(token, category_id)

        # Assert
        self.assertIsInstance(result, BadRequest)
        self.assertEqual(result.body, f'Category {category_id} is not private.'.encode())
        mock_check_private.assert_called_once_with(category_id)

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    def test_viewPrivilegedUsers_when_notAdmin(self, mock_is_admin, mock_auth, mock_check_private, mock_exists):
        # Arrange
        category_id = 1
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_auth.return_value = {'is_admin': False}
        mock_is_admin.return_value = False

        # Act
        result = users_router.view_privileged_users(token, category_id)

        # Assert
        self.assertIsInstance(result, Forbidden)
        self.assertEqual(result.body, b'Only admins can access this endpoint')

    @patch('routers.users.categories_service.exists')
    @patch('routers.users.users_service.check_if_private')
    @patch('routers.users.users_service.authenticate_user')
    @patch('routers.users.users_service.is_admin')
    @patch('routers.users.view_privileged_users')
    def test_viewPrivilegedUsers_when_adminSuccess(self, mock_view_privileged, mock_is_admin, mock_auth, 
                                                   mock_check_private, mock_exists):
        # Arrange
        category_id = 1
        token = "valid.token"
        mock_exists.return_value = True
        mock_check_private.return_value = True
        mock_auth.return_value = {'is_admin': True}
        mock_is_admin.return_value = True
        mock_view_privileged.return_value = [
            UserAccessResponse(id=1, email="test@example.com", username="testuser", first_name="Test", last_name="User", access='read'),
            UserAccessResponse(id=2, email="test2@example.com", username="testuser2", first_name="Test2", last_name="User2", access='write')
        ]

        # Act
        result = users_router.view_privileged_users(token, category_id)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].email, "test@example.com")
        self.assertEqual(result[0].username, "testuser")
        self.assertEqual(result[0].first_name, "Test")
        self.assertEqual(result[0].last_name, "User")
        self.assertEqual(result[0].access, 'read')
        mock_view_privileged.assert_called_once_with(token, category_id)