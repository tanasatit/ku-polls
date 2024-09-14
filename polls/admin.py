"""
Admin module for managing Polls application
models in the Django admin interface.

Registers the following models:
- Question
- Choice
"""

from django.contrib import admin
from .models import Question, Choice

admin.site.register(Question)
admin.site.register(Choice)
