import unittest
from unittest.mock import Mock
from common.responses import NotFound, BadRequest
from routers import replies as reply_router
from data.models import ReplyText, ReplyResponse

mock_topics_service = Mock(spec='services.topics_service')
mock_replies_service = Mock(spec='services.replies_service')

reply_router.topics_service = mock_topics_service
reply_router.replies_service = mock_replies_service

class RepliesRouter_Should(unittest.TestCase):

    def setUp(self) -> None:
        mock_topics_service.reset_mock()
        mock_replies_service.reset_mock()

    def test_createReply_returnsNotFound_whenTopicDoesNotExist(self):

        reply_text = ReplyText(text="mock text", topic_id = 1)
        mock_topics_service.get_by_id = lambda topic_id: False

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, NotFound)

    def test_createReply_returnsBadRequest_whenReplyTextIsEmpty(self):

        reply_text = ReplyText(text="", topic_id = 1)
        mock_topics_service.get_by_id = lambda topic_id: True

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, BadRequest)

    def test_createReply_returnsBadRequest_whenReplyTextIsOver200Characters(self):

        reply_text = ReplyText(text="x" * 201, topic_id = 1)
        mock_topics_service.get_by_id = lambda topic_id: True

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, BadRequest)

    def test_createReply_returnsReplyCorrect(self):

        reply_text = ReplyText(text="mock text", topic_id = 1)
        mock_topics_service.get_by_id = lambda topic_id: True
        mock_replies_service.create = lambda reply_text, token: ReplyResponse(id=1,
                    user_id=1,
                    reply_date='2024-11-11 14:11:49',
                    reply_text='mock text')

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, ReplyResponse)

    
