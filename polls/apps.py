"""
Configuration for the Polls application.

Defines the settings and configuration for the Polls app.
"""

from django.apps import AppConfig


class PollsConfig(AppConfig):
    """
    Configuration for the Polls app.

    Sets the default auto field type and specifies the app name.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
