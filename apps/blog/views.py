"""
=============================================================================
Blog Views - Handle HTTP Requests and Return Responses
=============================================================================

Views are functions or classes that:
    1. Receive HTTP requests
    2. Process data (read from database, handle forms)
    3. Return HTTP responses (usually rendered HTML)

Django provides two types of views:
    1. Function-Based Views (FBV) - Simple functions
    2. Class-Based Views (CBV) - Classes with methods for HTTP verbs

We use CBVs because they:
    - Reduce code duplication
    - Follow DRY principle
    - Are easier to extend
    - Handle common patterns (CRUD) well

Common Generic Views:
    - ListView: Display a list of objects
    - DetailView: Display single object details
    - CreateView: Form to create new objects
    - UpdateView: Form to edit existing objects
    - DeleteView: Confirm and delete objects

Mixins:
    - LoginRequiredMixin: Require user to be logged in
    - UserPassesTestMixin: Custom permission checks

=============================================================================
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect

from .models import Post, Category, Tag, Comment, CommentReaction
from .forms import PostForm, CommentForm, SearchForm


class HomeView(ListView):
    """
    Home page view - displays featured/recent posts.

    ListView automatically:
        - Fetches objects from database
        - Paginates results
        - Passes objects to template as 'object_list'
    """

    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'  # Custom name for template variable
    paginate_by = 6  # Show 6 posts per page

    def get_queryset(self):
        """
        Override get_queryset to filter posts.

        This method returns the list of posts to display.
        We only want published posts, ordered by date.
        """
        return Post.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'  # Optimize: fetch related objects in one query
        ).prefetch_related(
            'tags'  # Optimize: fetch many-to-many in efficient query
        ).order_by('-published_at')

    def get_context_data(self, **kwargs):
        """
        Add extra context data to the template.

        This method lets you pass additional variables to the template.
        The parent class handles the post list, we add extras.
        """
        context = super().get_context_data(**kwargs)

        # Add featured posts (most viewed)
        context['featured_posts'] = Post.objects.filter(
            status='published'
        ).order_by('-views_count')[:3]

        # Add recent comments
        context['recent_comments'] = Comment.objects.filter(
            is_approved=True
        ).select_related('author', 'post').order_by('-created_at')[:5]

        # Add search form
        context['search_form'] = SearchForm()

        return context


class PostListView(ListView):
    """
    Blog listing page - shows all published posts with pagination.
    """

    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9  # 3x3 grid of posts

    def get_queryset(self):
        return Post.objects.filter(
            status='published'
        ).select_related('author', 'category').prefetch_related('tags')


class PostDetailView(DetailView):
    """
    Single post detail page.

    DetailView automatically:
        - Fetches single object by pk or slug
        - Returns 404 if not found
        - Passes object to template as 'object' or 'post' (via context_object_name)
    """

    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'  # URL parameter name

    def get_queryset(self):
        """
        Allow viewing published posts, or any post by its author.
        """
        user = self.request.user

        if user.is_authenticated:
            # Logged-in users can see their own drafts
            return Post.objects.filter(
                Q(status='published') | Q(author=user)
            ).select_related('author', 'category').prefetch_related('tags')
        else:
            # Anonymous users only see published posts
            return Post.objects.filter(
                status='published'
            ).select_related('author', 'category').prefetch_related('tags')

    def get_object(self, queryset=None):
        """
        Get the post and increment view count.
        """
        obj = super().get_object(queryset)

        # Increment views (only for published posts, not author viewing)
        if obj.status == 'published':
            if not self.request.user.is_authenticated or obj.author != self.request.user:
                obj.increment_views()

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add comment form
        context['comment_form'] = CommentForm()

        # Get approved comments (top-level only, not replies)
        context['comments'] = self.object.comments.filter(
            is_approved=True,
            parent=None  # Only top-level comments
        ).select_related('author').prefetch_related('replies', 'reactions')

        # Get related posts
        context['related_posts'] = self.object.get_related_posts()

        # Get user's reactions for all comments (for highlighting active reactions)
        import json
        if self.request.user.is_authenticated:
            user_reactions = CommentReaction.objects.filter(
                comment__post=self.object,
                user=self.request.user
            ).values('comment_id', 'reaction_type')
            reactions_dict = {
                str(r['comment_id']): r['reaction_type'] for r in user_reactions
            }
            context['user_reactions'] = json.dumps(reactions_dict)
        else:
            context['user_reactions'] = json.dumps({})

        # Add reaction emojis mapping for template
        context['reaction_emojis'] = CommentReaction.REACTION_EMOJIS

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new blog post.

    LoginRequiredMixin:
        - Redirects anonymous users to login page
        - login_url specifies where to redirect

    CreateView:
        - Displays form on GET request
        - Validates and saves on POST request
        - Redirects to success_url on success
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    login_url = '/accounts/login/'  # Redirect here if not logged in

    def form_valid(self, form):
        """
        Called when form is valid.
        Set the author to the current user before saving.
        Handle publish vs draft action from buttons.
        """
        from django.utils import timezone

        form.instance.author = self.request.user

        # Check which button was clicked
        action = self.request.POST.get('action', 'publish')

        if action == 'draft':
            form.instance.status = 'draft'
            form.instance.published_at = None
            messages.success(self.request, 'Your post has been saved as a draft!')
        else:
            form.instance.status = 'published'
            if not form.instance.published_at:
                form.instance.published_at = timezone.now()
            messages.success(self.request, 'Your post has been published!')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Post'
        context['button_text'] = 'Publish Post'
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edit an existing blog post.

    UserPassesTestMixin:
        - Calls test_func() to check permissions
        - Returns 403 Forbidden if test fails
    """

    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def test_func(self):
        """
        Check if current user is the post author.
        Only the author can edit their own posts.
        """
        post = self.get_object()
        return self.request.user == post.author

    def form_valid(self, form):
        """
        Handle update with publish/draft action buttons.
        """
        from django.utils import timezone

        # Check which button was clicked
        action = self.request.POST.get('action', 'publish')

        if action == 'draft':
            form.instance.status = 'draft'
            messages.success(self.request, 'Your post has been saved as a draft!')
        else:
            form.instance.status = 'published'
            if not form.instance.published_at:
                form.instance.published_at = timezone.now()
            messages.success(self.request, 'Your post has been published!')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Post'
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a blog post.

    Shows confirmation page on GET.
    Deletes and redirects on POST.
    """

    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:home')  # Redirect after delete

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Your post has been deleted!')
        return super().delete(request, *args, **kwargs)


class CategoryDetailView(ListView):
    """
    Display posts in a specific category.

    Uses ListView because we're listing posts, not showing category details.
    """

    model = Post
    template_name = 'blog/category_detail.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        """Filter posts by category slug from URL."""
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status='published',
            category=self.category
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagDetailView(ListView):
    """
    Display posts with a specific tag.
    """

    model = Post
    template_name = 'blog/tag_detail.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status='published',
            tags=self.tag
        ).select_related('author', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class SearchView(ListView):
    """
    Search posts by title, content, and excerpt.

    Uses Q objects for complex queries (OR conditions).
    """

    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        """
        Filter posts based on search query.

        Q objects allow complex lookups:
            Q(title__icontains='django') | Q(content__icontains='django')
            This finds posts where title OR content contains 'django'

        __icontains: Case-insensitive contains
        """
        query = self.request.GET.get('q', '')
        self.query = query

        if query:
            return Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__name__icontains=query),
                status='published'
            ).distinct().select_related('author', 'category')

        return Post.objects.none()  # Return empty if no query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        context['search_form'] = SearchForm(initial={'q': self.query})
        return context


class AddCommentView(LoginRequiredMixin, View):
    """
    Handle comment submission.

    Uses View instead of CreateView for more control.
    Only handles POST requests (no GET form display).
    """

    def post(self, request, slug):
        """Handle POST request to add comment."""
        post = get_object_or_404(Post, slug=slug, status='published')

        # Check if comments are allowed
        if not post.allow_comments:
            messages.error(request, 'Comments are disabled for this post.')
            return redirect('blog:post_detail', slug=slug)

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user

            # Check if this is a reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = Comment.objects.get(id=parent_id)
                comment.parent = parent_comment

            comment.save()
            messages.success(request, 'Your comment has been added!')
        else:
            messages.error(request, 'There was an error with your comment.')

        return redirect('blog:post_detail', slug=slug)


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Delete a comment.

    Only comment author or post author can delete.
    """

    model = Comment
    template_name = 'blog/comment_confirm_delete.html'

    def test_func(self):
        comment = self.get_object()
        user = self.request.user
        # Comment author or post author can delete
        return user == comment.author or user == comment.post.author

    def get_success_url(self):
        """Redirect back to the post after deleting comment."""
        return reverse_lazy('blog:post_detail', kwargs={'slug': self.object.post.slug})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Comment deleted!')
        return super().delete(request, *args, **kwargs)


