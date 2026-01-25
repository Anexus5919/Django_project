"""
=============================================================================
WSGI Configuration for Blog CMS
=============================================================================

WSGI = Web Server Gateway Interface

This file is the entry point for WSGI-compatible web servers.
In production, servers like Gunicorn or uWSGI use this file.

How it works:
    1. Web server (Nginx) receives a request
    2. Passes it to Gunicorn (WSGI server)
    3. Gunicorn uses this file to load your Django app
    4. Django processes the request and returns a response

Development:
    You don't need to worry about this file for development.
    `python manage.py runserver` uses its own server.

Production:
    Run with Gunicorn: gunicorn blog_cms.wsgi:application

=============================================================================
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_cms.settings')

# Create the WSGI application
# This is what Gunicorn/uWSGI looks for
application = get_wsgi_application()
