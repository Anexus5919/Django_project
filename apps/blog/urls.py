"""
=============================================================================
Blog URL Configuration
=============================================================================

This file maps URLs to views for the blog app.

URL patterns:
    - '' (home) -> List of all posts
    - 'blog/' -> Blog listing page
    - 'blog/<slug>/' -> Single post detail
    - 'blog/create/' -> Create new post
    - 'blog/<slug>/edit/' -> Edit post
    - 'blog/<slug>/delete/' -> Delete post
    - 'category/<slug>/' -> Posts in category
    - 'tag/<slug>/' -> Posts with tag
    - 'search/' -> Search results

Path converters:
    - <slug:slug> -> Matches URL-friendly strings (letters, numbers, hyphens)
    - <int:pk> -> Matches integers (primary key)
    - <str:name> -> Matches any non-empty string

The 'name' parameter allows reverse URL lookup:
    - In views: reverse('blog:post_detail', kwargs={'slug': 'my-post'})
    - In templates: {% url 'blog:post_detail' slug='my-post' %}

app_name creates a namespace to avoid URL name conflicts between apps.

=============================================================================
"""

from django.urls import path
from . import views

# Namespace for this app's URLs
# Usage: {% url 'blog:post_list' %} instead of {% url 'post_list' %}
app_name = 'blog'

urlpatterns = [
    # ----- Home Page -----
    # URL: /
    path(
        '',
        views.HomeView.as_view(),
        name='home'
    ),

    # ----- Post List -----
    # URL: /blog/
    path(
        'blog/',
        views.PostListView.as_view(),
        name='post_list'
    ),

    # ----- Create Post -----
    # URL: /blog/create/
    # Note: This must come BEFORE post_detail to avoid 'create' being treated as a slug
    path(
        'blog/create/',
        views.PostCreateView.as_view(),
        name='post_create'
    ),

    # ----- Post Detail -----
    # URL: /blog/my-first-post/
    path(
        'blog/<slug:slug>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),

    # ----- Edit Post -----
    # URL: /blog/my-first-post/edit/
    path(
        'blog/<slug:slug>/edit/',
        views.PostUpdateView.as_view(),
        name='post_update'
    ),

    # ----- Delete Post -----
    # URL: /blog/my-first-post/delete/
    path(
        'blog/<slug:slug>/delete/',
        views.PostDeleteView.as_view(),
        name='post_delete'
    ),

    # ----- Category Detail -----
    # URL: /category/technology/
    path(
        'category/<slug:slug>/',
        views.CategoryDetailView.as_view(),
        name='category_detail'
    ),

    # ----- Tag Detail -----
    # URL: /tag/python/
    path(
        'tag/<slug:slug>/',
        views.TagDetailView.as_view(),
        name='tag_detail'
    ),

    # ----- Search -----
    # URL: /search/?q=django
    path(
        'search/',
        views.SearchView.as_view(),
        name='search'
    ),

    # ----- Add Comment -----
    # URL: /blog/my-first-post/comment/
    path(
        'blog/<slug:slug>/comment/',
        views.AddCommentView.as_view(),
        name='add_comment'
    ),

    # ----- Delete Comment -----
    # URL: /comment/5/delete/
    path(
        'comment/<int:pk>/delete/',
        views.DeleteCommentView.as_view(),
        name='delete_comment'
    ),

    # ----- Author Posts -----
    # URL: /author/username/
    path(
        'author/<str:username>/',
        views.AuthorPostsView.as_view(),
        name='author_posts'
    ),
]
