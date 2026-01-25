"""
=============================================================================
Core App Configuration
=============================================================================

This file configures the core app.
Core contains shared utilities used across other apps.

=============================================================================
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core Utilities'
