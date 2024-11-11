# import unittest
# from unittest.mock import Mock, patch
# from common.responses import NotFound, BadRequest, Unauthorized
# from routers import replies as reply_router
# from data.models import ReplyText, ReplyResponse

# mock_topics_service = Mock(spec='services.topics_service')
# mock_replies_service = Mock(spec='services.replies_service')
# mock_categories_service = Mock(spec='services.categories_service')
# mock_users_service = Mock(spec='services.users_service')

# reply_router.topics_service = mock_topics_service
# reply_router.replies_service = mock_replies_service
# reply_router.categories_service = mock_categories_service
# reply_router.users_service = mock_users_service

# class RepliesRouter_Should(unittest.TestCase):

#     def setUp(self) -> None:
#         mock_topics_service.reset_mock()
#         mock_replies_service.reset_mock()
#         mock_categories_service.reset_mock()
#         mock_users_service.reset_mock()

       
#     @patch("services.users_service.authenticate_user")  # Patching authenticate_user in users_service
#     @patch("services.topics_service.get_by_id")  # Patching get_by_id in topics_service
#     def test_createReply_returnsNotFound_whenTopicDoesNotExist(self, mock_get_by_id, mock_authenticate_user):
#             reply_text = ReplyText(text="mock text", topic_id = 1)
#             mock_topics_service.get_by_id = lambda topic_id: False

#             result = reply_router.create_reply(reply_text, token='mock-token')

#             self.assertIsInstance(result, NotFound)         


#     def test_createReply_returnsBadRequest_whenReplyTextIsEmpty(self):

#         reply_text = ReplyText(text="", topic_id = 1)
#         mock_topics_service.get_by_id = lambda topic_id: True

#         result = reply_router.create_reply(reply_text, token='mock-token')

#         self.assertIsInstance(result, BadRequest)

#     def test_createReply_returnsBadRequest_whenReplyTextIsOver200Characters(self):

#         reply_text = ReplyText(text="x" * 201, topic_id = 1)
#         mock_topics_service.get_by_id = lambda topic_id: True

#         result = reply_router.create_reply(reply_text, token='mock-token')

#         self.assertIsInstance(result, BadRequest)

#     def test_createReply_returnsReplyCorrect(self):

#         reply_text = ReplyText(text="mock text", topic_id = 1)
#         mock_topics_service.get_by_id = lambda topic_id: True
#         mock_replies_service.create = lambda reply_text, token: ReplyResponse(id=1,
#                     user_id=1,
#                     reply_date='2024-11-11 14:11:49',
#                     reply_text='mock text')

#         result = reply_router.create_reply(reply_text, token='mock-token')

#         self.assertIsInstance(result, ReplyResponse)

    


import unittest
from unittest.mock import Mock
from common.responses import NotFound, BadRequest, Unauthorized
from routers import replies as reply_router
from data.models import ReplyText, ReplyResponse

# Mocking the services used in the replies router
mock_topics_service = Mock()
mock_replies_service = Mock()
mock_categories_service = Mock()
mock_users_service = Mock()

# Assigning the mocked services to the router
reply_router.topics_service = mock_topics_service
reply_router.replies_service = mock_replies_service
reply_router.categories_service = mock_categories_service
reply_router.users_service = mock_users_service

