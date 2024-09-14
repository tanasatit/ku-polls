from django.test import TestCase
from polls.models import Question
from django.utils import timezone
import datetime


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and publish the question
    with a pub_date offset by the given number of `days` from now.
    Negative values indicate a past date and positive values a future date.
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    """
    Test cases for the Question model, focusing on publication dates.
    """

    def test_future_pub_date(self):
        """
        A question with a pub_date in the future should not be published.
        """
        future_question = create_question(question_text='Future Question',
                                          days=5)
        self.assertFalse(future_question.is_published())

    def test_default_pub_date(self):
        """
        A question with a pub_date equal to
        the current date should be published.
        """
        current_question = create_question(question_text='Current Question',
                                           days=0)
        self.assertTrue(current_question.is_published())

    def test_past_pub_date(self):
        """
        A question with a pub_date in the past should be published.
        """
        past_question = create_question(question_text='Past Question', days=-5)
        self.assertTrue(past_question.is_published())


class QuestionVoteTests(TestCase):
    """
    Test cases for the voting functionality based on the voting period.
    """

    def test_can_vote_when_within_period(self):
        """
        Voting should be allowed if
        the question's end_date is in the future.
        """
        question = create_question(question_text='Vote Allowed Question',
                                   days=0)
        question.end_date = timezone.now() + datetime.timedelta(days=1)
        question.save()
        self.assertTrue(question.can_vote())

    def test_cannot_vote_after_end_date(self):
        """
        Voting should not be allowed if
        the question's end_date is in the past.
        """
        question = create_question(question_text='Vote Not Allowed Question',
                                   days=-5)
        question.end_date = timezone.now() - datetime.timedelta(days=1)
        question.save()
        self.assertFalse(question.can_vote())

    def test_cannot_vote_before_pub_date(self):
        """
        Voting should not be allowed if
        the question's pub_date is in the future.
        """
        question = create_question(
            question_text='Vote Not Allowed Yet Question',
            days=5)
        self.assertFalse(question.can_vote())
