"""
=============================================================================
Django Settings for Blog CMS Project
=============================================================================

This is the central configuration file for your Django project.
Every setting here affects how your application behaves.

Django settings are organized into sections:
    1. Core Settings (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
    2. Application Definition (INSTALLED_APPS, MIDDLEWARE)
    3. URL & Template Configuration
    4. Database Configuration
    5. Authentication Settings
    6. Static & Media Files
    7. Third-Party App Settings

=============================================================================
"""

import os
from pathlib import Path

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

# BASE_DIR is the root directory of your project
# Path(__file__) = this settings.py file
# .resolve() = get absolute path
# .parent.parent = go up two directories (from blog_cms/ to Django_project/)
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

# SECRET_KEY is used for cryptographic signing
# IMPORTANT: In production, keep this secret and load from environment variable!
# Generate a new one at: https://djecrety.ir/
SECRET_KEY = 'django-insecure-change-this-in-production-abc123xyz789'

# DEBUG mode shows detailed error pages
# Set to False in production for security!
DEBUG = True

# List of domain names that can serve this site
# Add your domain here in production (e.g., ['yourblog.com', 'www.yourblog.com'])
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

# INSTALLED_APPS lists all Django apps that are enabled
# Order matters! Django processes them from top to bottom

INSTALLED_APPS = [
    # ----- Django Built-in Apps -----
    'django.contrib.admin',          # Admin panel (yoursite.com/admin/)
    'django.contrib.auth',           # User authentication system
    'django.contrib.contenttypes',   # Framework for content types
    'django.contrib.sessions',       # Session management
    'django.contrib.messages',       # Flash messages (success, error alerts)
    'django.contrib.staticfiles',    # Serving static files (CSS, JS, images)
    'django.contrib.sites',          # Multi-site support (required by allauth)
    'django.contrib.humanize',       # Template filters (e.g., naturaltime)

    # ----- Third-Party Apps -----
    'allauth',                        # Core authentication
    'allauth.account',                # Account management (login, register)
    'allauth.socialaccount',          # Social auth support (optional)
    'crispy_forms',                   # Better form rendering
    'crispy_bootstrap5',              # Bootstrap 5 for crispy forms
    'django_ckeditor_5',              # Rich text editor

    # ----- Our Custom Apps -----
    'apps.blog',                      # Blog functionality
    'apps.accounts',                  # User profiles
    'apps.core',                      # Shared utilities
]

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================

# Middleware are "hooks" that process requests/responses
# They run in order for requests (top to bottom)
# And reverse order for responses (bottom to top)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',       # Security enhancements
    'django.contrib.sessions.middleware.SessionMiddleware', # Session handling
    'django.middleware.common.CommonMiddleware',           # URL normalization
    'django.middleware.csrf.CsrfViewMiddleware',           # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # User auth
    'django.contrib.messages.middleware.MessageMiddleware', # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Clickjack protection
    'allauth.account.middleware.AccountMiddleware',        # Allauth middleware
]

# =============================================================================
# URL CONFIGURATION
# =============================================================================

# Points to the main URL configuration file
ROOT_URLCONF = 'blog_cms.urls'

# =============================================================================
# TEMPLATE CONFIGURATION
# =============================================================================

# Templates are HTML files that Django renders with dynamic data

TEMPLATES = [
    {
        # Use Django's built-in template engine
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Where to look for templates (in addition to app templates)
        'DIRS': [BASE_DIR / 'templates'],

        # Automatically look for templates/ folder inside each app
        'APP_DIRS': True,

        # Template context processors add variables to every template
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',      # Adds 'debug' variable
                'django.template.context_processors.request',    # Adds 'request' object
                'django.contrib.auth.context_processors.auth',   # Adds 'user' object
                'django.contrib.messages.context_processors.messages',  # Adds 'messages'
                'apps.core.context_processors.site_settings',    # Our custom processor
            ],
        },
    },
]

# =============================================================================
# WSGI CONFIGURATION
# =============================================================================

# WSGI (Web Server Gateway Interface) is how Python web apps communicate
# with web servers like Nginx or Apache
WSGI_APPLICATION = 'blog_cms.wsgi.application'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# SQLite is perfect for development - no setup required!
# For production, switch to PostgreSQL:
# 'ENGINE': 'django.db.backends.postgresql',
# 'NAME': 'your_db_name',
# 'USER': 'your_db_user',
# 'PASSWORD': 'your_db_password',
# 'HOST': 'localhost',
# 'PORT': '5432',

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Database backend
        'NAME': BASE_DIR / 'db.sqlite3',         # Database file location
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

# These validators ensure users create strong passwords

AUTH_PASSWORD_VALIDATORS = [
    {
        # Prevents password similar to user attributes (username, email)
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Requires minimum password length
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # Prevents common passwords like "password123"
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Prevents entirely numeric passwords like "12345678"
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'      # Default language
TIME_ZONE = 'UTC'            # Default timezone (change to your local timezone)
USE_I18N = True              # Enable translation system
USE_TZ = True                # Enable timezone-aware datetimes

# =============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# =============================================================================

# URL prefix for static files
STATIC_URL = '/static/'

# Additional directories to look for static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Where to collect static files for production (python manage.py collectstatic)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# =============================================================================
# MEDIA FILES (User Uploads)
# =============================================================================

# URL prefix for user-uploaded files
MEDIA_URL = '/media/'

# Directory where uploaded files are stored
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# =============================================================================

# BigAutoField uses 64-bit integer for IDs (can handle billions of records)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# DJANGO-ALLAUTH CONFIGURATION
# =============================================================================

# Required by allauth for multi-site support
SITE_ID = 1

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth
]

# Allauth settings (updated for django-allauth 65.x)
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # Auto-login after email verification
ACCOUNT_LOGIN_METHODS = {'email'}           # Login with email (not username)
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True                  # Each email can only be used once
ACCOUNT_EMAIL_VERIFICATION = 'optional'      # Options: 'mandatory', 'optional', 'none'
ACCOUNT_SESSION_REMEMBER = True              # Remember me checkbox
ACCOUNT_LOGOUT_REDIRECT_URL = '/'            # Redirect after logout

# Redirect URLs after login/logout
LOGIN_REDIRECT_URL = '/'                     # Where to go after login
LOGIN_URL = '/accounts/login/'               # Where to redirect non-logged users

# Email configuration (for development - prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production, use real SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'

# =============================================================================
# CRISPY FORMS CONFIGURATION
# =============================================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# =============================================================================
# CKEDITOR 5 CONFIGURATION
# =============================================================================

# Custom CKEditor configurations
customColorPalette = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'link', 'bulletedList', 'numberedList', 'blockQuote', '|',
            'imageUpload', 'insertTable', 'mediaEmbed', '|',
            'undo', 'redo', '|',
            'fontSize', 'fontColor', 'fontBackgroundColor', '|',
            'codeBlock', 'sourceEditing',
        ],
        'image': {
            'toolbar': [
                'imageTextAlternative', 'imageTitle', '|',
                'imageStyle:alignLeft', 'imageStyle:full', 'imageStyle:alignRight',
            ],
            'styles': ['full', 'alignLeft', 'alignRight'],
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties',
            ],
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'},
            ]
        },
        'fontColor': {'colors': customColorPalette},
        'fontBackgroundColor': {'colors': customColorPalette},
    },
    'minimal': {
        'toolbar': ['bold', 'italic', 'link', 'bulletedList', 'numberedList'],
    },
}

# Where CKEditor uploads files
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "authenticated"
