"""
Models for the Polls app.

Defines the Question, Choice, and Vote models.
"""

import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Question(models.Model):
    """
    A poll question.

    Attributes:
        question_text (str): The text of the question.
        pub_date (datetime): The date the question was published.
        end_date (datetime): The date the question ends.
    """

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('date end', null=True, blank=True)

    def was_published_recently(self):
        """
        Check if the question was published within the last day.

        Returns:
            bool: True if published within the last day, False otherwise.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Return True if the current date-time is on or after the publication date.

        Returns:
            bool: True if the question is published, False otherwise.
        """
        now = timezone.localtime()
        return now >= self.pub_date

    def can_vote(self):
        """
        Return True if voting is allowed for this question.

        Returns:
            bool: True if voting is allowed, False otherwise.
        """
        now = timezone.localtime()
        if self.end_date:
            return self.pub_date <= now <= self.end_date
        return now >= self.pub_date

    def __str__(self):
        """Return the string representation of the question."""
        return self.question_text


class Choice(models.Model):
    """
    A choice for a poll question.

    Attributes:
        question (Question): The question this choice is related to.
        choice_text (str): The text of the choice.
    """

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    # votes = models.IntegerField(default=0)

    @property
    def votes(self):
        """
        Return the number of votes for this choice.

        Returns:
            int: The number of votes.
        """
        return Vote.objects.filter(choice=self).count()

    def __str__(self):
        """Return the string representation of the choice."""
        return self.choice_text


class Vote(models.Model):
    """
    Record a choice for a question made by a user.

    Attributes:
        user (User): The user who made the vote.
        choice (Choice): The choice that was voted for.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        """Return the string representation of the vote."""
        return f"{self.user} voted for {self.choice}"
