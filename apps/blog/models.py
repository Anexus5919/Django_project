"""
=============================================================================
Blog Models - The Database Structure
=============================================================================

Models are Python classes that define the structure of your database tables.
Django's ORM (Object-Relational Mapper) converts these to SQL automatically.

Model concepts:
    - Each class = one database table
    - Each attribute = one database column
    - Each instance = one row in the table

Field types used:
    - CharField: Short text (max 255 characters)
    - TextField: Long text (unlimited)
    - SlugField: URL-friendly text (e.g., "my-first-post")
    - ImageField: File path to uploaded image
    - DateTimeField: Date and time
    - BooleanField: True/False
    - IntegerField: Whole numbers
    - ForeignKey: Many-to-one relationship
    - ManyToManyField: Many-to-many relationship

Relationships:
    - ForeignKey: One post has ONE author (many posts -> one user)
    - ManyToManyField: One post has MANY tags, one tag has MANY posts

=============================================================================
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class Category(models.Model):
    """
    Category Model - Organizes blog posts into groups.

    Example categories: "Technology", "Travel", "Food", "Lifestyle"

    Database table: blog_category
    """

    # Icon choices for categories (Bootstrap Icons)
    ICON_CHOICES = (
        ('bi-laptop', 'Technology'),
        ('bi-globe', 'Web Development'),
        ('bi-code-slash', 'Programming'),
        ('bi-graph-up', 'Data Science'),
        ('bi-mortarboard', 'Tutorial'),
        ('bi-newspaper', 'News'),
        ('bi-camera', 'Photography'),
        ('bi-palette', 'Design'),
        ('bi-briefcase', 'Business'),
        ('bi-heart', 'Lifestyle'),
        ('bi-airplane', 'Travel'),
        ('bi-cup-hot', 'Food'),
        ('bi-controller', 'Gaming'),
        ('bi-music-note', 'Music'),
        ('bi-film', 'Entertainment'),
        ('bi-book', 'Education'),
        ('bi-lightbulb', 'Ideas'),
        ('bi-chat-quote', 'Opinion'),
    )

    # Color choices for category styling
    COLOR_CHOICES = (
        ('#4f46e5', 'Indigo'),
        ('#2563eb', 'Blue'),
        ('#0891b2', 'Cyan'),
        ('#059669', 'Green'),
        ('#84cc16', 'Lime'),
        ('#eab308', 'Yellow'),
        ('#f97316', 'Orange'),
        ('#ef4444', 'Red'),
        ('#ec4899', 'Pink'),
        ('#8b5cf6', 'Purple'),
        ('#6366f1', 'Violet'),
        ('#64748b', 'Slate'),
    )

    # ----- Fields -----

    # The category name (e.g., "Technology")
    # max_length is required for CharField
    name = models.CharField(
        max_length=100,
        unique=True,  # No two categories can have the same name
        help_text="Category name (e.g., 'Technology', 'Travel')"
    )

    # URL-friendly version of the name (e.g., "technology")
    # SlugField only allows letters, numbers, hyphens, and underscores
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,  # Can be empty in forms (we auto-generate it)
        help_text="URL-friendly name (auto-generated from name)"
    )

    # Optional description for the category
    description = models.TextField(
        blank=True,  # Optional in forms
        help_text="Brief description of this category"
    )

    # Icon for category (used in default post images)
    icon = models.CharField(
        max_length=50,
        choices=ICON_CHOICES,
        default='bi-newspaper',
        help_text="Bootstrap icon for this category"
    )

    # Color for category styling
    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default='#4f46e5',
        help_text="Color for category badge and default image"
    )

    # When the category was created
    # auto_now_add=True means it's set automatically when created
    created_at = models.DateTimeField(auto_now_add=True)

    # ----- Meta Options -----

    class Meta:
        """
        Meta class defines model-level options.
        """
        # Human-readable name for the model
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'  # Plural form

        # Default ordering (newest first would be '-created_at')
        ordering = ['name']

    # ----- Methods -----

    def __str__(self):
        """
        String representation of the model.
        This is what you see in the admin panel and shell.
        """
        return self.name

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate slug from name.
        Called every time you save a category.
        """
        if not self.slug:
            # slugify converts "My Category" to "my-category"
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the URL to view this category's posts.
        Used by Django's generic views and in templates.
        """
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

    def post_count(self):
        """Returns the number of published posts in this category."""
        return self.posts.filter(status='published').count()


class Tag(models.Model):
    """
    Tag Model - Fine-grained labeling for posts.

    Tags are more specific than categories.
    Example: A post in "Technology" category might have tags:
    "Python", "Django", "Web Development", "Tutorial"

    Database table: blog_tag
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Tag name (e.g., 'Python', 'Tutorial')"
    )

    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})

    def post_count(self):
        """Returns the number of published posts with this tag."""
        return self.posts.filter(status='published').count()


