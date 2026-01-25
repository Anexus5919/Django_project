#!/usr/bin/env python
"""
=============================================================================
Django's Command-Line Utility for Administrative Tasks
=============================================================================

This file is the entry point for all Django management commands.
You'll use this file constantly during development:

Common commands:
    python manage.py runserver          # Start the development server
    python manage.py makemigrations     # Create database migration files
    python manage.py migrate            # Apply migrations to database
    python manage.py createsuperuser    # Create an admin user
    python manage.py shell              # Open Python shell with Django loaded
    python manage.py collectstatic      # Gather static files for production

How it works:
    1. Sets the DJANGO_SETTINGS_MODULE environment variable
    2. Imports Django's command-line utility
    3. Passes your command to Django for execution

=============================================================================
"""
import os
import sys


def main():
    """Run administrative tasks."""
    # Tell Django which settings file to use
    # 'blog_cms.settings' means: look in blog_cms folder for settings.py
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_cms.settings')

    try:
        # Import Django's command-line utility
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # This error occurs if Django isn't installed
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Execute the command (e.g., 'runserver', 'migrate', etc.)
    execute_from_command_line(sys.argv)


# This runs when you execute: python manage.py <command>
if __name__ == '__main__':
    main()
