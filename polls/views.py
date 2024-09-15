"""
Views for the Polls app.

This module contains views for listing polls,
displaying details and results,
handling votes, and logging user actions.
"""

from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from .models import Choice, Question, Vote
from django.contrib.auth.decorators import login_required
import logging
from django.contrib.auth.signals import (
    user_logged_in, user_logged_out, user_login_failed
)
from django.dispatch import receiver


class IndexView(generic.ListView):
    """Display a list of all published polls,sorted by date, from newest to oldest."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return all published questions, ordered by date from newest to oldest."""
        return Question.objects.filter(
            pub_date__lte=timezone.localtime()
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        """
        Add extra context to check if voting is allowed.

        This method adds a 'voting_allowed' status to each question in the context.
        """
        context = super().get_context_data(**kwargs)
        latest_questions = context['latest_question_list']

        # Add voting allowed status for each question
        for question in latest_questions:
            question.voting_allowed = question.can_vote()

        return context


class DetailView(generic.DetailView):
    """Display details of a specific question, excluding unpublished questions."""

    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Exclude questions that aren't published yet."""
        return Question.objects.filter(pub_date__lte=timezone.localtime())

    def get_context_data(self, **kwargs):
        """
        Add the previous vote of the authenticated user to the context.

        Retrieves the user's previous choice for the question, if available,
        and includes it in the context data. Logs debug information about the
        user's voting status.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            dict: Context data including 'previous_choice', which is the user's
                  last selected choice or None if no previous vote is found.
        """
        context = super().get_context_data(**kwargs)
        question = self.object
        this_user = self.request.user

        if this_user.is_authenticated:
            try:
                previous_vote = Vote.objects.get(user=this_user, choice__question=question)
                context['previous_choice'] = previous_vote.choice
                logger.debug(f"Previous choice for user {this_user.username}: {previous_vote.choice.choice_text}")
            except Vote.DoesNotExist:
                context['previous_choice'] = None
                logger.debug(f"No previous vote found for user {this_user.username}")
        else:
            context['previous_choice'] = None
            logger.debug("User is not authenticated.")

        return context


class ResultsView(generic.DetailView):
    """Display the results for a specific question."""

    model = Question
    template_name = 'polls/results.html'


@login_required(login_url='login')
def vote(request, question_id):
    """
    Handle voting for a specific choice in a question.

    Checks if the user is allowed to vote on the specified question.
    Updates the user's vote if they have already voted, otherwise creates a new vote.
    Redirects to the results page with a success message or the detail page with an error message.

    Args:
        request: The HTTP request object containing the vote details.
        question_id: The ID of the question being voted on.

    Returns:
        HttpResponseRedirect: Redirects to the results page or back to the detail page with an error message.
    """
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        return redirect('polls:index')

    choice_id = request.POST.get('choice')
    if not choice_id:
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    try:
        selected_choice = question.choice_set.get(pk=choice_id)
    except Choice.DoesNotExist:
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "Invalid choice selected.",
        })

    # Check if the user has already voted
    previous_vote = Vote.objects.filter(user=request.user, choice__question=question).first()
    if previous_vote:
        # If the user has voted before, update the vote
        previous_vote.choice = selected_choice
        previous_vote.save()
    else:
        # Create a new vote
        Vote.objects.create(user=request.user, choice=selected_choice)

    # Add the message
    messages.success(request, f"Your vote for {selected_choice.choice_text} has been recorded.")

    return redirect('polls:results', question.id)


def index(request):
    """Display a list of the latest five published questions."""
    latest_question_list = Question.objects.filter(
        pub_date__lte=timezone.localtime()
    ).order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


@login_required(login_url='login')
def detail(request, question_id):
    """
    Display the details of a specific question.

    Checks if voting is allowed for the question. If not, redirects to the index page with an error message.
    Also checks if the user has previously voted on this question and passes the choice to the template.

    Args:
        request: The HTTP request object.
        question_id: The ID of the question to be displayed.

    Returns:
        HttpResponse: Renders the detail page for the specified question.
    """
    question = get_object_or_404(Question, pk=question_id)

    # Check if voting is allowed
    if not question.can_vote():
        messages.error(request, "Voting is not allowed for this poll.")
        return redirect('polls:index')

    # Check if the user has already voted on this question
    previous_vote = None
    if request.user.is_authenticated:
        previous_vote = Vote.objects.filter(
            user=request.user, choice__question=question
        ).first()

    return render(request, 'polls/detail.html', {
        'question': question,
        'previous_choice': previous_vote.choice if previous_vote else None,
    })


def results(request, question_id):
    """
    Display the results of a specific question.

    Retrieves the vote confirmation from the session and renders the results page for the specified question.

    Args:
        request: The HTTP request object.
        question_id: The ID of the question whose results are to be displayed.

    Returns:
        HttpResponse: Renders the results page for the specified question.
    """
    question = get_object_or_404(Question, pk=question_id)

    # Retrieve the vote confirmation from the session
    voted_choice = request.session.get(f'voted_for_{question.id}', None)

    return render(request, 'polls/results.html', {
        'question': question,
        'voted_choice': voted_choice,  # Pass the voted choice to the template
    })


logger = logging.getLogger("polls")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log user login events.

    Record the login event with the user's username and IP address.
    """
    ip_addr = get_client_ip(request)
    logger.info(f"{user.username} logged in from {ip_addr}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout events.

    Record the logout event with the user's username and IP address.
    """
    ip_addr = get_client_ip(request)
    logger.info(f"{user.username} logged out from {ip_addr}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Log failed login attempts.

    Record failed login attempts with the username and IP address.
    """
    ip_addr = get_client_ip(request)
    logger.warning(f"Failed login for {credentials.get('username')} from {ip_addr}")


def get_client_ip(request):
    """
    Get the visitor’s IP address using request headers.

    Returns the IP address from the HTTP_X_FORWARDED_FOR header or REMOTE_ADDR.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
