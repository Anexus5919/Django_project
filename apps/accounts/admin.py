"""
=============================================================================
Accounts Admin Configuration
=============================================================================

Customize the admin for user profiles.
We also extend the User admin to show profile info inline.

=============================================================================
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile.

    This shows the profile fields on the User edit page,
    making it easy to manage both in one place.
    """

    model = UserProfile
    can_delete = False
    verbose_name = 'Profile'
    verbose_name_plural = 'Profile'
    fk_name = 'user'

    # Organize fields
    fieldsets = (
        ('Profile Info', {
            'fields': ('avatar', 'bio', 'location', 'website')
        }),
        ('Social Links', {
            'fields': ('twitter', 'github', 'linkedin'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('email_notifications', 'is_public'),
            'classes': ('collapse',)
        }),
    )


class UserAdmin(BaseUserAdmin):
    """
    Extended User admin with profile inline.

    This replaces Django's default User admin.
    """

    inlines = [UserProfileInline]
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'date_joined',
        'post_count'
    ]

    def post_count(self, obj):
        """Display user's post count."""
        return obj.posts.filter(status='published').count()

    post_count.short_description = 'Posts'

    def get_inline_instances(self, request, obj=None):
        """Only show inline when editing existing user."""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Standalone UserProfile admin.

    Useful for viewing all profiles at once.
    """

    list_display = [
        'user',
        'avatar_preview',
        'location',
        'is_public',
        'created_at'
    ]
    list_filter = ['is_public', 'email_notifications', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio', 'location']
    readonly_fields = ['user', 'created_at', 'updated_at', 'avatar_preview']

    def avatar_preview(self, obj):
        """Display avatar thumbnail."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; '
                'border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url
            )
        return '-'

    avatar_preview.short_description = 'Avatar'


# Unregister the default User admin and register our extended version
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
