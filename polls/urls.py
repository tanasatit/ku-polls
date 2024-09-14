"""
URL configuration for the Polls app.

This module defines URL patterns for the Polls app, including paths for
index, detail, results, voting, and logout views.
"""

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'polls'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
