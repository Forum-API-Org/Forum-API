import unittest
from unittest.mock import Mock, patch
from common.responses import NotFound
from data.models import VoteResult
from routers import votes as votes_router

mock_votes_service = Mock(spec='services.votes_service')
mock_replies_service = Mock(spec='services.replies_service')
# mock_authenticate_user = Mock(spec='services.users_service.authenticate_user')
# mock_create_token = Mock(spec='services.users_service.create_token')

votes_router.votes_service = mock_votes_service
votes_router.replies_service = mock_replies_service

# mock_payload = {
#         'user_id': 1,
#         'username': 'testuser',
#         'is_admin': True,
#         'exp': '30.11.2024 15:00:00'
#     }
# mock_create_token.return_value = mock_payload


class VotesRouter_Should(unittest.TestCase):

    def setUp(self) -> None:
        mock_votes_service.reset_mock()
        mock_replies_service.reset_mock()
        #mock_authenticate_user.reset_mock()

    #@patch('routers.votes.Header', lambda: 'mocked-token')
    def test_putVote_returnsNotFound_whenReplyDoesNotExist(self):
        # with patch('routers.votes.Header', lambda: 'mocked-token') as token:
        reply_id = 1
        vote = VoteResult(vote="upvote")
        mock_replies_service.reply_exists = lambda reply_id: False
        #mock_authenticate_user = lambda x: mock_payload
        #mock_votes_service.vote.return_value = 
        # mock_authenticate_user.return_value = True
        # mock_create_token.return_value = mock_payload
        # token = mock_create_token.return_value

        result = votes_router.put_vote(reply_id, vote, token='mock-token')

        self.assertIsInstance(result, NotFound)


    def test_putVote_createsNewVote_whenUserHasNotVotedBefore(self):
        # with patch('routers.votes.Header', lambda: 'mocked-token') as token:
        reply_id = 1
        vote = VoteResult(vote="upvote")
        mock_replies_service.reply_exists = lambda reply_id: True
        mock_votes_service.vote = lambda x,y,z: "You voted with upvote"

        result = votes_router.put_vote(reply_id, vote, token='mock-token')

        self.assertEqual(result, "You voted with upvote")


    def test_putVote_updatesVote_whenUserChangesVote(self):
        reply_id = 1
        vote = VoteResult(vote="upvote")
        mock_replies_service.reply_exists = lambda reply_id: True
        mock_votes_service.vote = lambda reply_id, vote , token: "Vote changed to upvote"

        result = votes_router.put_vote(reply_id, vote, token='mock-token')

        self.assertEqual(result, "Vote changed to upvote")


    def test_putVote_returnsAlreadyVotedMessage_whenVoteIsTheSame(self):
        reply_id = 1
        vote = VoteResult(vote="upvote")
        mock_replies_service.reply_exists = lambda reply_id: True
        mock_votes_service.vote = lambda reply_id, vote , token: "The vote is already upvote"

        result = votes_router.put_vote(reply_id, vote, token='mock-token')

        self.assertEqual(result, "The vote is already upvote")
