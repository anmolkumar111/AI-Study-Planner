/**
 * AIStudyPlanner — Main JavaScript
 * ==================================
 * Handles:
 * 1. Progress bar animations
 * 2. Exam countdown timers
 * 3. Topic completion AJAX toggle
 * 4. Form validation
 * 5. Alert auto-dismiss
 * 6. Dashboard interactivity
 *
 * Uses vanilla JavaScript only — no frameworks needed!
 */

/* ─────────────────────────────────────────────────────────
   1. INITIALIZATION — Run after page loads
   ───────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
    // Run all init functions
    initProgressBars();
    initAlertDismiss();
    initTopicToggles();
    initPlanToggles();
    initFormValidation();
    initCountdownTimers();
    highlightActiveNav();
    initAnimations();
});


/* ─────────────────────────────────────────────────────────
   2. PROGRESS BAR ANIMATION
   Animates progress bars from 0% to their target value.
   The 'data-progress' attribute stores the target %.
   ───────────────────────────────────────────────────────── */
function initProgressBars() {
    // Select all progress bar fill elements
    const bars = document.querySelectorAll('.progress-bar-fill');

    bars.forEach(function (bar) {
        // Read the target value from HTML attribute
        const targetValue = parseInt(bar.getAttribute('data-progress')) || 0;

        // Small delay before animation starts (looks nicer)
        setTimeout(function () {
            bar.style.width = targetValue + '%';
        }, 300);
    });
}


/* ─────────────────────────────────────────────────────────
   3. ALERT / MESSAGE AUTO-DISMISS
   Flash messages disappear after 5 seconds automatically.
   Users can also click ✕ to close them.
   ───────────────────────────────────────────────────────── */
function initAlertDismiss() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function (alert) {
        // Auto-dismiss after 5 seconds
        const timer = setTimeout(function () {
            dismissAlert(alert);
        }, 5000);

        // Close button click handler
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                clearTimeout(timer); // Cancel auto-dismiss
                dismissAlert(alert);
            });
        }
    });
}

function dismissAlert(alert) {
    // Fade out animation before removing from DOM
    alert.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(20px)';
    setTimeout(function () {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 300);
}


/* ─────────────────────────────────────────────────────────
   4. TOPIC COMPLETION TOGGLE (AJAX)
   When user clicks a topic checkbox:
   - Send AJAX request to /topics/<id>/toggle/
   - Update the UI without page reload
   - Update progress bar in real time
   ───────────────────────────────────────────────────────── */
function initTopicToggles() {
    // Find all topic checkboxes with the data-toggle attribute
    const checkboxes = document.querySelectorAll('.topic-checkbox[data-topic-id]');

    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            const topicId = this.getAttribute('data-topic-id');
            const csrfToken = getCsrfToken();

            // Show loading state
            this.disabled = true;
            const topicItem = this.closest('.topic-item');

            // Make AJAX POST request to toggle endpoint
            fetch('/topics/' + topicId + '/toggle/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.success) {
                    // Update the topic row visual state
                    if (data.is_completed) {
                        topicItem.classList.add('completed');
                    } else {
                        topicItem.classList.remove('completed');
                    }

                    // Update progress bar if it exists on this page
                    const progressBar = document.querySelector('.progress-bar-fill[data-subject-progress]');
                    if (progressBar) {
                        progressBar.style.width = data.progress + '%';
                        // Update the percentage text display
                        const progressText = document.querySelector('.progress-percent-text');
                        if (progressText) {
                            progressText.textContent = data.progress + '%';
                        }
                    }

                    // Re-enable checkbox
                    checkbox.disabled = false;
                    checkbox.checked = data.is_completed;

                    // Show a brief success indicator
                    showToast(data.is_completed ? '✓ Topic completed!' : 'Topic marked incomplete', 'success');
                }
            })
            .catch(function (error) {
                console.error('Error toggling topic:', error);
                // Revert checked state on error
                checkbox.checked = !checkbox.checked;
                checkbox.disabled = false;
                showToast('Error updating topic. Please try again.', 'error');
            });
        });
    });
}


/* ─────────────────────────────────────────────────────────
   5. STUDY PLAN TASK TOGGLE (AJAX)
   Toggle study plan tasks as done/undone from dashboard
   ───────────────────────────────────────────────────────── */
