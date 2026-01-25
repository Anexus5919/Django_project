"""
=============================================================================
Accounts URL Configuration
=============================================================================

This file maps URLs for user profile functionality.

Note: Authentication URLs (login, register, logout, password reset)
are handled by django-allauth at /accounts/

These URLs are for profile-related features:
    - View profile
    - Edit profile
    - View other users' profiles

=============================================================================
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ----- View Own Profile -----
    # URL: /profile/
    # Shows the logged-in user's profile
    path(
        '',
        views.ProfileView.as_view(),
        name='profile'
    ),

    # ----- Edit Profile -----
    # URL: /profile/edit/
    path(
        'edit/',
        views.ProfileUpdateView.as_view(),
        name='profile_edit'
    ),

    # ----- View Any User's Profile -----
    # URL: /profile/username/
    path(
        '<str:username>/',
        views.ProfileDetailView.as_view(),
        name='profile_detail'
    ),
]
