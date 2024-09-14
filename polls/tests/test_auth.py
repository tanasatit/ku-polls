from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from polls.models import Question, Choice
from mysite import settings


class UserAuthTest(TestCase):
    """
    Test cases related to user authentication and voting access.
    """

    def setUp(self):
        """
        Create a test user and a poll question with choices
        for authentication and voting tests.
        """
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(username=self.username,
                                              password=self.password,
                                              email="testuser@nowhere.com")
        self.user1.first_name = "Tester"
        self.user1.save()

        # Create a poll question with choices
        q = Question.objects.create(question_text="First Poll Question")
        for n in range(1, 4):
            Choice.objects.create(choice_text=f"Choice {n}", question=q)
        self.question = q

    def test_logout(self):
        """Test if a user can log out successfully using the logout URL."""
        logout_url = reverse("logout")
        self.assertTrue(self.client.login(username=self.username,
                                          password=self.password))
        response = self.client.post(logout_url)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """
        Test if a user can log in successfully using the login view.
        """
        login_url = reverse("login")
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)

        form_data = {"username": "testuser", "password": "FatChance!"}
        response = self.client.post(login_url, form_data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """
        Test if authentication is required to submit a vote.
        Unauthenticated users should be redirected to the login page.
        """
        vote_url = reverse('polls:vote', args=[self.question.id])
        choice = self.question.choice_set.first()
        form_data = {"choice": f"{choice.id}"}

        # Attempt to vote without authentication
        response = self.client.post(vote_url, form_data)
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)