function initPlanToggles() {
    const planCheckboxes = document.querySelectorAll('.plan-checkbox[data-plan-id]');

    planCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            const planId = this.getAttribute('data-plan-id');
            const csrfToken = getCsrfToken();
            const planItem = this.closest('.plan-item');

            this.disabled = true;

            fetch('/plans/' + planId + '/toggle/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.success) {
                    checkbox.disabled = false;
                    checkbox.checked = data.is_done;

                    // Strike through the task if done
                    const planTopic = planItem.querySelector('.plan-topic');
                    if (planTopic) {
                        if (data.is_done) {
                            planTopic.style.textDecoration = 'line-through';
                            planTopic.style.opacity = '0.6';
                        } else {
                            planTopic.style.textDecoration = 'none';
                            planTopic.style.opacity = '1';
                        }
                    }
                }
            })
            .catch(function (error) {
                console.error('Error toggling plan task:', error);
                checkbox.disabled = false;
                checkbox.checked = !checkbox.checked;
            });
        });
    });
}


/* ─────────────────────────────────────────────────────────
   6. FORM VALIDATION
   Client-side validation before form submission.
   This catches simple errors without a server round-trip.
   ───────────────────────────────────────────────────────── */
function initFormValidation() {
    // Subject form validation
    const subjectForm = document.querySelector('#subject-form');
    if (subjectForm) {
        subjectForm.addEventListener('submit', function (e) {
            const nameField = this.querySelector('[name="name"]');
            if (nameField && nameField.value.trim() === '') {
                e.preventDefault(); // Stop form submission
                showFieldError(nameField, 'Subject name cannot be empty.');
            }
        });
    }

    // Topic form validation
    const topicForm = document.querySelector('#topic-form');
    if (topicForm) {
        topicForm.addEventListener('submit', function (e) {
            const nameField = this.querySelector('[name="name"]');
            const hoursField = this.querySelector('[name="estimated_hours"]');
            let valid = true;

            if (nameField && nameField.value.trim() === '') {
                e.preventDefault();
                showFieldError(nameField, 'Topic name cannot be empty.');
                valid = false;
            }

            if (hoursField && parseFloat(hoursField.value) <= 0) {
                e.preventDefault();
                showFieldError(hoursField, 'Hours must be greater than 0.');
                valid = false;
            }

            return valid;
        });
    }

    // Exam form — validate date is not in past
    const examForm = document.querySelector('#exam-form');
    if (examForm) {
        examForm.addEventListener('submit', function (e) {
            const dateField = this.querySelector('[name="exam_date"]');
            if (dateField && dateField.value) {
                const selectedDate = new Date(dateField.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);

                if (selectedDate < today) {
                    e.preventDefault();
                    showFieldError(dateField, 'Exam date cannot be in the past!');
                }
            }
        });
    }

    // Add real-time clearing of field errors on input
    document.querySelectorAll('.form-control').forEach(function (field) {
        field.addEventListener('input', function () {
            const errorEl = this.parentElement.querySelector('.form-error.js-error');
            if (errorEl) {
                errorEl.remove();
                this.style.borderColor = '';
            }
        });
    });
}

function showFieldError(field, message) {
    // Remove any existing JS-generated error
    const existingError = field.parentElement.querySelector('.form-error.js-error');
    if (existingError) existingError.remove();

    // Add red border to the field
    field.style.borderColor = 'var(--accent-red)';
    field.focus();

    // Insert error message after the field
    const errorEl = document.createElement('div');
    errorEl.className = 'form-error js-error';
    errorEl.innerHTML = '⚠ ' + message;
    field.insertAdjacentElement('afterend', errorEl);
}


/* ─────────────────────────────────────────────────────────
   7. COUNTDOWN TIMERS
   Creates a live countdown to exam dates.
   Updates every second for "today" exams.
   ───────────────────────────────────────────────────────── */
function initCountdownTimers() {
    const countdownEls = document.querySelectorAll('[data-exam-date]');

    countdownEls.forEach(function (el) {
        const examDateStr = el.getAttribute('data-exam-date');
        if (!examDateStr) return;

        // Parse the exam date (format: YYYY-MM-DD)
        const examDate = new Date(examDateStr + 'T00:00:00');

        function updateCountdown() {
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const examDay = new Date(examDate.getFullYear(), examDate.getMonth(), examDate.getDate());
            const diffMs = examDay - today;
            const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

            if (diffDays < 0) {
                el.textContent = 'Exam passed';
                el.style.color = 'var(--text-muted)';
            } else if (diffDays === 0) {
                el.textContent = '🎯 TODAY!';
                el.style.color = 'var(--accent-red)';
                el.style.animation = 'pulse-glow 1.5s ease infinite';
            } else {
                el.textContent = diffDays;
                // Color code by urgency
                if (diffDays <= 3) {
                    el.style.color = 'var(--accent-red)';
                } else if (diffDays <= 7) {
                    el.style.color = 'var(--accent-orange)';
                } else if (diffDays <= 14) {
                    el.style.color = 'var(--accent-yellow)';
                } else {
                    el.style.color = 'var(--accent-purple)';
                }
            }
        }

        // Run immediately and then every hour
        updateCountdown();
        setInterval(updateCountdown, 3600000);
    });
}


