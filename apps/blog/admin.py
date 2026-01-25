"""
=============================================================================
Blog Admin Configuration
=============================================================================

The Django admin is a powerful built-in interface for managing your data.
This file customizes how blog models appear in the admin panel.

Key concepts:
    - ModelAdmin: Customize how a model is displayed
    - list_display: Columns shown in the list view
    - list_filter: Sidebar filters
    - search_fields: Fields to search
    - prepopulated_fields: Auto-fill fields (like slug from title)
    - inlines: Show related models on the same page

Access admin at: http://localhost:8000/admin/

=============================================================================
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Tag, Post, Comment, NewsletterSubscriber


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model.

    Features:
        - Auto-generate slug from name
        - Show post count in list view
        - Search by name
    """

    # Columns to display in list view
    list_display = ['name', 'slug', 'post_count', 'created_at']

    # Fields that are auto-populated
    prepopulated_fields = {'slug': ('name',)}

    # Search functionality
    search_fields = ['name', 'description']

    # Date hierarchy navigation
    date_hierarchy = 'created_at'

    # Fields shown in the edit form
    fields = ['name', 'slug', 'description', 'icon', 'color']

    def post_count(self, obj):
        """Display the number of posts in this category."""
        count = obj.posts.filter(status='published').count()
        return count

    post_count.short_description = 'Published Posts'

    def icon_preview(self, obj):
        """Display the category icon."""
        return format_html(
            '<i class="bi {}" style="font-size: 1.5rem; color: {};"></i>',
            obj.icon, obj.color
        )
    icon_preview.short_description = 'Icon'

    def color_preview(self, obj):
        """Display the category color."""
        return format_html(
            '<div style="width: 20px; height: 20px; background: {}; border-radius: 4px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'

    list_display = ['name', 'slug', 'post_count', 'icon', 'color', 'created_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin configuration for Tag model.
    """

    list_display = ['name', 'slug', 'post_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def post_count(self, obj):
        return obj.posts.filter(status='published').count()

    post_count.short_description = 'Posts'


class CommentInline(admin.TabularInline):
    """
    Inline display of comments on the Post edit page.

    Inline admins let you edit related objects on the same page
    as the parent object.
    """

    model = Comment
    extra = 0  # Don't show empty extra forms
    readonly_fields = ['author', 'content', 'created_at', 'is_approved']
    can_delete = True

    # Only show top-level comments (not replies)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent=None)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for Post model.

    This is the most complex admin because posts have
    many fields and relationships.
    """

    # List view configuration
    list_display = [
        'thumbnail_preview',
        'title_with_link',
        'author',
        'category_badge',
        'status_badge',
        'views_count',
        'comment_count',
        'published_at',
    ]

    # Sidebar filters
    list_filter = ['status', 'category', 'created_at', 'published_at', 'author']

    # Search functionality
    search_fields = ['title', 'content', 'excerpt', 'author__username']

    # Auto-populate slug from title
    prepopulated_fields = {'slug': ('title',)}

    # Date-based navigation
    date_hierarchy = 'published_at'

    # Read-only fields (can't be edited)
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'thumbnail_preview_large']

    # Many-to-many field widget
    filter_horizontal = ['tags']

    # Show comments inline
    inlines = [CommentInline]

    # Default ordering in admin
    ordering = ['-created_at']

    # Items per page
    list_per_page = 20

    # Organize fields into sections (fieldsets)
    fieldsets = (
        ('Post Content', {
            'fields': ('title', 'slug', 'content', 'excerpt'),
            'description': 'Enter the main content of your blog post.'
        }),
        ('Featured Image', {
            'fields': ('featured_image', 'thumbnail_preview_large'),
            'description': 'Upload an eye-catching image for your post.'
        }),
        ('Organization', {
            'fields': ('category', 'tags'),
            'description': 'Categorize your post to help readers find it.'
        }),
        ('Publishing Options', {
            'fields': ('author', 'status', 'published_at', 'allow_comments'),
            'description': 'Control when and how your post appears.'
        }),
        ('SEO Settings', {
            'fields': ('meta_description',),
            'classes': ('collapse',),
            'description': 'Optimize your post for search engines.'
        }),
        ('Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def title_with_link(self, obj):
        """Display title with link to view on site."""
        site_url = obj.get_absolute_url()
        return format_html(
            '<strong>{}</strong><br>'
            '<small><a href="{}" target="_blank" style="color: #417690;">View on site →</a></small>',
            obj.title[:50] + '...' if len(obj.title) > 50 else obj.title,
            site_url
        )
    title_with_link.short_description = 'Title'
    title_with_link.admin_order_field = 'title'

    def thumbnail_preview(self, obj):
        """Display a small thumbnail of the featured image."""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 40px; object-fit: cover; border-radius: 4px;" />',
                obj.featured_image.url
            )
        return format_html(
            '<div style="width: 60px; height: 40px; background: #f0f0f0; border-radius: 4px; '
            'display: flex; align-items: center; justify-content: center; color: #999; font-size: 12px;">No img</div>'
        )
    thumbnail_preview.short_description = 'Image'

    def thumbnail_preview_large(self, obj):
        """Display a larger thumbnail for the edit form."""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: cover; border-radius: 8px;" />',
                obj.featured_image.url
            )
        return format_html('<span style="color: #999;">No image uploaded yet</span>')
    thumbnail_preview_large.short_description = 'Current Image'

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'published': ('#28a745', 'white'),
            'draft': ('#ffc107', 'black'),
        }
        bg_color, text_color = colors.get(obj.status, ('#6c757d', 'white'))
        return format_html(
            '<span style="background: {}; color: {}; padding: 3px 10px; border-radius: 12px; '
            'font-size: 11px; font-weight: 600; text-transform: uppercase;">{}</span>',
            bg_color, text_color, obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def category_badge(self, obj):
        """Display category as a badge."""
        if obj.category:
            return format_html(
                '<span style="background: #e9ecef; color: #495057; padding: 3px 8px; '
                'border-radius: 4px; font-size: 12px;">{}</span>',
                obj.category.name
            )
        return format_html('<span style="color: #999;">—</span>')
    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'

    def comment_count(self, obj):
        """Display comment count with icon."""
        count = obj.comments.filter(is_approved=True).count()
        return format_html(
            '<span style="color: #666;">💬 {}</span>',
            count
        )
    comment_count.short_description = 'Comments'

    def save_model(self, request, obj, form, change):
        """Set author automatically on create."""
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    # Custom actions
    actions = ['make_published', 'make_draft']

    @admin.action(description='✅ Publish selected posts')
    def make_published(self, request, queryset):
        """Bulk action to publish selected posts."""
        from django.utils import timezone
        count = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, f'✅ {count} posts have been published.')

    @admin.action(description='📝 Move to drafts')
    def make_draft(self, request, queryset):
        """Bulk action to move posts to draft."""
        count = queryset.update(status='draft')
        self.message_user(request, f'📝 {count} posts moved to drafts.')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comment model.

    Features:
        - Moderate comments (approve/unapprove)
        - Filter by approval status
        - Link to parent post
    """

    list_display = ['short_content', 'author', 'post_link', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['author', 'post', 'parent', 'created_at', 'updated_at']

    # Editable in list view
    list_editable = ['is_approved']

    actions = ['approve_comments', 'unapprove_comments']

    def short_content(self, obj):
        """Show truncated content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    short_content.short_description = 'Content'

    def post_link(self, obj):
        """Create a link to the post in admin."""
        from django.urls import reverse
        url = reverse('admin:blog_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title[:30])

    post_link.short_description = 'Post'

    def approve_comments(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f'{count} comments approved.')

    approve_comments.short_description = 'Approve selected comments'

    def unapprove_comments(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f'{count} comments unapproved.')

    unapprove_comments.short_description = 'Unapprove selected comments'


# =============================================================================
# Admin Site Customization
# =============================================================================

admin.site.site_header = format_html(
    '<span style="font-weight: 700; letter-spacing: -0.5px;">📝 Blog CMS</span> '
    '<span style="font-weight: 400; color: #999;">Administration</span>'
)
admin.site.site_title = 'Blog CMS Admin'
admin.site.index_title = format_html(
    '<div style="margin-bottom: 10px;">'
    '<h1 style="font-size: 24px; font-weight: 600; margin: 0;">Welcome to Blog CMS Admin</h1>'
    '<p style="color: #666; margin: 5px 0 0 0;">Manage your blog posts, categories, tags, and user comments.</p>'
    '</div>'
)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """
    Admin configuration for Newsletter Subscribers.
    """

    list_display = ['email', 'is_active', 'is_verified', 'subscribed_at']
    list_filter = ['is_active', 'is_verified', 'subscribed_at']
    search_fields = ['email']
    readonly_fields = ['subscribed_at', 'verified_at']
    list_editable = ['is_active']
    ordering = ['-subscribed_at']

    actions = ['activate_subscribers', 'deactivate_subscribers']

    @admin.action(description='Activate selected subscribers')
    def activate_subscribers(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} subscribers activated.')

    @admin.action(description='Deactivate selected subscribers')
    def deactivate_subscribers(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} subscribers deactivated.')


# Add custom admin CSS
class CustomAdminMixin:
    """Mixin to add custom styling to admin."""

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
