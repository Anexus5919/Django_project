/*
=============================================================================
Blog CMS Main JavaScript
=============================================================================

This file contains custom JavaScript for the blog.
Bootstrap 5 handles most interactive components; we add custom behavior.

Sections:
    1. DOM Ready Handler
    2. Search Enhancement
    3. Comment System
    4. Form Validation
    5. Image Preview
    6. Scroll to Top
    7. Utility Functions

=============================================================================
*/

/**
 * Wait for DOM to be fully loaded before running scripts.
 * This is the standard way to ensure all elements exist before manipulating them.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Blog CMS JavaScript loaded');

    // Initialize all components
    initSearchEnhancement();
    initCommentSystem();
    initImagePreview();
    initScrollToTop();
    initAutoHideAlerts();
    initCharacterCounters();
});


/* ==========================================================================
   2. SEARCH ENHANCEMENT
   ========================================================================== */

/**
 * Enhance the search functionality with keyboard shortcuts
 * and auto-focus features.
 */
function initSearchEnhancement() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[name="q"]');

    searchInputs.forEach(input => {
        // Clear button functionality
        input.addEventListener('input', function() {
            // Could add a clear button here
        });

        // Prevent form submission if empty
        const form = input.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (input.value.trim() === '') {
                    e.preventDefault();
                    input.focus();
                }
            });
        }
    });

    // Keyboard shortcut: Press '/' to focus search
    document.addEventListener('keydown', function(e) {
        // Only if not already in an input
        if (e.key === '/' && !isInputFocused()) {
            e.preventDefault();
            const mainSearch = document.querySelector('.navbar input[type="search"]');
            if (mainSearch) {
                mainSearch.focus();
            }
        }
    });
}


/* ==========================================================================
   3. COMMENT SYSTEM
   ========================================================================== */

/**
 * Initialize comment system features like
 * reply toggles and character limits.
 */
function initCommentSystem() {
    // Toggle reply forms
    const replyButtons = document.querySelectorAll('.reply-btn');

    replyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById('reply-form-' + commentId);

            if (replyForm) {
                // Toggle visibility
                replyForm.classList.toggle('d-none');

                // Focus input when shown
                if (!replyForm.classList.contains('d-none')) {
                    const input = replyForm.querySelector('input[name="content"]');
                    if (input) input.focus();
                }
            }
        });
    });

    // Character counter for comment textarea
    const commentTextareas = document.querySelectorAll('textarea[name="content"]');

    commentTextareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength') || 1000;

        // Create counter element if not exists
        if (!textarea.nextElementSibling?.classList.contains('char-counter')) {
            const counter = document.createElement('small');
            counter.className = 'char-counter text-muted d-block text-end';
            counter.textContent = `0/${maxLength}`;
            textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        }

        textarea.addEventListener('input', function() {
            const counter = this.nextElementSibling;
            if (counter?.classList.contains('char-counter')) {
                const current = this.value.length;
                counter.textContent = `${current}/${maxLength}`;

                // Change color when near limit
                if (current > maxLength * 0.9) {
                    counter.classList.add('text-danger');
                } else {
                    counter.classList.remove('text-danger');
                }
            }
        });
    });
}


/* ==========================================================================
   4. IMAGE PREVIEW
   ========================================================================== */

/**
 * Show image preview when user selects an image file.
 * Works for featured images and avatars.
 */
function initImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');

    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];

            if (file && file.type.startsWith('image/')) {
                // Find or create preview element
                let preview = this.parentNode.querySelector('.image-preview');

                if (!preview) {
                    preview = document.createElement('div');
                    preview.className = 'image-preview mt-2';
                    this.parentNode.appendChild(preview);
                }

                // Create image element
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.className = 'img-thumbnail';
                img.style.maxHeight = '200px';
                img.onload = function() {
                    URL.revokeObjectURL(this.src);
                };

                preview.innerHTML = '';
                preview.appendChild(img);

                // Add file name
                const fileName = document.createElement('small');
                fileName.className = 'd-block text-muted mt-1';
                fileName.textContent = file.name;
                preview.appendChild(fileName);
            }
        });
    });
}


/* ==========================================================================
   5. SCROLL TO TOP
   ========================================================================== */

/**
 * Add a "scroll to top" button that appears when user scrolls down.
 */
function initScrollToTop() {
    // Create button
    const button = document.createElement('button');
    button.innerHTML = '<i class="bi bi-arrow-up"></i>';
    button.className = 'btn btn-primary btn-scroll-top';
    button.setAttribute('aria-label', 'Scroll to top');
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: none;
        z-index: 1000;
        opacity: 0.8;
        transition: opacity 0.2s;
    `;

    document.body.appendChild(button);

    // Show/hide based on scroll position
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }
    });

    // Scroll to top when clicked
    button.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Hover effect
    button.addEventListener('mouseenter', function() {
        this.style.opacity = '1';
    });
    button.addEventListener('mouseleave', function() {
        this.style.opacity = '0.8';
    });
}


/* ==========================================================================
   6. AUTO-HIDE ALERTS
   ========================================================================== */

/**
 * Automatically hide Bootstrap alerts after a delay.
 */
function initAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');

    alerts.forEach(alert => {
        // Auto-hide after 5 seconds
        setTimeout(() => {
            // Use Bootstrap's alert close method if available
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            } else {
                alert.style.transition = 'opacity 0.3s';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}


/* ==========================================================================
   7. CHARACTER COUNTERS
   ========================================================================== */

/**
 * Add character counters to inputs with maxlength attribute.
 */
function initCharacterCounters() {
    // Meta description counter is handled in the template
    // This can be extended for other fields

    const metaDesc = document.getElementById('id_meta_description');
    const charCount = document.getElementById('meta-char-count');

    if (metaDesc && charCount) {
        charCount.textContent = metaDesc.value.length;
        metaDesc.addEventListener('input', function() {
            charCount.textContent = this.value.length;
        });
    }
}


/* ==========================================================================
   8. UTILITY FUNCTIONS
   ========================================================================== */

/**
 * Check if user is currently focused on an input element.
 * @returns {boolean}
 */
function isInputFocused() {
    const active = document.activeElement;
    return active && (
        active.tagName === 'INPUT' ||
        active.tagName === 'TEXTAREA' ||
        active.tagName === 'SELECT' ||
        active.isContentEditable
    );
}

/**
 * Format a date to relative time (e.g., "2 hours ago").
 * @param {Date|string} date
 * @returns {string}
 */
function timeAgo(date) {
    const now = new Date();
    const past = new Date(date);
    const diffMs = now - past;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return past.toLocaleDateString();
}

/**
 * Debounce function to limit how often a function can fire.
 * @param {Function} func
 * @param {number} wait
 * @returns {Function}
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Copy text to clipboard.
 * @param {string} text
 * @returns {Promise<void>}
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        console.log('Copied to clipboard');
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}
