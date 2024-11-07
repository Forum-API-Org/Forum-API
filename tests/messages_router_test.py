import unittest
from unittest.mock import Mock
from common.responses import NotFound, BadRequest
from routers import messages as messages_router
from data.models import MessageText, Message, UserResponse

mock_messages_service = Mock(spec='messages_service')
mock_users_service = Mock(spec='users_service')

messages_router.messages_service = mock_messages_service
messages_router.users_service = mock_users_service

class MessagesRouterShould(unittest.TestCase):

    def setUp(self):
        mock_messages_service.reset_mock()

    def test_createMessage_returnsNotFound_whenNoReceiver(self):

        receiver_id = 1
        msg = MessageText(text="mock-text")
        mock_users_service.get_user_by_id = lambda receiver_id: False

        result = messages_router.create_message(receiver_id, msg ,token='mock-token')

        self.assertIsInstance(result, NotFound)


    def test_createMessage_returnsBadRequest_whenMessageTextIsEmpty(self):

        receiver_id = 1
        msg = MessageText(text="")
        mock_users_service.get_user_by_id = lambda receiver_id: True
        result = messages_router.create_message(receiver_id, msg ,token='mock-token')

        self.assertIsInstance(result, BadRequest)

    def test_createMessage_returnsBadRequest_whenMessageTextIsOver500Characters(self):

        receiver_id = 1
        msg = MessageText(text="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        mock_users_service.get_user_by_id = lambda receiver_id: True
        result = messages_router.create_message(receiver_id, msg ,token='mock-token')

        self.assertIsInstance(result, BadRequest)

    def test_createMessage_returnsCorrectRestult(self):

        receiver_id = 1
        msg = MessageText(text="mock-text")
        mock_messages_service.create = lambda receiver_id, msg, token: "mock-text"
        mock_users_service.get_user_by_id = lambda receiver_id: True
        result = messages_router.create_message(receiver_id, msg ,token='mock-token')
        
        expected_result = {"message": "Message sent successfully.", "content": msg.text}



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
            Message(id=1, sender_id=2, receiver_id=receiver_id, message_date="2024-11-11 14:00:00", message_text="Hello!"),
            Message(id=2, sender_id=receiver_id, receiver_id=2, message_date="2024-11-11 14:00:00", message_text="Hi there!")
        ]

        result = messages_router.view_conversation(receiver_id, token='mock-token')

        expected_result = {
            "conversation": [(2, "Hello!"), (receiver_id, "Hi there!")],
            "message_count": 2
        }

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
            UserResponse(id=2, email="user2@example.com", username="user2", first_name="User", last_name="Two", is_admin=False),
            UserResponse(id=3, email="user3@example.com", username="user3", first_name="User", last_name="Three", is_admin=False)
        ]

        # Act
        result = messages_router.view_conversations(token)

        # Assert
        expected_result = [
            UserResponse(id=2, email="user2@example.com", username="user2", first_name="User", last_name="Two", is_admin=False),
            UserResponse(id=3, email="user3@example.com", username="user3", first_name="User", last_name="Three", is_admin=False)
        ]
        self.assertEqual(result, expected_result)

