"""
=============================================================================
URL Configuration for Blog CMS
=============================================================================

This file is the "table of contents" for your website.
It maps URLs to views (the code that handles requests).

How URL routing works in Django:
    1. User requests a URL (e.g., /blog/my-post/)
    2. Django checks urlpatterns from top to bottom
    3. First matching pattern wins
    4. Django calls the associated view function/class
    5. View returns a response (usually HTML)

URL Pattern Syntax:
    path('url/', view, name='name')
    - 'url/' - The URL pattern to match
    - view   - The view function or class to call
    - name   - A unique name for reverse URL lookup

Example:
    path('blog/', include('apps.blog.urls'))
    This means all URLs starting with /blog/ will be handled by apps.blog.urls

=============================================================================
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Main URL patterns
urlpatterns = [
    # ----- Admin Panel Disabled -----
    # All content is managed through the frontend dashboard
    path('admin/', lambda request: redirect('/')),

    # ----- Blog URLs -----
    # All blog-related URLs (posts, categories, tags, search)
    # Access at: http://localhost:8000/ (home), /blog/, /category/, /tag/
    path('', include('apps.blog.urls')),

    # ----- Authentication URLs -----
    # django-allauth handles login, logout, register, password reset
    # Access at: http://localhost:8000/accounts/login/, /accounts/signup/, etc.
    path('accounts/', include('allauth.urls')),

    # ----- User Profile URLs -----
    # Custom profile views (view profile, edit profile)
    # Access at: http://localhost:8000/profile/
    path('profile/', include('apps.accounts.urls')),

    # ----- CKEditor URLs -----
    # Handles image uploads for the rich text editor
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# Serve media files during development
# In production, use a web server like Nginx to serve these
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
