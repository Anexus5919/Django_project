"""
=============================================================================
Core Context Processors - Global Template Variables
=============================================================================

Context processors add variables to EVERY template automatically.
You don't need to pass them manually in views.

How they work:
    1. You define a function that takes 'request' as argument
    2. Function returns a dictionary of variables
    3. Add function to TEMPLATES setting in settings.py
    4. Variables are available in all templates

Use cases:
    - Site name and settings
    - Navigation menu items
    - User-specific data
    - Feature flags

Example usage in template:
    {{ site_name }}
    {% for category in all_categories %}...{% endfor %}

=============================================================================
"""

from apps.blog.models import Category, Tag


def site_settings(request):
    """
    Returns site-wide settings available in all templates.

    Usage in template:
        {{ site_name }}
        {{ site_description }}
        {% for category in all_categories %}
            {{ category.name }}
        {% endfor %}
    """
    return {
        # Site information
        'site_name': 'Django Blog CMS',
        'site_description': 'A powerful blogging platform built with Django',
        'site_author': 'Your Name',

        # Footer information
        'site_year': '2024',

        # Navigation data - available in all templates
        # Only show categories and tags that have published posts
        'all_categories': Category.objects.all()[:10],
        'all_tags': Tag.objects.all()[:20],

        # Social media links (customize these)
        'social_links': {
            'twitter': 'https://twitter.com/yourusername',
            'github': 'https://github.com/yourusername',
            'linkedin': 'https://linkedin.com/in/yourusername',
        },
    }
