from unittest import TestCase
from unittest.mock import patch
from data.models import VoteResult
from services import votes_service as service

class VotesService_Should(TestCase):

    def test_vote_insertsNewVote_whenNoExistingVote(self):
        with patch('services.votes_service.authenticate_user') as mock_auth_user, \
             patch('services.votes_service.read_query') as mock_read_query, \
             patch('services.votes_service.insert_query') as mock_insert_query:

            reply_id = 1
            token = 'mock-token'
            vote = VoteResult(vote='upvote')
            mock_auth_user.return_value = {'user_id': 1}
            mock_read_query.return_value = []
            mock_insert_query.return_value = 1

            result = service.vote(reply_id, vote, token)

            self.assertEqual(result, "You voted with upvote")


    def test_vote_updatesVote_whenExistingVoteDiffers(self):
        with patch('services.votes_service.authenticate_user') as mock_auth_user, \
             patch('services.votes_service.read_query') as mock_read_query, \
             patch('services.votes_service.update_query') as mock_update_query:

            reply_id = 1
            token = 'mock-token'
            vote = VoteResult(vote='upvote')
            mock_auth_user.return_value = {'user_id': 1}
            mock_read_query.return_value = [(1, 1, 0)]
            mock_update_query.return_value = 1

            result = service.vote(reply_id, vote, token)

            self.assertEqual(result, "Vote changed to upvote")


    def test_vote_returnsMessage_whenVoteAlreadyExists(self):
        with patch('services.votes_service.authenticate_user') as mock_auth_user, \
             patch('services.votes_service.read_query') as mock_read_query:

            reply_id = 1
            token = 'mock-token'
            vote = VoteResult(vote='upvote')
            mock_auth_user.return_value = {'user_id': 1}
            mock_read_query.return_value = [(1, 2, 1)]

            result = service.vote(reply_id, vote, token)
            self.assertEqual(result, "The vote is already upvote")