/* ─────────────────────────────────────────────────────────
   8. ACTIVE NAVIGATION HIGHLIGHT
   Adds 'active' class to the current nav link
   ───────────────────────────────────────────────────────── */
function highlightActiveNav() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(function (item) {
        const href = item.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            item.classList.add('active');
        } else if (href === '/dashboard/' && currentPath === '/dashboard/') {
            item.classList.add('active');
        }
    });
}


/* ─────────────────────────────────────────────────────────
   9. SCROLL ANIMATIONS
   Adds animation classes when elements enter the viewport
   ───────────────────────────────────────────────────────── */
function initAnimations() {
    // Intersection Observer for scroll animations
    if (!window.IntersectionObserver) return; // Browser support check

    const observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1 }
    );

    // Observe stat cards and panels
    document.querySelectorAll('.stat-card, .panel, .subject-card').forEach(function (el) {
        observer.observe(el);
    });
}


/* ─────────────────────────────────────────────────────────
   10. UTILITY FUNCTIONS
   ───────────────────────────────────────────────────────── */

/**
 * Get CSRF token from cookie — required for Django AJAX POST requests.
 * Django uses CSRF tokens to prevent cross-site request forgery attacks.
 */
function getCsrfToken() {
    const name = 'csrftoken';
    const cookieValue = document.cookie
        .split('; ')
        .find(function (row) { return row.startsWith(name + '='); });

    return cookieValue ? cookieValue.split('=')[1] : '';
}

/**
 * Show a toast notification at top-right corner.
 * @param {string} message - Text to display
 * @param {string} type - 'success', 'error', or 'info'
 */
function showToast(message, type) {
    type = type || 'info';

    // Get or create messages container
    let container = document.querySelector('.messages-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'messages-container';
        document.body.appendChild(container);
    }

    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '⚠',
    };

    const toast = document.createElement('div');
    toast.className = 'alert alert-' + type;
    toast.innerHTML = '<span>' + icons[type] + '</span> ' + message +
        '<button class="alert-close" aria-label="Close">✕</button>';

    container.appendChild(toast);

    // Auto dismiss after 4 seconds
    setTimeout(function () {
        dismissAlert(toast);
    }, 4000);

    // Close button
    const closeBtn = toast.querySelector('.alert-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            dismissAlert(toast);
        });
    }
}

/**
 * Confirm before deleting (extra safety check in browser)
 * @param {string} itemName - Name of item to delete
 * @returns {boolean} - Whether user confirmed
 */
function confirmDelete(itemName) {
    return confirm('Are you sure you want to delete "' + itemName + '"?\nThis cannot be undone.');
}


/* ─────────────────────────────────────────────────────────
   11. REGISTER FORM — Password strength indicator
   ───────────────────────────────────────────────────────── */
(function () {
    const passwordField = document.querySelector('#id_password1');
    const confirmField = document.querySelector('#id_password2');

    if (!passwordField) return;

    // Create strength indicator element
    const strengthEl = document.createElement('div');
    strengthEl.className = 'password-strength';
    strengthEl.style.cssText = 'margin-top:6px; font-size:0.76rem;';
    passwordField.insertAdjacentElement('afterend', strengthEl);

    passwordField.addEventListener('input', function () {
        const val = this.value;
        const strength = getPasswordStrength(val);

        const colors   = ['', 'var(--accent-red)', 'var(--accent-orange)', 'var(--accent-yellow)', 'var(--accent-green)'];
        const labels   = ['', 'Weak', 'Fair', 'Good', 'Strong'];

        if (val.length === 0) {
            strengthEl.textContent = '';
        } else {
            strengthEl.innerHTML =
                '<span style="color:' + colors[strength] + '">● ' + labels[strength] + ' password</span>';
        }
    });

    // Check if passwords match in real time
    if (confirmField) {
        confirmField.addEventListener('input', function () {
            if (this.value && this.value !== passwordField.value) {
                this.style.borderColor = 'var(--accent-red)';
            } else if (this.value) {
                this.style.borderColor = 'var(--accent-green)';
            } else {
                this.style.borderColor = '';
            }
        });
    }

    function getPasswordStrength(password) {
        let score = 0;
        if (password.length >= 8)  score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;
        return score;
    }
})();