class Post(models.Model):
    """
    Post Model - The main blog post content.

    This is the core model of the blog.
    Each post belongs to one category and one author,
    but can have multiple tags.

    Database table: blog_post
    """

    # ----- Status Choices -----
    # Tuple of tuples: (database_value, display_value)
    STATUS_CHOICES = (
        ('draft', 'Draft'),        # Not visible to public
        ('published', 'Published'),  # Visible to everyone
    )

    # ----- Content Fields -----

    title = models.CharField(
        max_length=200,
        help_text="Post title (appears in browser tab and listings)"
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text="URL-friendly title (auto-generated)"
    )

    # CKEditor5Field provides a rich text editor
    # config_name refers to the configuration in settings.py
    content = CKEditor5Field(
        'Content',
        config_name='default',
        help_text="Main post content with formatting"
    )

    # Short summary shown in post listings
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief summary (shown in post listings)"
    )

    # Featured image for the post
    featured_image = models.ImageField(
        upload_to='posts/%Y/%m/%d/',  # Organize by date
        blank=True,
        null=True,  # Can be NULL in database
        help_text="Main image for the post"
    )

    # ----- Relationship Fields -----

    # ForeignKey creates a many-to-one relationship
    # Many posts can belong to one author
    author = models.ForeignKey(
        User,  # Link to Django's built-in User model
        on_delete=models.CASCADE,  # Delete posts if user is deleted
        related_name='posts',  # Access user's posts: user.posts.all()
        help_text="Post author"
    )

    # Many posts can belong to one category
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # Keep post if category is deleted
        null=True,  # Allow NULL in database
        blank=True,  # Optional in forms
        related_name='posts',
        help_text="Post category"
    )

    # ManyToManyField creates a many-to-many relationship
    # A post can have many tags, a tag can belong to many posts
    tags = models.ManyToManyField(
        Tag,
        blank=True,  # Tags are optional
        related_name='posts',  # Access tag's posts: tag.posts.all()
        help_text="Post tags"
    )

    # ----- Status Fields -----

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Draft posts are only visible to author"
    )

    # Track post popularity
    views_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this post was viewed"
    )

    # Allow/disallow comments
    allow_comments = models.BooleanField(
        default=True,
        help_text="Enable comments on this post"
    )

    # ----- Date Fields -----

    # auto_now_add: Set once when created
    created_at = models.DateTimeField(auto_now_add=True)

    # auto_now: Updated every time the model is saved
    updated_at = models.DateTimeField(auto_now=True)

    # When the post was published (can be scheduled for future)
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the post was/will be published"
    )

    # ----- SEO Fields -----

    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta description (160 chars max)"
    )

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        # Order by published date, newest first
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Override save to:
        1. Auto-generate slug from title
        2. Set published_at when status changes to published
        3. Auto-generate excerpt if not provided
        """
        # Generate slug if not provided
        if not self.slug:
            # Make slug unique by adding a number if needed
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Set published_at when first published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        # Auto-generate excerpt from content if not provided
        if not self.excerpt and self.content:
            # Strip HTML tags and take first 200 characters
            import re
            clean_content = re.sub('<[^<]+?>', '', self.content)
            self.excerpt = clean_content[:200] + '...' if len(clean_content) > 200 else clean_content

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns the URL to view this post."""
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """Increment the view count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    @property
    def is_published(self):
        """Check if post is published and publication date has passed."""
        if self.status != 'published':
            return False
        if self.published_at and self.published_at > timezone.now():
            return False
        return True

    def get_related_posts(self, limit=3):
        """
        Get related posts based on category and tags.
        Useful for "You might also like" section.
        """
        # Get posts in same category or with same tags
        related = Post.objects.filter(
            status='published'
        ).exclude(
            pk=self.pk
        ).filter(
            models.Q(category=self.category) |
            models.Q(tags__in=self.tags.all())
        ).distinct()[:limit]
        return related


class Comment(models.Model):
    """
    Comment Model - User comments on posts.

    Supports threaded comments (replies to comments).

    Database table: blog_comment
    """

    # Link to the post being commented on
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,  # Delete comments if post is deleted
        related_name='comments',   # Access post's comments: post.comments.all()
    )

    # Comment author (logged-in user)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    # Comment text
    content = models.TextField(
        max_length=1000,
        help_text="Comment text (max 1000 characters)"
    )

    # Parent comment for replies (enables threaded comments)
    # If parent is NULL, this is a top-level comment
    parent = models.ForeignKey(
        'self',  # Self-referential foreign key
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',  # Access comment's replies: comment.replies.all()
    )

    # Moderation status
    is_approved = models.BooleanField(
        default=True,  # Auto-approve by default
        help_text="Approved comments are visible to public"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        # Oldest first for comments (chronological order)
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on "{self.post.title}"'

    def get_replies(self):
        """Get all approved replies to this comment."""
        return self.replies.filter(is_approved=True)

    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent is not None

    def get_reactions_summary(self):
        """
        Get a summary of reactions for this comment.
        Returns a dict with reaction counts and total.
        """
        from django.db.models import Count

        reactions = self.reactions.values('reaction_type').annotate(
            count=Count('id')
        ).order_by('-count')

        summary = {
            'total': 0,
            'by_type': {},
            'top_reactions': []
        }

        for r in reactions:
            summary['by_type'][r['reaction_type']] = r['count']
            summary['total'] += r['count']
            if len(summary['top_reactions']) < 3:
                summary['top_reactions'].append(r['reaction_type'])

        return summary

    def get_user_reaction(self, user):
        """Get the current user's reaction on this comment, if any."""
        if not user.is_authenticated:
            return None
        reaction = self.reactions.filter(user=user).first()
        return reaction.reaction_type if reaction else None


