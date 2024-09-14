from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from .models import Choice, Question, Vote
from django.contrib.auth.decorators import login_required
import logging
from django.contrib.auth.signals import (
    user_logged_in, user_logged_out, user_login_failed)
from django.dispatch import receiver


class IndexView(generic.ListView):
    """
    Display a list of all published polls, sorted by date, from newest to oldest.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return all published questions, ordered by date from newest to oldest."""
        return Question.objects.filter(
            pub_date__lte=timezone.localtime()
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        """Add extra context to check if voting is allowed."""
        context = super().get_context_data(**kwargs)
        latest_questions = context['latest_question_list']

        # Add voting allowed status for each question
        for question in latest_questions:
            question.voting_allowed = question.can_vote()

        return context


class DetailView(generic.DetailView):
    """
    Display details of a specific question,
    excluding unpublished questions.
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """Exclude questions that aren't published yet."""
        return Question.objects.filter(
            pub_date__lte=timezone.localtime()
        )


class ResultsView(generic.DetailView):
    """Display the results for a specific question."""
    model = Question
    template_name = 'polls/results.html'


@login_required(login_url='login')
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        return redirect('polls:index')

    # Get the selected choice
    choice_id = request.POST.get('choice')
    if not choice_id:
        # Pass an error message as context
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

    Vote.objects.update_or_create(
        user=request.user,
        choice__question=question,
        defaults={'choice': selected_choice}
    )

    return redirect('polls:results', pk=question.id)


def index(request):
    """Display a list of the latest five published questions."""
    latest_question_list = Question.objects.filter(
        pub_date__lte=timezone.localtime()
    ).order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    """
    Display details of a specific question. Redirect to the index page
    with an error message if voting is not allowed. Also, if the user
    has previously voted,pass the selected choice to the template.
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
            user=request.user, choice__question=question).first()

    return render(request, 'polls/detail.html', {
        'question': question,
        'previous_vote': previous_vote,
    })


def results(request, question_id):
    """Display the results of a specific question."""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


logger = logging.getLogger("polls")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip_addr = get_client_ip(request)
    logger.info(f"{user.username} logged in from {ip_addr}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    ip_addr = get_client_ip(request)
    logger.info(f"{user.username} logged out from {ip_addr}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip_addr = get_client_ip(request)
    (logger.warning
     (f"Failed login for {credentials.get('username')} from {ip_addr}"))


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
