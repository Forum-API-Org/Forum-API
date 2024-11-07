import unittest
from unittest.mock import patch
from data.models import Message, MessageText, UserResponseChats, MessageOutput
from services import messages_service as service


class MessagesService_Should(unittest.TestCase):

    def test_create_returnsError_whenReceiverDoesNotExist(self):
        with patch('services.messages_service.authenticate_user') as mock_auth_user, \
             patch('services.messages_service.read_query') as mock_read_query:

            token = 'mock-token'
            
            message_text = MessageText(text="Hello", receiver_id = 99)
            mock_auth_user.return_value = {'user_id': 1}
            mock_read_query.return_value = []

            result = service.create(message_text, token)

            self.assertEqual(result, {"error": "Receiver does not exist"})

    def test_create_insertsMessage_whenReceiverExists(self):
        with patch('services.messages_service.authenticate_user') as mock_auth_user, \
             patch('services.messages_service.read_query') as mock_read_query, \
             patch('services.messages_service.insert_query') as mock_insert_query:

            token = 'mock-token'
            
            message_text = MessageText(text="Hello", receiver_id = 2)
            mock_auth_user.return_value = {'user_id': 1}
            mock_read_query.return_value = [(2,)]
            mock_insert_query.return_value = 1

            result = service.create(message_text, token)

            self.assertEqual(result, message_text)


    def test_all_messages_returnsMessages_withReceiver(self):
        with patch('services.messages_service.authenticate_user') as mock_auth_user, \
            patch('services.messages_service.read_query') as mock_read_query:

            token = 'mock-token'
            receiver_id = 2
            mock_auth_user.return_value = {'user_id': 1}

            # Mock data adjusted to match expected output structure
            mock_read_query.return_value = [
                (2, "2024-11-11 14:00:00", "Hello!"),
                (receiver_id, "2024-11-11 15:00:00", "Hi there!")
            ]

            expected = [
                MessageOutput(sender_id=2, message_date="2024-11-11 14:00:00", message_text="Hello!"),
                MessageOutput(sender_id=receiver_id, message_date="2024-11-11 15:00:00", message_text="Hi there!")
            ]

            result = service.all_messages(receiver_id, token)

            self.assertEqual(result, expected)

    def test_all_conversations_returnsDistinctConversations(self):
        with patch('services.messages_service.authenticate_user') as mock_auth_user, \
             patch('services.messages_service.read_query') as mock_read_query:

            token = 'mock-token'
            mock_auth_user.return_value = {'user_id': 1}
            mock_read_query.return_value = [
                (2, "user2"),
                (3, "user3")
            ]
            
            expected = [
                UserResponseChats(id=2, username="user2"),
                UserResponseChats(id=3, username="user3")
            ]

            result = service.all_conversations(token)

            self.assertEqual(result, expected)

