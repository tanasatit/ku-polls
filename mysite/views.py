"""
Views for user authentication.

This module contains views for user authentication, including registration and login.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm


def signup(request):
    """
    Register a new user.

    If the request method is POST, validate and save the form data, then authenticate and log in the user.
    Redirect to the polls index page upon successful registration.
    If the form is not valid, display errors on the signup page.
    If the request method is GET, render the signup form.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data
            username = form.cleaned_data.get('username')
            # password input field is named 'password1'
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
            return redirect('polls:index')
        # if the form is not valid, we should display a message in signup.html
    else:
        # create a user form and display it on the signup page
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
