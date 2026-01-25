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
from .models import Category, Tag, Post, Comment


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
    fields = ['name', 'slug', 'description']

    def post_count(self, obj):
        """Display the number of posts in this category."""
        count = obj.posts.filter(status='published').count()
        return count

    post_count.short_description = 'Published Posts'


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
        'title',
        'author',
        'category',
        'status',
        'views_count',
        'created_at',
        'published_at',
        'thumbnail_preview'
    ]

    # Sidebar filters
    list_filter = ['status', 'category', 'created_at', 'published_at']

    # Search functionality
    search_fields = ['title', 'content', 'excerpt', 'author__username']

    # Auto-populate slug from title
    prepopulated_fields = {'slug': ('title',)}

    # Date-based navigation
    date_hierarchy = 'published_at'

    # Read-only fields (can't be edited)
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'thumbnail_preview']

    # Many-to-many field widget
    filter_horizontal = ['tags']

    # Show comments inline
    inlines = [CommentInline]

    # Default ordering in admin
    ordering = ['-created_at']

    # Organize fields into sections (fieldsets)
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        ('Media', {
            'fields': ('featured_image', 'thumbnail_preview'),
            'classes': ('collapse',),  # Collapsible section
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Publishing', {
            'fields': ('author', 'status', 'published_at', 'allow_comments')
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',),
        }),
        ('Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def thumbnail_preview(self, obj):
        """Display a thumbnail of the featured image."""
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px;" />',
                obj.featured_image.url
            )
        return '-'

    thumbnail_preview.short_description = 'Thumbnail'

    def save_model(self, request, obj, form, change):
        """
        Override save_model to set author automatically.

        This is called when admin saves the model.
        """
        if not change:  # If creating new post
            obj.author = request.user
        super().save_model(request, obj, form, change)

    # Custom actions
    actions = ['make_published', 'make_draft']

    def make_published(self, request, queryset):
        """Bulk action to publish selected posts."""
        count = queryset.update(status='published')
        self.message_user(request, f'{count} posts marked as published.')

    make_published.short_description = 'Mark selected posts as published'

    def make_draft(self, request, queryset):
        """Bulk action to move posts to draft."""
        count = queryset.update(status='draft')
        self.message_user(request, f'{count} posts moved to draft.')

    make_draft.short_description = 'Mark selected posts as draft'


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


# Customize the admin site header
admin.site.site_header = 'Blog CMS Administration'
admin.site.site_title = 'Blog CMS Admin'
admin.site.index_title = 'Welcome to Blog CMS Admin Panel'
