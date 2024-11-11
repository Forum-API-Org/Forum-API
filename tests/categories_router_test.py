import unittest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from data.models import CategoryResponse, Category, CategoryCreation
from routers import categories
from main import app  # Assuming your FastAPI app is in main.py

mock_categories_service = Mock(spec='services.categories_service')
categories.categories_service = mock_categories_service

def fake_category():
    category = Mock(spec=CategoryResponse)
    category.cat_name = 'Test Category'
    category.creator_id = 1
    category.is_locked = False
    category.is_private = False
    return category

def fake_category_creation():
    category = Mock(spec=CategoryCreation)
    category.cat_name = 'Test Category'
    return category


class TestCategoriesRouter(unittest.TestCase):

    def setUp(self):
        mock_categories_service.reset_mock()

    def test_get_all_categories(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1}
            test_category = fake_category()
            mock_categories_service.get_categories = lambda: [test_category]

            result = categories.get_all_categories('token')

            self.assertEqual(result, [test_category])

    def test_get_category_by_id(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1}
            test_category = fake_category()
            mock_categories_service.exists = lambda id: True
            mock_categories_service.check_if_private = lambda id: False
            mock_categories_service.get_by_id = lambda id: test_category

            result = categories.get_category_by_id(1, 'token')

            self.assertEqual(result, test_category)

    # def test_create_category(self):
    #     with patch('routers.categories.authenticate_user') as authenticate_user:
    #         authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
    #         creation = fake_category_creation()
    #         mock_categories_service.cat_name_exists = lambda cat_name: False
    #         mock_categories_service.create = lambda cat_name, creator_id: (creation.cat_name, creator_id)
    #
    #         result = categories.create_category(creation, 'token')
    #
    #         self.assertEqual(result, fake_category())

    def test_lock_category(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_categories_service.exists = lambda id: True
            mock_categories_service.lock = lambda id: True

            result = categories.lock_category(1, 'token')

            self.assertEqual(result, True)

    def test_lock_category_not_admin(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
            mock_categories_service.exists = lambda id: True
            mock_categories_service.lock = lambda id: True

            result = categories.lock_category(1, 'token')

            self.assertEqual(result.status_code, 403)

    def test_lock_category_not_found(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_categories_service.exists = lambda id: False
            mock_categories_service.lock = lambda id: True

            result = categories.lock_category(1, 'token')

            self.assertEqual(result.status_code, 404)

    def test_make_category_private(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_categories_service.exists = lambda id: True
            mock_categories_service.make_private = lambda id: True

            result = categories.make_category_private(1, 'token')

            self.assertEqual(result, True)

    def test_make_category_private_not_admin(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
            mock_categories_service.exists = lambda id: True
            mock_categories_service.make_private = lambda id: True

            result = categories.make_category_private(1, 'token')

            self.assertEqual(result.status_code, 403)

    def test_make_category_private_not_found(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_categories_service.exists = lambda id: False
            mock_categories_service.make_private = lambda id: True

            result = categories.make_category_private(1, 'token')
            self.assertEqual(result.status_code, 404)

    def test_unlock_category(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_categories_service.exists = lambda id: True
            mock_categories_service.unlock = lambda id: True

            result = categories.unlock_category(1, 'token')

            self.assertEqual(result, True)

    def test_unlock_category_not_admin(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
            mock_categories_service.exists = lambda id: True
            mock_categories_service.unlock = lambda id: True

            result = categories.unlock_category(1, 'token')

            self.assertEqual(result.status_code, 403)

    def test_unlock_category_not_found(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_categories_service.exists = lambda id: False
            mock_categories_service.unlock = lambda id: True

            result = categories.unlock_category(1, 'token')

            self.assertEqual(result.status_code, 404)

    def test_make_category_public(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_categories_service.exists = lambda id: True
            mock_categories_service.make_public = lambda id: True

            result = categories.make_category_public(1, 'token')

            self.assertEqual(result, True)

    def test_make_category_public_not_admin(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
            mock_categories_service.exists = lambda id: True
            mock_categories_service.make_public = lambda id: True

            result = categories.make_category_public(1, 'token')

            self.assertEqual(result.status_code, 403)

    def test_make_category_public_not_found(self):
        with patch('routers.categories.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_categories_service.exists = lambda id: False
            mock_categories_service.make_public = lambda id: True

            result = categories.make_category_public(1, 'token')

            self.assertEqual(result.status_code, 404)


if __name__ == '__main__':
    unittest.main()




