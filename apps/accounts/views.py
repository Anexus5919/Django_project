"""
=============================================================================
Accounts Views - User Profile Management
=============================================================================

These views handle user profile functionality.
Authentication (login, register, etc.) is handled by django-allauth.

Views:
    - ProfileView: Show logged-in user's profile
    - ProfileDetailView: Show any user's profile
    - ProfileUpdateView: Edit profile

=============================================================================
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy

from .models import UserProfile
from .forms import UserForm, UserProfileForm


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Display the logged-in user's profile.

    TemplateView is simple: just render a template with context.
    We add the user's profile data to context.
    """

    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get user's posts
        context['posts'] = user.posts.filter(status='published').order_by('-published_at')[:5]
        context['draft_posts'] = user.posts.filter(status='draft').order_by('-created_at')[:5]

        # Get user's comments
        context['comments'] = user.comments.order_by('-created_at')[:5]

        # Statistics
        context['stats'] = {
            'total_posts': user.posts.filter(status='published').count(),
            'total_drafts': user.posts.filter(status='draft').count(),
            'total_comments': user.comments.count(),
            'total_views': sum(p.views_count for p in user.posts.filter(status='published')),
        }

        return context


class ProfileDetailView(DetailView):
    """
    View any user's public profile.

    Finds user by username, not pk.
    """

    model = User
    template_name = 'accounts/profile_detail.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        """Get user by username."""
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object

        # Check if profile is public
        if hasattr(profile_user, 'profile') and not profile_user.profile.is_public:
            # Only show if viewing own profile
            if self.request.user != profile_user:
                context['is_private'] = True
                return context

        # Get user's published posts
        context['posts'] = profile_user.posts.filter(
            status='published'
        ).order_by('-published_at')[:10]

        # Statistics
        context['stats'] = {
            'total_posts': profile_user.posts.filter(status='published').count(),
            'total_comments': profile_user.comments.count(),
        }

        return context


class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    """
    Edit user profile.

    We use TemplateView with custom form handling because we need
    to handle TWO forms: UserForm and UserProfileForm.
    """

    template_name = 'accounts/profile_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Create forms with current data
        context['user_form'] = UserForm(instance=user)
        context['profile_form'] = UserProfileForm(instance=user.profile)

        return context

    def post(self, request, *args, **kwargs):
        """Handle form submission."""
        user = request.user

        # Create forms with submitted data
        user_form = UserForm(
            request.POST,
            instance=user
        )
        profile_form = UserProfileForm(
            request.POST,
            request.FILES,  # For avatar upload
            instance=user.profile
        )

        # Validate both forms
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
        else:
            # Re-render with errors
            messages.error(request, 'Please correct the errors below.')
            return render(request, self.template_name, {
                'user_form': user_form,
                'profile_form': profile_form,
            })
