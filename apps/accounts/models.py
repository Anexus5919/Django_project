"""
=============================================================================
Accounts Models - User Profile Extension
=============================================================================

Django's built-in User model includes:
    - username, email, password
    - first_name, last_name
    - is_active, is_staff, is_superuser
    - date_joined, last_login

We extend it with UserProfile for additional fields like:
    - Avatar image
    - Bio/about text
    - Website URL
    - Social media links

Two approaches to extend User:
    1. OneToOneField (we use this) - Separate table linked to User
    2. AbstractUser - Custom User model (more complex)

We use OneToOneField because:
    - It's simpler and works with existing User model
    - Easy to add fields without migrations on User table
    - Works seamlessly with django-allauth

=============================================================================
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    """
    User Profile Model - Extends Django's User with additional fields.

    OneToOneField means:
        - Each User has exactly ONE UserProfile
        - Each UserProfile belongs to exactly ONE User
        - Access: user.profile (thanks to related_name='profile')

    Database table: accounts_userprofile
    """

    # ----- Link to User -----

    # OneToOneField creates a 1:1 relationship
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # Delete profile if user is deleted
        related_name='profile',    # Access profile: user.profile
        primary_key=True,          # Use user_id as primary key
    )

    # ----- Profile Fields -----

    # User's profile picture
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="Profile picture (recommended: 200x200 pixels)"
    )

    # Short biography
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Tell us about yourself (max 500 characters)"
    )

    # User's location
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Your location (e.g., 'New York, USA')"
    )

    # Personal website
    website = models.URLField(
        blank=True,
        help_text="Your personal website URL"
    )

    # ----- Social Media Links -----

    twitter = models.CharField(
        max_length=50,
        blank=True,
        help_text="Twitter username (without @)"
    )

    github = models.CharField(
        max_length=50,
        blank=True,
        help_text="GitHub username"
    )

    linkedin = models.CharField(
        max_length=100,
        blank=True,
        help_text="LinkedIn profile URL or username"
    )

    # ----- Settings -----

    # Email notification preferences
    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive email notifications for comments on your posts"
    )

    # Profile visibility
    is_public = models.BooleanField(
        default=True,
        help_text="Make your profile visible to other users"
    )

    # ----- Timestamps -----

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.username}\'s Profile'

    def get_absolute_url(self):
        """Returns URL to view this profile."""
        return reverse('accounts:profile_detail', kwargs={'username': self.user.username})

    @property
    def full_name(self):
        """
        Returns user's full name or username.
        Property decorator allows accessing like an attribute: profile.full_name
        """
        if self.user.first_name and self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        return self.user.username

    @property
    def post_count(self):
        """Returns the number of published posts by this user."""
        return self.user.posts.filter(status='published').count()

    @property
    def comment_count(self):
        """Returns the number of comments by this user."""
        return self.user.comments.count()

    def get_avatar_url(self):
        """
        Returns the avatar URL or a default avatar.
        Useful in templates: {{ profile.get_avatar_url }}
        """
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        # Return a placeholder avatar URL
        return '/static/images/default-avatar.png'
