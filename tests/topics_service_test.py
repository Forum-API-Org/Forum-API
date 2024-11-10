import unittest
from unittest.mock import patch, Mock
from datetime import datetime
from common.responses import BadRequest
from data.models import CategoryResponse, TopicResponse, Topic, Reply, ReplyResponse
from services import categories_service, topics_service
from fastapi.exceptions import HTTPException


@patch('services.topics_service.read_query', autospec=True)
class TopicsServiceShould(unittest.TestCase):

    def test_view_replies(self, mock_read_query):
        mock_read_query.return_value = [(1, '2024-11-08 18:19:15', 'Reply')]

        result = topics_service.view_replies(1)

        self.assertEqual(result, [ReplyResponse(
            user_id=1,
            reply_date=datetime(2024, 11, 8, 18, 19, 15),
            reply_text='Reply'
        )])

    def test_get_by_id(self, mock_read_query):
        mock_read_query.side_effect = [[(1, 'Topic', 1, '2024-11-08 18:19:15', 0, 0)], [(1, '2024-11-08 18:19:15', 'Reply')]]

        result = topics_service.get_by_id(1)

        self.assertEqual(result, TopicResponse(
            top_name='Topic',
            user_id=1,
            topic_date='2024-11-08 18:19:15',
            is_locked=0,
            best_reply_id=0,
            replies=[ReplyResponse(user_id=1, reply_date=datetime(2024, 11, 8, 18, 19, 15), reply_text='Reply')]
        ))

    def test_get_by_id_when_topic_does_not_exist(self, mock_read_query):
        mock_read_query.return_value = []

        result = topics_service.get_by_id(1)
        self.assertIsNone(result)

    def test_get_by_id_when_topic_has_no_replies(self, mock_read_query):
        mock_read_query.side_effect = [[(1, 'Topic', 1, '2024-11-08 18:19:15', 0, 0)], []]

        result = topics_service.get_by_id(1)

        self.assertEqual(result, TopicResponse(
            top_name='Topic',
            user_id=1,
            topic_date='2024-11-08 18:19:15',
            is_locked=0,
            best_reply_id=0,
            replies=[]
        ))

    def test_get_by_id_when_topic_has_multiple_replies(self, mock_read_query):
        mock_read_query.side_effect = [[(1, 'Topic', 1, '2024-11-08 18:19:15', 0, 0)], [(1, '2024-11-08 18:19:15', 'Reply1'), (2, '2024-11-08 18:19:15', 'Reply2')]]

        result = topics_service.get_by_id(1)

        self.assertEqual(result, TopicResponse(
            top_name='Topic',
            user_id=1,
            topic_date='2024-11-08 18:19:15',
            is_locked=0,
            best_reply_id=0,
            replies=[ReplyResponse(user_id=1, reply_date=datetime(2024, 11, 8, 18, 19, 15), reply_text='Reply1'),
                     ReplyResponse(user_id=2, reply_date=datetime(2024, 11, 8, 18, 19, 15), reply_text='Reply2')]
        ))

    def test_exists(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Topic')]

        result = topics_service.exists(1)

        self.assertTrue(result)

    def test_exists_when_topic_does_not_exist(self, mock_read_query):
        mock_read_query.return_value = []

        result = topics_service.exists(1)

        self.assertFalse(result)

    def test_check_category(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Category')]

        result = topics_service.check_category(1)

        self.assertEqual(result, 1)

    def test_topic_name_exists(self, mock_read_query):
        mock_read_query.return_value = [(1, 'Topic')]

        result = topics_service.top_name_exists('Topic')

        self.assertTrue(result)

    def test_topic_name_exists_when_topic_does_not_exist(self, mock_read_query):
        mock_read_query.return_value = []

        result = topics_service.top_name_exists('Topic')

        self.assertFalse(result)

    def test_check_if_locked(self, mock_read_query):
        mock_read_query.return_value = [(1,)]

        result = topics_service.check_if_locked(1)

        self.assertTrue(result)

    def test_check_if_locked_when_topic_is_not_locked(self, mock_read_query):
        mock_read_query.return_value = [(0,)]

        result = topics_service.check_if_locked(1)

        self.assertFalse(result)

    def test_reply_belongs_to_topic(self, mock_read_query):
        mock_read_query.return_value = [(1,)]

        result = topics_service.reply_belongs_to_topic(1, 1)

        self.assertTrue(result)

    def test_reply_belongs_to_topic_when_reply_does_not_belong_to_topic(self, mock_read_query):
        mock_read_query.return_value = [(0,)]

        result = topics_service.reply_belongs_to_topic(1, 1)

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
