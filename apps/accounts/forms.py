"""
=============================================================================
Accounts Forms - User Profile Management
=============================================================================

These forms handle user profile updates.
Authentication forms (login, register) are provided by django-allauth.

We need two forms for profile editing:
    1. UserForm - Updates User model (first_name, last_name, email)
    2. UserProfileForm - Updates UserProfile model (bio, avatar, etc.)

Both forms are submitted together in the view.

=============================================================================
"""

from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML

from .models import UserProfile


class UserForm(forms.ModelForm):
    """
    Form for updating basic User information.

    This updates Django's built-in User model fields:
        - first_name
        - last_name
        - email
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
        }

    def clean_email(self):
        """
        Ensure email is unique across users.
        """
        email = self.cleaned_data.get('email')
        # Check if another user has this email
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class UserProfileForm(forms.ModelForm):
    """
    Form for updating UserProfile information.

    Handles additional profile fields:
        - bio
        - avatar
        - location
        - website
        - social media links
        - notification settings
    """

    class Meta:
        model = UserProfile
        fields = [
            'avatar',
            'bio',
            'location',
            'website',
            'twitter',
            'github',
            'linkedin',
            'email_notifications',
            'is_public',
        ]
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'twitter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'username (without @)'
            }),
            'github': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'username'
            }),
            'linkedin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'profile URL or username'
            }),
        }
        labels = {
            'email_notifications': 'Email me when someone comments on my posts',
            'is_public': 'Make my profile visible to other users',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Crispy forms layout
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'

        self.helper.layout = Layout(
            Div(
                HTML('<h5 class="mb-3">Profile Picture</h5>'),
                'avatar',
                css_class='mb-4'
            ),
            Div(
                HTML('<h5 class="mb-3">About You</h5>'),
                'bio',
                Row(
                    Column('location', css_class='col-md-6'),
                    Column('website', css_class='col-md-6'),
                ),
                css_class='mb-4'
            ),
            Div(
                HTML('<h5 class="mb-3">Social Links</h5>'),
                Row(
                    Column('twitter', css_class='col-md-4'),
                    Column('github', css_class='col-md-4'),
                    Column('linkedin', css_class='col-md-4'),
                ),
                css_class='mb-4'
            ),
            Div(
                HTML('<h5 class="mb-3">Settings</h5>'),
                'email_notifications',
                'is_public',
                css_class='mb-4'
            ),
        )


class CombinedProfileForm:
    """
    Helper class to manage both forms together.

    This isn't a Django form, but a utility class that
    makes handling both forms in views easier.

    Usage in view:
        combined = CombinedProfileForm(request.user)
        if request.method == 'POST':
            combined.bind(request.POST, request.FILES)
            if combined.is_valid():
                combined.save()
    """

    def __init__(self, user, data=None, files=None):
        self.user_form = UserForm(
            data=data,
            instance=user,
            prefix='user'
        )
        self.profile_form = UserProfileForm(
            data=data,
            files=files,
            instance=user.profile,
            prefix='profile'
        )

    def is_valid(self):
        """Check if both forms are valid."""
        return self.user_form.is_valid() and self.profile_form.is_valid()

    def save(self):
        """Save both forms."""
        self.user_form.save()
        self.profile_form.save()

    @property
    def errors(self):
        """Combine errors from both forms."""
        errors = {}
        errors.update(self.user_form.errors)
        errors.update(self.profile_form.errors)
        return errors
