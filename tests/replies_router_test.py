import unittest
from unittest.mock import Mock
from common.responses import NotFound, BadRequest
from routers import replies as reply_router
from data.models import ReplyText, Reply

mock_topics_service = Mock(spec='services.topics_service')
mock_replies_service = Mock(spec='services.replies_service')

reply_router.topics_service = mock_topics_service
reply_router.replies_service = mock_replies_service

class RepliesRouter_Should(unittest.TestCase):

    def setUp(self) -> None:
        mock_topics_service.reset_mock()
        mock_replies_service.reset_mock()

    def test_createReply_returnsNotFound_whenTopicDoesNotExist(self):

        topic_id = 1
        reply_text = ReplyText(text="mock text")
        mock_topics_service.get_by_id = lambda topic_id: False

        result = reply_router.create_reply(topic_id, reply_text, token='mock-token')

        self.assertIsInstance(result, NotFound)

    def test_createReply_returnsBadRequest_whenReplyTextIsEmpty(self):

        topic_id = 1
        reply_text = ReplyText(text="")
        mock_topics_service.get_by_id = lambda topic_id: True

        result = reply_router.create_reply(topic_id, reply_text, token='mock-token')

        self.assertIsInstance(result, BadRequest)

    def test_createReply_returnsBadRequest_whenReplyTextIsOver200Characters(self):

        topic_id = 1
        reply_text = ReplyText(text="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        mock_topics_service.get_by_id = lambda topic_id: True

        result = reply_router.create_reply(topic_id, reply_text, token='mock-token')

        self.assertIsInstance(result, BadRequest)

    def test_createReply_returnsReplyCorrect(self):

        topic_id = 1
        reply_text = ReplyText(text="mock text")
        mock_topics_service.get_by_id = lambda topic_id: True
        mock_replies_service.create = lambda topic_id, reply_text, token: Reply(id=1,
                    topic_id=1,
                    user_id=1,
                    reply_date='2024-11-11 14:11:49',
                    reply_text='mock text',
                    replies_reply_id=1)

        result = reply_router.create_reply(topic_id, reply_text, token='mock-token')

        self.assertIsInstance(result, Reply)

    
