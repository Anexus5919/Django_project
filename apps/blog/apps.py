"""
=============================================================================
Blog App Configuration
=============================================================================

This file configures the blog app for Django.
Django uses this to identify and configure the app.

AppConfig class attributes:
    - default_auto_field: Default primary key type for models
    - name: Full Python path to the app (must match INSTALLED_APPS)
    - verbose_name: Human-readable name (shown in admin)

=============================================================================
"""

from django.apps import AppConfig


class BlogConfig(AppConfig):
    """Configuration for the blog application."""

    # Use 64-bit integer for auto-generated primary keys
    default_auto_field = 'django.db.models.BigAutoField'

    # Python path to the app (must match INSTALLED_APPS entry)
    name = 'apps.blog'

    # Human-readable name displayed in admin
    verbose_name = 'Blog'

    def ready(self):
        """
        Called when Django starts.
        Use this to register signals or perform app initialization.
        """
        # Import signals to register them
        # We'll create signals later for things like auto-generating slugs
        pass
