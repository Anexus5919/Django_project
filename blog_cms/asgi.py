"""
=============================================================================
ASGI Configuration for Blog CMS
=============================================================================

ASGI = Asynchronous Server Gateway Interface

ASGI is the successor to WSGI, supporting:
    - Traditional HTTP requests (like WSGI)
    - WebSockets (real-time communication)
    - Long-polling
    - Server-sent events

When to use ASGI:
    - Real-time features (chat, notifications)
    - Long-running connections
    - Async views

Production:
    Run with Daphne: daphne blog_cms.asgi:application
    Or with Uvicorn: uvicorn blog_cms.asgi:application

For this blog project, WSGI is sufficient. ASGI is included for future use.

=============================================================================
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog_cms.settings')

application = get_asgi_application()
