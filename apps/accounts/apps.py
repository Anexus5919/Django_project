"""
=============================================================================
Accounts App Configuration
=============================================================================

This file configures the accounts app for Django.
The accounts app handles user profiles and related functionality.

=============================================================================
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for the accounts application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'User Accounts'

    def ready(self):
        """
        Called when Django starts.
        Import signals to auto-create user profiles.
        """
        # Import signals to register them
        import apps.accounts.signals  # noqa