class CommentReaction(models.Model):
    """
    Comment Reaction Model - Emoji reactions on comments like LinkedIn.

    Users can react to comments with one of 6 emojis.
    Each user can only have one reaction per comment (can change it).

    Database table: blog_commentreaction
    """

    # Available reaction types - similar to LinkedIn
    REACTION_CHOICES = (
        ('like', 'Like'),           # Thumbs up
        ('love', 'Love'),           # Heart
        ('celebrate', 'Celebrate'), # Clapping hands
        ('insightful', 'Insightful'),  # Light bulb
        ('curious', 'Curious'),     # Thinking face
        ('support', 'Support'),     # Hands together
    )

    # Map reactions to emojis for display
    REACTION_EMOJIS = {
        'like': '👍',
        'love': '❤️',
        'celebrate': '🎉',
        'insightful': '💡',
        'curious': '🤔',
        'support': '🙏',
    }

    # Link to the comment being reacted to
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='reactions',
    )

    # User who reacted
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment_reactions',
    )

    # Type of reaction
    reaction_type = models.CharField(
        max_length=20,
        choices=REACTION_CHOICES,
    )

    # When the reaction was created/updated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comment Reaction'
        verbose_name_plural = 'Comment Reactions'
        # Each user can only have one reaction per comment
        unique_together = ['comment', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction_type} on comment #{self.comment.id}"

    @property
    def emoji(self):
        """Return the emoji for this reaction."""
        return self.REACTION_EMOJIS.get(self.reaction_type, '👍')

    @classmethod
    def get_emoji_for_type(cls, reaction_type):
        """Class method to get emoji for a reaction type."""
        return cls.REACTION_EMOJIS.get(reaction_type, '👍')


class NewsletterSubscriber(models.Model):
    """
    Newsletter Subscriber Model - Store email subscribers.

    Stores email addresses of users who want to receive updates.
    Includes verification and unsubscribe functionality.

    Database table: blog_newslettersubscriber
    """

    email = models.EmailField(
        unique=True,
        help_text="Subscriber's email address"
    )

    # Verification
    is_verified = models.BooleanField(
        default=False,
        help_text="Email has been verified"
    )

    # Active status (for unsubscribe)
    is_active = models.BooleanField(
        default=True,
        help_text="Subscription is active"
    )

    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
        ordering = ['-subscribed_at']

    def __str__(self):
        status = "Active" if self.is_active else "Unsubscribed"
        return f"{self.email} ({status})"
