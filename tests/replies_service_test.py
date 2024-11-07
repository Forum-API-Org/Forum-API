from unittest import TestCase
from unittest.mock import patch
from data.models import ReplyResponse, ReplyText
from services import replies_service as service

class RepliesService_Should(TestCase):

    def test_get_reply_by_id_returnsReply_whenExists(self):
        with patch('services.replies_service.authenticate_user') as mock_auth_user, \
             patch('services.replies_service.read_query') as mock_read_query:

            token = 'mock-token'
            reply_id = 1
            mock_auth_user.return_value = {'user_id': 2}
            mock_read_query.return_value = [
                (2, "2024-11-11 14:00:00", "Test reply")
            ]

            expected = ReplyResponse(
                user_id=2,
                reply_date="2024-11-11 14:00:00",
                reply_text="Test reply",
            )

            result = next(service.get_reply_by_id(reply_id, token), None)

            self.assertEqual(result, expected)

    def test_get_reply_by_id_returnsNone_whenNotExists(self):
        with patch('services.replies_service.authenticate_user') as mock_auth_user, \
             patch('services.replies_service.read_query') as mock_read_query:
             
            token = 'mock-token'
            reply_id = 1
            mock_auth_user.return_value = {'user_id': 2}
            mock_read_query.return_value = []

            result = next(service.get_reply_by_id(reply_id, token), None)

            self.assertIsNone(result)

    def test_create_returnsReply_whenSuccessful(self):
        with patch('services.replies_service.authenticate_user') as mock_auth_user, \
             patch('services.replies_service.insert_query') as mock_insert_query, \
             patch('services.replies_service.get_reply_by_id') as mock_get_reply_by_id:
             
            token = 'mock-token' 
            reply_text = ReplyText(text="Mock reply", topic_id = 1)
            generated_id = 10
            mock_auth_user.return_value = {'user_id': 2}
            mock_insert_query.return_value = generated_id
            mock_get_reply_by_id.return_value = ReplyResponse(
                user_id=2,
                reply_date="2024-11-11 14:00:00",
                reply_text="Mock reply",
            )

            result = service.create(reply_text, token)

            # self.assertEqual(result.id, generated_id)
            # self.assertEqual(result.topic_id, topic_id)
            self.assertEqual(result.reply_text, "Mock reply")

    def test_create_returnsNone_whenUserNotAuthenticated(self):
        with patch('services.replies_service.authenticate_user') as mock_auth_user:
            
            token = 'invalid-token'
            reply_text = ReplyText(text="Should not be created", topic_id = 1)
            mock_auth_user.return_value = False

            result = service.create(reply_text, token)

            self.assertFalse(result)

    def test_reply_exists_returnsTrue_whenReplyExists(self):
        with patch('services.replies_service.read_query') as mock_read_query:
            
            reply_id = 1
            mock_read_query.return_value = [(reply_id,)]

            result = service.reply_exists(reply_id)

            self.assertTrue(result)

    def test_reply_exists_returnsFalse_whenReplyDoesNotExist(self):
        with patch('services.replies_service.read_query') as mock_read_query:
            
            reply_id = 1
            mock_read_query.return_value = []

            result = service.reply_exists(reply_id)

            self.assertFalse(result)