class AuthorPostsView(ListView):
    """
    Display all posts by a specific author.
    """

    model = Post
    template_name = 'blog/author_posts.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(
            author=self.author,
            status='published'
        ).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context


class MyDraftsView(LoginRequiredMixin, ListView):
    """
    Display user's draft posts.

    This page shows all drafts so users can continue editing
    and publish them when ready.
    """

    model = Post
    template_name = 'blog/my_drafts.html'
    context_object_name = 'drafts'
    paginate_by = 10

    def get_queryset(self):
        """Get only the current user's drafts."""
        return Post.objects.filter(
            author=self.request.user,
            status='draft'
        ).select_related('category').prefetch_related('tags').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Also get published count for stats
        context['published_count'] = Post.objects.filter(
            author=self.request.user,
            status='published'
        ).count()
        context['draft_count'] = self.get_queryset().count()
        return context


class PublishPostView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Publish a draft post.

    Changes the post status from 'draft' to 'published'
    and sets the published_at date.
    """

    def test_func(self):
        """Only the author can publish their own posts."""
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        return self.request.user == post.author

    def post(self, request, slug):
        """Handle POST request to publish the post."""
        from django.utils import timezone

        post = get_object_or_404(Post, slug=slug, author=request.user)

        if post.status == 'draft':
            post.status = 'published'
            post.published_at = timezone.now()
            post.save()
            messages.success(request, f'"{post.title}" has been published!')
        else:
            messages.info(request, 'This post is already published.')

        return redirect('blog:post_detail', slug=post.slug)

    def get(self, request, slug):
        """Redirect GET requests to POST."""
        return redirect('blog:my_drafts')


class NewsletterSubscribeView(View):
    """
    Handle newsletter subscription.

    Accepts email via POST, saves subscriber, and sends welcome email.
    """

    def post(self, request):
        from django.core.mail import send_mail
        from django.conf import settings
        from django.http import JsonResponse
        from .models import NewsletterSubscriber

        email = request.POST.get('email', '').strip()

        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a valid email address.'
            })

        # Check if already subscribed
        if NewsletterSubscriber.objects.filter(email=email).exists():
            subscriber = NewsletterSubscriber.objects.get(email=email)
            if subscriber.is_active:
                return JsonResponse({
                    'success': False,
                    'message': 'This email is already subscribed.'
                })
            else:
                # Reactivate subscription
                subscriber.is_active = True
                subscriber.save()
                message = 'Welcome back! Your subscription has been reactivated.'
        else:
            # Create new subscriber
            NewsletterSubscriber.objects.create(email=email, is_verified=True)
            message = 'Thank you for subscribing!'

        # Send welcome email
        try:
            send_mail(
                subject='Welcome to Blog CMS Newsletter!',
                message=f'''Hello!

Thank you for subscribing to our newsletter. You'll receive updates on our latest posts and content.

We're excited to have you join our community!

Best regards,
The Blog CMS Team

---
If you didn't subscribe to this newsletter, please ignore this email.
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass  # Don't fail if email sending fails

        return JsonResponse({
            'success': True,
            'message': message
        })


class ReactToCommentView(LoginRequiredMixin, View):
    """
    Handle emoji reactions on comments.

    Supports adding, changing, and removing reactions.
    If user already has the same reaction, it removes it (toggle).
    If user has a different reaction, it updates to the new one.
    """

    def post(self, request, comment_id):
        from django.http import JsonResponse

        comment = get_object_or_404(Comment, pk=comment_id)
        reaction_type = request.POST.get('reaction_type', '').strip()

        # Validate reaction type
        valid_types = [choice[0] for choice in CommentReaction.REACTION_CHOICES]
        if reaction_type not in valid_types:
            return JsonResponse({
                'success': False,
                'message': 'Invalid reaction type.'
            }, status=400)

        # Check if user already has a reaction on this comment
        existing_reaction = CommentReaction.objects.filter(
            comment=comment,
            user=request.user
        ).first()

        if existing_reaction:
            if existing_reaction.reaction_type == reaction_type:
                # Same reaction - toggle off (remove)
                existing_reaction.delete()
                action = 'removed'
            else:
                # Different reaction - update
                existing_reaction.reaction_type = reaction_type
                existing_reaction.save()
                action = 'updated'
        else:
            # No existing reaction - create new
            CommentReaction.objects.create(
                comment=comment,
                user=request.user,
                reaction_type=reaction_type
            )
            action = 'added'

        # Get updated reaction summary
        summary = comment.get_reactions_summary()
        user_reaction = comment.get_user_reaction(request.user)

        return JsonResponse({
            'success': True,
            'action': action,
            'total_reactions': summary['total'],
            'reactions_by_type': summary['by_type'],
            'top_reactions': summary['top_reactions'],
            'user_reaction': user_reaction,
            'emojis': CommentReaction.REACTION_EMOJIS
        })
