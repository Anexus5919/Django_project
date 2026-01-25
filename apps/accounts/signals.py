"""
=============================================================================
Accounts Signals - Automatic Profile Creation
=============================================================================

Signals in Django:
    Signals allow certain senders to notify receivers when actions occur.
    They're like event listeners in JavaScript.

Common signals:
    - pre_save: Before a model is saved
    - post_save: After a model is saved
    - pre_delete: Before a model is deleted
    - post_delete: After a model is deleted

How this works:
    1. User registers (User instance is created)
    2. Django sends post_save signal
    3. Our receiver function catches it
    4. We create a UserProfile for that user

Why use signals?
    - Automatic profile creation without modifying registration code
    - Works with any method of user creation (admin, API, shell)
    - Keeps code decoupled and modular

=============================================================================
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a UserProfile when a User is created.

    Arguments:
        sender: The model class (User)
        instance: The actual User instance that was saved
        created: Boolean - True if a new User was created
        **kwargs: Additional keyword arguments

    This runs AFTER a User is saved to the database.
    """
    if created:
        # Only create profile for new users
        UserProfile.objects.create(user=instance)
        print(f"Created profile for user: {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal receiver that saves the UserProfile when User is saved.

    This ensures the profile is saved when the user is updated.
    Handles the case where profile already exists.
    """
    # Use get_or_create to handle existing profiles
    # This also handles the edge case where a user exists without a profile
    profile, created = UserProfile.objects.get_or_create(user=instance)
    if not created:
        profile.save()
