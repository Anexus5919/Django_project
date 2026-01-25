"""
=============================================================================
Blog Forms - User Input Handling
=============================================================================

Forms in Django:
    Forms handle user input validation and HTML generation.
    They're the bridge between HTML forms and Python/database.

Two types of forms:
    1. Form - Manual field definitions
    2. ModelForm - Automatically generated from a model

Benefits of Django forms:
    - Automatic HTML generation
    - Built-in validation
    - CSRF protection
    - Error handling
    - Data cleaning/sanitization

Form flow:
    1. User submits form
    2. Django validates data
    3. If valid: form.cleaned_data contains sanitized data
    4. If invalid: form.errors contains error messages

=============================================================================
"""

from django import forms
from django.utils.text import slugify
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Div, HTML

from .models import Post, Comment, Category, Tag


class PostForm(forms.ModelForm):
    """
    Form for creating and editing blog posts.

    ModelForm automatically creates fields from the Post model.
    We can customize which fields to include and their widgets.
    """

    # Custom field for tags (comma-separated input)
    tags_input = forms.CharField(
        required=False,
        label='Tags',
        help_text='Enter tags separated by commas (e.g., "python, django, tutorial")',
        widget=forms.TextInput(attrs={
            'placeholder': 'python, django, web development',
            'class': 'form-control'
        })
    )

    class Meta:
        """
        Meta class configures the ModelForm.
        """
        # Which model this form is for
        model = Post

        # Which fields to include in the form
        fields = [
            'title',
            'content',
            'excerpt',
            'featured_image',
            'category',
            'status',
            'allow_comments',
            'meta_description',
        ]

        # Custom widgets for better appearance
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your post title'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief summary of your post (optional - auto-generated if empty)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'SEO description (max 160 characters)'
            }),
        }

        # Custom labels
        labels = {
            'content': 'Post Content',
            'featured_image': 'Featured Image',
            'allow_comments': 'Allow Comments',
            'meta_description': 'SEO Description',
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with crispy-forms helper.
        """
        super().__init__(*args, **kwargs)

        # If editing existing post, populate tags_input
        if self.instance.pk:
            self.fields['tags_input'].initial = ', '.join(
                tag.name for tag in self.instance.tags.all()
            )

        # Crispy forms helper for styling
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'  # Required for file uploads

        self.helper.layout = Layout(
            'title',
            'content',
            Row(
                Column('category', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            'tags_input',
            'excerpt',
            'featured_image',
            'meta_description',
            'allow_comments',
            Div(
                Submit('submit', 'Publish Post', css_class='btn btn-primary me-2'),
                HTML('<a href="{% url \'blog:home\' %}" class="btn btn-secondary">Cancel</a>'),
                css_class='mt-3'
            )
        )

    def clean_title(self):
        """
        Custom validation for the title field.
        clean_<fieldname> methods are called automatically.
        """
        title = self.cleaned_data.get('title')

        # Ensure title isn't too short
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters long.")

        return title

    def save(self, commit=True):
        """
        Override save to handle tags.
        """
        # Save the post first (don't commit yet if we need to add tags)
        post = super().save(commit=False)

        if commit:
            post.save()

            # Handle tags
            tags_input = self.cleaned_data.get('tags_input', '')
            if tags_input:
                # Clear existing tags
                post.tags.clear()

                # Add new tags
                tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
                for tag_name in tag_names:
                    # Get or create the tag
                    tag, created = Tag.objects.get_or_create(
                        name__iexact=tag_name,
                        defaults={'name': tag_name, 'slug': slugify(tag_name)}
                    )
                    post.tags.add(tag)

            # Save many-to-many relationships
            self.save_m2m()

        return post


class CommentForm(forms.ModelForm):
    """
    Form for adding comments to posts.
    Simple form with just the content field.
    """

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...',
                'maxlength': 1000,
            })
        }
        labels = {
            'content': ''  # Hide label
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'content',
            Submit('submit', 'Post Comment', css_class='btn btn-primary mt-2')
        )


class ReplyForm(forms.ModelForm):
    """
    Form for replying to comments.
    Similar to CommentForm but smaller.
    """

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Write your reply...',
                'maxlength': 1000,
            })
        }


class SearchForm(forms.Form):
    """
    Simple search form.
    Not a ModelForm because search doesn't save data.
    """

    q = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...',
            'type': 'search',
        })
    )


class CategoryForm(forms.ModelForm):
    """
    Form for creating/editing categories (admin use).
    """

    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
