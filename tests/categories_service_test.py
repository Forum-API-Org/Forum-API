import unittest
from unittest.mock import patch, Mock
from common.responses import BadRequest
from data.models import CategoryResponse, TopicResponse
from services import categories_service
from fastapi.exceptions import HTTPException


@patch('services.categories_service.read_query')
class CategoriesServiceShould(unittest.TestCase):

    def test_get_categories(self, mock_read_query):
        mock_read_query.return_value = [('Category', 1, 0, 0)]

        result = categories_service.get_categories()

        self.assertEqual(result, [CategoryResponse(
            cat_name='Category',
            creator_id=1,
            is_locked=0,
            is_private=0
        )])

    def test_view_topics(self, mock_read_query):
        mock_read_query.return_value = [('Topic', 1, '2024-11-08 18:19:15', 0, 0)]

        result = categories_service.view_topics(1)

        self.assertEqual(result, [TopicResponse(
            top_name='Topic',
            user_id=1,
            topic_date='2024-11-08 18:19:15',
            is_locked=0,
            best_reply_id=0
        )])

    def test_get_by_id(self, mock_read_query):
        mock_read_query.side_effect = [[('Category', 1, 0, 0)], [('Topic', 1, '2024-11-08 18:19:15', 0, 0)]]

        result = categories_service.get_by_id(1)

        self.assertEqual(result, CategoryResponse(
            cat_name='Category',
            creator_id=1,
            is_locked=0,
            is_private=0,
            topics=[TopicResponse(
                top_name='Topic',
                user_id=1,
                topic_date='2024-11-08 18:19:15',
                is_locked=0,
                best_reply_id=0
            )]
        ))

    def test_get_by_id_when_category_does_not_exist(self, mock_read_query):
        mock_read_query.return_value = []

        result = categories_service.get_by_id(1)

        self.assertIsNone(result)

    def test_exists(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Category')]

        result = categories_service.exists(1)

        self.assertTrue(result)

    def test_cat_name_exists(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Category')]

        result = categories_service.cat_name_exists('Category')

        self.assertTrue(result)

    def test_cat_name_exists_when_category_does_not_exist(self, mock_read_query):
        mock_read_query.return_value = []

        result = categories_service.cat_name_exists('Category')

        self.assertFalse(result)

    def test_lock(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Category')]

        result = categories_service.lock(1)

        self.assertTrue(result)

    def test_make_private(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Category')]

        result = categories_service.make_private(1)

        self.assertTrue(result)

    def test_is_owner(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Category')]

        result = categories_service.is_owner(1, 1)

        self.assertTrue(result)

    def test_check_user_access(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Category')]

        result = categories_service.check_user_access(1, 1)

        self.assertTrue(result)







