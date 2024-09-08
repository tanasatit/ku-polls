import django
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from .models import Question
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from polls.models import Question, Choice, Vote
from mysite import settings


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionModelTests(TestCase):

    def test_future_pub_date(self):
        """
        Question with a pub_date in the future should not be published.
        """
        future_question = create_question(question_text='Future Question', days=5)
        self.assertFalse(future_question.is_published())

    def test_default_pub_date(self):
        """
        Question with the current date as pub_date should be published.
        """
        current_question = create_question(question_text='Current Question', days=0)
        self.assertTrue(current_question.is_published())

    def test_past_pub_date(self):
        """
        Question with a pub_date in the past should be published.
        """
        past_question = create_question(question_text='Past Question', days=-5)
        self.assertTrue(past_question.is_published())


class QuestionVoteTests(TestCase):

    def test_can_vote_when_within_period(self):
        """
        Voting should be allowed if the question's end_date is in the future.
        """
        question = create_question(question_text='Vote Allowed Question', days=0)
        question.end_date = timezone.now() + datetime.timedelta(days=1)
        question.save()
        self.assertTrue(question.can_vote())

    def test_cannot_vote_after_end_date(self):
        """
        Voting should not be allowed if the question's end_date is in the past.
        """
        question = create_question(question_text='Vote Not Allowed Question', days=-5)
        question.end_date = timezone.now() - datetime.timedelta(days=1)
        question.save()
        self.assertFalse(question.can_vote())

    def test_cannot_vote_before_start_date(self):
        """
        Voting should not be allowed if the question's start_date is in the future.
        """
        question = create_question(question_text='Vote Not Allowed Yet Question', days=5)
        question.start_date = timezone.now() + datetime.timedelta(days=1)
        question.save()
        self.assertFalse(question.can_vote())


