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


class UserAuthTest(django.test.TestCase):

    def setUp(self):
        # superclass setUp creates a Client object and initializes test database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def test_logout(self):
        """A user can logout using the logout URL.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        self.assertTrue(self.client.login(username=self.username, password=self.password))

        # Use POST to logout (as Django requires)
        response = self.client.post(logout_url)
        self.assertEqual(302, response.status_code)

        # Should redirect us to the LOGOUT_REDIRECT_URL
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": "testuser",
                     "password": "FatChance!"
                     }
        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page with a `next` parameter.
        """
        vote_url = reverse('polls:vote', args=[self.question.id])

        # Get the first choice for voting
        choice = self.question.choice_set.first()
        form_data = {"choice": f"{choice.id}"}

        # Try to submit the vote without being authenticated
        response = self.client.post(vote_url, form_data)

        # Expect to be redirected to the login page with the `next` parameter
        self.assertEqual(response.status_code, 302)  # Could also be 303 for a POST-redirect

        # Ensure the redirect includes the `?next=` query parameter pointing to the vote URL
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)


class VoteTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='testuser')
        question = Question.objects.create(question_text='Test question')
        choice = Choice.objects.create(question=question, choice_text='Test choice')

    def test_user_can_vote(self):
        user = User.objects.get(username='testuser')
        choice = Choice.objects.get(choice_text='Test choice')
        Vote.objects.create(user=user, choice=choice)

        self.assertEqual(choice.votes, 1)