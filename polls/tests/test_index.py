from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from polls.models import Question
import datetime


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and publish the question
    with a pub_date offset by the given number of `days` from now.
    Negative values indicate a past date and positive values a future date.
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    """
    Test cases for the index view of the polls app.
    """

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        The detail view of a question with a pub_date
        in the past should display the question.
        """
        past_question = create_question(question_text='Past Question.',
                                        days=-5)
        url = reverse('polls:detail',
                      args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_future_question(self):
        """
        The detail view of a question with a pub_date
        in the future should return a 404 error.
        """
        future_question = create_question(question_text='Future question.',
                                          days=5)
        url = reverse('polls:detail',
                      args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist,
        only past questions should be displayed.
        """
        question = create_question(question_text="Past question.",
                                   days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'],
                                 [question])

    def test_two_past_questions(self):
        """
        The index page should display multiple
        questions if they exist.
        """
        question1 = create_question(question_text="Past question 1.",
                                    days=-30)
        question2 = create_question(question_text="Past question 2.",
                                    days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerySetEqual(response.context['latest_question_list'], [
            question2, question1])
