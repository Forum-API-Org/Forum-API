import unittest
from unittest.mock import Mock, patch
from fastapi.exceptions import HTTPException
from common.responses import BadRequest, Unauthorized, NotFound, Forbidden
from routers import topics
from data.models import TopicResponse, CategoryResponse, TopicCreation


mock_topics_service = Mock(spec='services.topics_service')
mock_replies_service = Mock(spec='services.replies_service')
topics.topics_service = mock_topics_service
topics.replies_service = mock_replies_service


def fake_topic():
    topic = Mock(spec=TopicResponse)
    topic.top_name = 'Test Topic'
    topic.user_id = 1
    topic.topic_date = '2021-01-01 00:00:00'
    topic.is_locked = False
    topic.best_reply_id = None

    return topic


def fake_topic_creation():
    topic = Mock(spec=TopicCreation)
    topic.top_name = 'Test Topic'
    topic.category_id = 1

    return topic


def fake_category():
    category = Mock(spec=CategoryResponse)
    category.cat_name = 'Test Category'
    category.creator_id = 1
    category.is_locked = False
    category.is_private = False

    return category


class TestTopicsRouter(unittest.TestCase):

    def setUp(self):
        mock_topics_service.reset_mock()

    # def test_get_all_topics(self):
    #     with patch('routers.topics.authenticate_user') as authenticate_user:
    #         authenticate_user.return_value = {'user_id': 1}
    #         test_topic = fake_topic()
    #         mock_topics_service.get_all_topics = lambda: [test_topic]
    #
    #         result = topics.get_topics('token', search=None, sort_by=None, sort_order=None, limit=10, offset=0)
    #
    #         self.assertEqual(result, [test_topic])

    def test_get_topic_by_id(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1}
            test_topic = fake_topic()
            mock_topics_service.check_category = lambda id: 1
            mock_topics_service.check_if_private = lambda id: False
            mock_topics_service.exists = lambda id: True
            mock_topics_service.get_by_id = lambda id: test_topic

            result = topics.get_topic_by_id(1, 'token')

            self.assertEqual(result, test_topic)

    # def test_create_topic(self):
    #     with patch('routers.topics.authenticate_user') as authenticate_user:
    #         authenticate_user.return_value = {'user_id': 1}
    #         creation = fake_topic_creation()
    #         mock_topics_service.top_name_exists = lambda top_name: False
    #         mock_topics_service.create = lambda top_name, category_id, user_id: (creation.top_name, category_id, user_id)
    #
    #         result = topics.create_topic(creation, 'token')
    #
    #         self.assertEqual(result, fake_topic())

    # def test_get_topic_by_id_topic_not_found(self):
    #     with patch('routers.topics.authenticate_user') as authenticate_user:
    #         authenticate_user.return_value = {'user_id': 1}
    #         mock_topics_service.exists = lambda id: False
    #
    #         with self.assertEqual(topics.get_topic_by_id(1, 'token'), NotFound('Topic not found')):
    #             topics.get_topic_by_id(1, 'token')
    #
    # def test_get_topic_by_id_topic_private(self):
    #     with patch('routers.topics.authenticate_user') as authenticate_user:
    #         authenticate_user.return_value = {'user_id': 1}
    #         mock_topics_service.exists = lambda id: True
    #         mock_topics_service.get_by_id = lambda id: fake_topic()
    #         mock_topics_service.check_category = lambda id: 1
    #         mock_topics_service.check_if_private = lambda id: True
    #         mock_topics_service.check_user_access = lambda user_id, category_id: 0
    #
    #         with self.assertEqual(topics.get_topic_by_id(1, 'token'), Unauthorized()):
    #             topics.get_topic_by_id(1, 'token')

    # def test_get_topic_by_id_topic_locked(self):
    #     with patch('routers.topics.authenticate_user') as authenticate_user:
    #         authenticate_user.return_value = {'user_id': 1}
    #         mock_topics_service.exists = lambda id: True
    #         mock_topics_service.get_by_id = lambda id: fake_topic()
    #         mock_topics_service.check_category = lambda id: 1
    #         mock_topics_service.check_if_private = lambda id: False
    #         mock_topics_service.check_if_locked = lambda id: True
    #
    #         result = topics.get_topic_by_id(1, 'token')

            # self.assertEqual(result.status_code, 403)

    def test_lock_topic(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_topics_service.exists = lambda id: True
            mock_topics_service.lock = lambda id: True

            result = topics.lock_topic(1, 'token')

            self.assertEqual(result, True)

    def test_lock_topic_not_admin(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
            mock_topics_service.exists = lambda id: True
            mock_topics_service.lock = lambda id: True

            result = topics.lock_topic(1, 'token')

            self.assertEqual(result.status_code, 403)

    def test_lock_topic_not_found(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_topics_service.exists = lambda id: False
            mock_topics_service.lock = lambda id: True

            result = topics.lock_topic(1, 'token')

            self.assertEqual(result.status_code, 404)

    def test_unlock_topic(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_topics_service.exists = lambda id: True
            mock_topics_service.unlock = lambda id: True

            result = topics.unlock_topic(1, 'token')

            self.assertEqual(result, True)

    def test_unlock_topic_not_admin(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
            mock_topics_service.exists = lambda id: True
            mock_topics_service.unlock = lambda id: True

            result = topics.unlock_topic(1, 'token')

            self.assertEqual(result.status_code, 403)

    def test_unlock_topic_not_found(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1, 'is_admin': True}
            mock_topics_service.exists = lambda id: False
            mock_topics_service.unlock = lambda id: True

            result = topics.unlock_topic(1, 'token')

            self.assertEqual(result.status_code, 404)

    def test_choose_best_reply(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1}
            mock_topics_service.exists = lambda id: True
            mock_replies_service.reply_exists = lambda id: True
            mock_topics_service.is_owner = lambda user_id, topic_id: True
            mock_topics_service.reply_belongs_to_topic = lambda reply_id, topic_id: True
            mock_topics_service.make_best_reply = lambda topic_id, reply_id: True

            result = topics.choose_best_reply(1, 1, 'token')

            self.assertEqual(result, True)

    def test_choose_best_reply_topic_not_found(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1}
            mock_topics_service.exists = lambda id: False

            result = topics.choose_best_reply(1, 1, 'token')

            self.assertEqual(result.status_code, 404)

    def test_choose_best_reply_reply_not_found(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1}
            mock_topics_service.exists = lambda id: True
            mock_replies_service.reply_exists = lambda id: False

            result = topics.choose_best_reply(1, 1, 'token')

            self.assertEqual(result.status_code, 404)

    def test_choose_best_reply_not_owner(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1}
            mock_topics_service.exists = lambda id: True
            mock_replies_service.reply_exists = lambda id: True
            mock_topics_service.is_owner = lambda user_id, topic_id: False

            result = topics.choose_best_reply(1, 1, 'token')

            self.assertEqual(result.status_code, 403)

    def test_choose_best_reply_reply_not_belongs_to_topic(self):
        with patch('routers.topics.authenticate_user') as authenticate_user:
            authenticate_user.return_value = {'user_id': 1}
            mock_topics_service.exists = lambda id: True
            mock_replies_service.reply_exists = lambda id: True
            mock_topics_service.is_owner = lambda user_id, topic_id: True
            mock_topics_service.reply_belongs_to_topic = lambda reply_id, topic_id: False

            result = topics.choose_best_reply(1, 1, 'token')

            self.assertEqual(result.status_code, 400)


if __name__ == '__main__':
    unittest.main()






