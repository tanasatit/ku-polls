from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from .models import Choice, Question


class IndexView(generic.ListView):
    """
    Display a list of the last five published questions, excluding those
    scheduled to be published in the future.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(
            pub_date__lte=timezone.localtime()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """Display details of a specific question, excluding unpublished questions."""
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


def vote(request, question_id):
    """
    Handle voting for a specific question. Increments the vote count for the
    selected choice and redirects to the results page.

    If voting is not allowed or if no choice is selected, redisplay the question
    detail page with an error message.
    """
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "Voting is not allowed for this question.",
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def index(request):
    """Display a list of the latest five published questions."""
    latest_question_list = Question.objects.filter(
        pub_date__lte=timezone.localtime()
    ).order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    """
    Display details of a specific question. Redirect to the index page with an
    error message if voting is not allowed.
    """
    question = get_object_or_404(Question, pk=question_id)
    if not question.can_vote():
        messages.error(request, "Voting is not allowed for this poll.")
        return redirect('polls:index')
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    """Display the results of a specific question."""
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})
