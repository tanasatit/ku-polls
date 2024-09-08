from django.test import TestCase
from django.contrib.auth.models import User
from polls.models import Question, Choice, Vote


class VoteTestCase(TestCase):
    """
    Test cases for the voting functionality in the polls app.
    """

    def setUp(self):
        """
        Create a test user, a question, and a choice for testing voting functionality.
        """
        self.user = User.objects.create(username='testuser')
        self.question = Question.objects.create(question_text='Test question')
        self.choice = Choice.objects.create(question=self.question, choice_text='Test choice')

    def test_user_can_vote(self):
        """
        Test if a user can successfully vote for a choice.
        """
        Vote.objects.create(user=self.user, choice=self.choice)

        # Fetch the choice again to ensure the vote count is updated
        choice = Choice.objects.get(pk=self.choice.pk)
        self.assertEqual(choice.votes, 1)
