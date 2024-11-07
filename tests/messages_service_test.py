import unittest
from unittest.mock import patch
from data.models import Message, MessageText, UserResponse
from services import messages_service as service


class MessagesService_Should(unittest.TestCase):

    def test_create_returnsError_whenReceiverDoesNotExist(self):
        with patch('services.messages_service.authenticate_user') as mock_auth_user, \
             patch('services.messages_service.read_query') as mock_read_query:

            token = 'mock-token'
            receiver_id = 99
            message_text = MessageText(text="Hello")
            mock_auth_user.return_value = {'user_id': 1}
            mock_read_query.return_value = []

            result = service.create(receiver_id, message_text, token)

            self.assertEqual(result, {"error": "Receiver does not exist"})

    def test_create_insertsMessage_whenReceiverExists(self):
        with patch('services.messages_service.authenticate_user') as mock_auth_user, \
             patch('services.messages_service.read_query') as mock_read_query, \
             patch('services.messages_service.insert_query') as mock_insert_query:

            token = 'mock-token'
            receiver_id = 2
            message_text = MessageText(text="Hello")
            mock_auth_user.return_value = {'user_id': 1}
            mock_read_query.return_value = [(receiver_id,)]
            mock_insert_query.return_value = 1

            result = service.create(receiver_id, message_text, token)

            self.assertEqual(result, message_text.text)


    def test_all_messages_returnsMessages_withReceiver(self):
        with patch('services.messages_service.authenticate_user') as mock_auth_user, \
            patch('services.messages_service.read_query') as mock_read_query:

            token = 'mock-token'
            receiver_id = 2
            mock_auth_user.return_value = {'user_id': 1}

            mock_read_query.return_value = [
                (1, 1, receiver_id, "2024-11-01 10:00:00", "Hello"),
                (2, receiver_id, 1, "2024-11-02 12:00:00", "Hi there")
            ]

            expected = [
                Message(id=1, sender_id=1, receiver_id=receiver_id, message_date="2024-11-01 10:00:00", message_text="Hello"),
                Message(id=2, sender_id=receiver_id, receiver_id=1, message_date="2024-11-02 12:00:00", message_text="Hi there")
            ]

            result = service.all_messages(receiver_id, token)

            self.assertEqual(result, expected)

    def test_all_conversations_returnsDistinctConversations(self):
        with patch('services.messages_service.authenticate_user') as mock_auth_user, \
             patch('services.messages_service.read_query') as mock_read_query:

            token = 'mock-token'
            mock_auth_user.return_value = {'user_id': 1}
            mock_read_query.return_value = [
                (2, "user2@example.com", "user2", "User", "Two", False),
                (3, "user3@example.com", "user3", "User", "Three", False)
            ]
            
            expected = [
                UserResponse(id=2, email="user2@example.com", username="user2", first_name="User", last_name="Two", is_admin=False),
                UserResponse(id=3, email="user3@example.com", username="user3", first_name="User", last_name="Three", is_admin=False)
            ]

            result = service.all_conversations(token)

            self.assertEqual(result, expected)