class RepliesRouter_Should(unittest.TestCase):

    def setUp(self) -> None:
        # Reset mocks before each test
        mock_topics_service.reset_mock()
        mock_replies_service.reset_mock()
        mock_categories_service.reset_mock()
        mock_users_service.reset_mock()

    def test_createReply_returnsNotFound_whenTopicDoesNotExist(self):
        reply_text = ReplyText(text="mock text", topic_id=1)

        # Simulate topic not existing
        mock_topics_service.get_by_id.return_value = None

        result = reply_router.create_reply(reply_text, token='mock-token')
        
        self.assertIsInstance(result, NotFound)

    def test_createReply_returnsUnauthorized_whenCategoryIsLocked(self):
        reply_text = ReplyText(text="mock text", topic_id=1)

        # Simulate topic exists and category is locked
        mock_topics_service.get_by_id.return_value = True
        mock_topics_service.check_category.return_value = 10
        mock_categories_service.check_if_locked.return_value = True

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, Unauthorized)

    def test_createReply_returnsUnauthorized_whenCategoryIsPrivateAndUserHasNoAccess(self):
        reply_text = ReplyText(text="mock text", topic_id=1)

        # Set up mock return values for access checks
        mock_topics_service.get_by_id.return_value = True
        mock_topics_service.check_category.return_value = 10
        mock_categories_service.check_if_locked.return_value = False
        mock_categories_service.check_if_private.return_value = True
        mock_users_service.authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
        mock_categories_service.check_user_access.return_value = None

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, Unauthorized)
        #self.assertEqual(result.content, "Category is private.")

    def test_createReply_returnsUnauthorized_whenUserHasReadOnlyAccessToCategory(self):
        reply_text = ReplyText(text="mock text", topic_id=1)

        # Mock the topic and category checks, and set access to read-only
        mock_topics_service.get_by_id.return_value = True
        mock_topics_service.check_category.return_value = 10
        mock_categories_service.check_if_locked.return_value = False
        mock_categories_service.check_if_private.return_value = True
        mock_users_service.authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
        mock_categories_service.check_user_access.return_value = 0

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, Unauthorized)
        #self.assertEqual(result.content, "You have only read access.")

    def test_createReply_returnsUnauthorized_whenTopicIsLocked(self):
        reply_text = ReplyText(text="mock text", topic_id=1)

        # Simulate topic exists but is locked
        mock_topics_service.get_by_id.return_value = True
        mock_topics_service.check_category.return_value = 10
        mock_categories_service.check_if_locked.return_value = False
        mock_users_service.authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
        mock_topics_service.check_if_locked.return_value = True

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, Unauthorized)
        #self.assertEqual(result.content, "This topic is locked.")

    def test_createReply_returnsBadRequest_whenReplyTextIsEmpty(self):
        reply_text = ReplyText(text="", topic_id=1)

        # Mock topic existence check
        mock_topics_service.get_by_id.return_value = True
        mock_topics_service.check_category.return_value = 10
        mock_categories_service.check_if_locked.return_value = False
        mock_users_service.authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
        mock_topics_service.check_if_locked.return_value = False

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, BadRequest)
        #self.assertEqual(result.content, "Reply text cannot be empty.")

    def test_createReply_returnsBadRequest_whenReplyTextIsOver200Characters(self):
        reply_text = ReplyText(text="x" * 201, topic_id=1)

        # Mock topic existence check
        mock_topics_service.get_by_id.return_value = True
        mock_topics_service.check_category.return_value = 10
        mock_categories_service.check_if_locked.return_value = False
        mock_users_service.authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
        mock_topics_service.check_if_locked.return_value = False

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, BadRequest)
        #self.assertEqual(result.content, "Reply text cannot be more than 200 characters.")

    def test_createReply_returnsReplyResponse_onSuccessfulCreation(self):
        reply_text = ReplyText(text="mock text", topic_id=1)

        # Simulate topic and category being accessible
        mock_topics_service.get_by_id.return_value = True
        mock_topics_service.check_category.return_value = 10
        mock_categories_service.check_if_locked.return_value = False
        mock_topics_service.check_if_locked.return_value = False
        mock_users_service.authenticate_user.return_value = {'user_id': 1, 'is_admin': False}
        mock_categories_service.check_if_private.return_value = False

        # Simulate reply creation returning a response
        mock_replies_service.create.return_value = ReplyResponse(
            id=1,
            user_id=1,
            reply_date='2024-11-11 14:11:49',
            reply_text='mock text'
        )

        result = reply_router.create_reply(reply_text, token='mock-token')

        self.assertIsInstance(result, ReplyResponse)
        self.assertEqual(result.reply_text, "mock text")
