import unittest
from unittest.mock import Mock
from common.responses import NotFound, BadRequest
from routers import messages as messages_router
from data.models import MessageText, MessageOutput, UserResponseChats

mock_messages_service = Mock(spec='messages_service')
mock_users_service = Mock(spec='users_service')

messages_router.messages_service = mock_messages_service
messages_router.users_service = mock_users_service

class MessagesRouterShould(unittest.TestCase):

    def setUp(self):
        mock_messages_service.reset_mock()
        mock_users_service.reset_mock()

    def test_createMessage_returnsNotFound_whenNoReceiver(self):

        msg = MessageText(text="mock-text", receiver_id=1)
        mock_users_service.get_user_by_id = lambda receiver_id: False

        result = messages_router.create_message(msg ,token='mock-token')

        self.assertIsInstance(result, NotFound)


    def test_createMessage_returnsBadRequest_whenMessageTextIsEmpty(self):

        msg = MessageText(text="", receiver_id=1)
        mock_users_service.get_user_by_id = lambda receiver_id: True
        result = messages_router.create_message(msg ,token='mock-token')

        self.assertIsInstance(result, BadRequest)

    def test_createMessage_returnsBadRequest_whenMessageTextIsOver500Characters(self):

        msg = MessageText(text="x" * 501, receiver_id=1)        
        mock_users_service.get_user_by_id = lambda receiver_id: True
        result = messages_router.create_message(msg ,token='mock-token')

        self.assertIsInstance(result, BadRequest)

    def test_createMessage_returnsCorrectRestult(self): 

        msg = MessageText(text="mock-text", receiver_id=1)
        mock_messages_service.create = lambda msg, token: "mock-text"
        mock_users_service.get_user_by_id = lambda receiver_id: True

        result = messages_router.create_message(msg ,token='mock-token')
        
        expected_result = "mock-text" # Няма ЛОГИКААААА



        self.assertEqual(result, expected_result)


    def test_viewConversation_returnsNotFound_whenNoReceiver(self):

        receiver_id = 1
        mock_users_service.get_user_by_id = lambda receiver_id: False

        result = messages_router.view_conversation(receiver_id,token='mock-token')

        self.assertIsInstance(result, NotFound)

    def test_viewConversation_returnsNotFound_whenNoResult(self):

        receiver_id = 1
        mock_users_service.get_user_by_id = lambda receiver_id: True
        mock_messages_service.all_messages = lambda receiver_id, token: False

        result = messages_router.view_conversation(receiver_id,token='mock-token')

        self.assertIsInstance(result, NotFound)

    def test_viewConversation_returnsCorrectResult(self):

        receiver_id = 1

        #mock_users_service.get_user_by_id = lambda receiver_id: {"id": receiver_id, "username": "receiver_user"}
        mock_users_service.get_user_by_id = lambda receiver_id: True

        mock_messages_service.all_messages = lambda receiver_id, token: [
            MessageOutput(sender_id=2, message_date="2024-11-11 14:00:00", message_text="Hello!"),
            MessageOutput(sender_id=receiver_id, message_date="2024-11-11 15:00:00", message_text="Hi there!")
        ]

        result = messages_router.view_conversation(receiver_id, token='mock-token')

        expected_result = [
            MessageOutput(sender_id=2, message_date="2024-11-11 14:00:00", message_text="Hello!"),
            MessageOutput(sender_id=receiver_id, message_date="2024-11-11 15:00:00", message_text="Hi there!")
        ]

        self.assertEqual(result, expected_result)

    def test_viewConversations_returnsNotFound_whenNoData(self):

        mock_messages_service.all_conversations = lambda token: False
        result = messages_router.view_conversations(token='mock-token')

        self.assertIsInstance(result, NotFound)

    def test_viewConversations_returnsCorrectResult(self):
        # Arrange
        #mock_user_id = 1
        token = 'mock-token'

        # Mocking authenticate_user to simulate a valid token
        #mock_authenticate_user.return_value = {'user_id': mock_user_id}

        # Mock messages_service.all_conversations to return a list of UserResponse objects
        mock_messages_service.all_conversations = lambda token: [
            UserResponseChats(id=2, username="user2"),
            UserResponseChats(id=3, username="user3")
        ]

        # Act
        result = messages_router.view_conversations(token)

        # Assert
        expected_result = [
            UserResponseChats(id=2, username="user2"),
            UserResponseChats(id=3, username="user3")
        ]
        self.assertEqual(result, expected_result)

