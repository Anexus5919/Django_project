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
        profile = user.profile

        # Handle User model fields
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')

        # Handle UserProfile fields
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.website = request.POST.get('website', '')
        profile.twitter = request.POST.get('twitter', '')
        profile.github = request.POST.get('github', '')
        profile.linkedin = request.POST.get('linkedin', '')

        # Handle checkboxes (unchecked = not in POST data)
        profile.email_notifications = 'email_notifications' in request.POST
        profile.is_public = 'is_public' in request.POST

        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        try:
            user.save()
            profile.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return render(request, self.template_name, {})


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Comprehensive dashboard for content management.

    This replaces the need for Django admin for content creators.
    Provides full control over posts, categories, tags, and comments.
    """

    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        from apps.blog.models import Post, Category, Tag, Comment

        context = super().get_context_data(**kwargs)
        user = self.request.user

        # User's posts
        context['published_posts'] = user.posts.filter(status='published').order_by('-published_at')[:10]
        context['draft_posts'] = user.posts.filter(status='draft').order_by('-updated_at')[:10]

        # Recent comments on user's posts
        context['recent_comments'] = Comment.objects.filter(
            post__author=user
        ).order_by('-created_at')[:10]

        # Statistics
        context['stats'] = {
            'total_published': user.posts.filter(status='published').count(),
            'total_drafts': user.posts.filter(status='draft').count(),
            'total_comments': Comment.objects.filter(post__author=user).count(),
            'total_views': sum(p.views_count for p in user.posts.filter(status='published')),
            'pending_comments': Comment.objects.filter(post__author=user, is_approved=False).count(),
        }

        # For staff users, show additional management options
        if user.is_staff:
            context['all_categories'] = Category.objects.all()
            context['all_tags'] = Tag.objects.all()
            context['total_posts'] = Post.objects.count()
            context['total_users'] = User.objects.count()

        return context


class ManageCommentsView(LoginRequiredMixin, TemplateView):
    """
    Manage comments on user's posts.

    Allows approving, rejecting, and deleting comments.
    """

    template_name = 'accounts/manage_comments.html'

    def get_context_data(self, **kwargs):
        from apps.blog.models import Comment

        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get all comments on user's posts
        context['comments'] = Comment.objects.filter(
            post__author=user
        ).select_related('post', 'author').order_by('-created_at')

        # Filter by status if requested
        status = self.request.GET.get('status')
        if status == 'pending':
            context['comments'] = context['comments'].filter(is_approved=False)
        elif status == 'approved':
            context['comments'] = context['comments'].filter(is_approved=True)

        return context


class ApproveCommentView(LoginRequiredMixin, TemplateView):
    """
    Approve or reject a comment.
    """

    def post(self, request, pk):
        from apps.blog.models import Comment

        comment = get_object_or_404(Comment, pk=pk, post__author=request.user)
        action = request.POST.get('action')

        if action == 'approve':
            comment.is_approved = True
            comment.save()
            messages.success(request, 'Comment approved.')
        elif action == 'reject':
            comment.is_approved = False
            comment.save()
            messages.success(request, 'Comment rejected.')
        elif action == 'delete':
            comment.delete()
            messages.success(request, 'Comment deleted.')

        return redirect('accounts:manage_comments')
