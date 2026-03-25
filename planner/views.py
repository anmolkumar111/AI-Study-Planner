"""
AIStudyPlanner - Views
=======================
Views are Python functions/classes that handle HTTP requests
and return HTML responses.

Each view = one page in the web app.

Flow: URL → View → Template (with data) → HTML page shown to user
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required  # Protect pages
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta, datetime
from collections import defaultdict

from .models import Subject, Topic, Exam, StudyPlan
from .forms import RegisterForm, SubjectForm, TopicForm, ExamForm
from .timetable import generate_study_plan, get_todays_plan, get_nearest_exam


# ═══════════════════════════════════════════════════
# AUTH VIEWS — Signup, Login, Logout
# ═══════════════════════════════════════════════════

def register_view(request):
    """
    Handle student registration.
    GET  → Show registration form
    POST → Validate & create account → redirect to login
    """
    # If already logged in, go to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created! Welcome, {user.username}. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """
    Handle student login.
    GET  → Show login form
    POST → Authenticate → redirect to dashboard
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
        else:
            # Django's built-in auth function
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                # Go to the page they were trying to visit, or dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html', {})


def logout_view(request):
    """Log out the user and redirect to login page."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


# ═══════════════════════════════════════════════════
# DASHBOARD VIEW — Main page after login
# ═══════════════════════════════════════════════════

@login_required
def dashboard_view(request):
    """
    Main dashboard showing:
    - Stats (subjects, topics, progress)
    - Nearest exam countdown
    - Today's study plan
    """
    user = request.user

    # ── Gather Statistics ──────────────────────────
    subjects = Subject.objects.filter(user=user)

    # ── Auto-Populate Sample Data for Demo ──────────────────
    if not subjects.exists():
        # Create Sample Subjects
        cs = Subject.objects.create(user=user, name="Computer Science", description="Algorithms and databases.")
        math = Subject.objects.create(user=user, name="Mathematics", description="Calculus and Linear Algebra.")
        physics = Subject.objects.create(user=user, name="Physics", description="Quantum Mechanics and Electromagnetism.")

        # Create Topics for Computer Science
        Topic.objects.create(subject=cs, name="Data Structures", difficulty='hard', estimated_hours=10)
        Topic.objects.create(subject=cs, name="SQL Queries", difficulty='easy', estimated_hours=3)
        Topic.objects.create(subject=cs, name="Django Fundamentals", difficulty='medium', estimated_hours=8)

        # Create Topics for Mathematics
        Topic.objects.create(subject=math, name="Integrals & Derivatives", difficulty='hard', estimated_hours=15)
        Topic.objects.create(subject=math, name="Probability Theory", difficulty='medium', estimated_hours=7)

        # Create Topics for Physics
        Topic.objects.create(subject=physics, name="Schrodinger Equation", difficulty='hard', estimated_hours=20)
        Topic.objects.create(subject=physics, name="Newtonian Mechanics", difficulty='easy', estimated_hours=4)

        # Create Exams
        today = timezone.now().date()
        Exam.objects.create(user=user, subject=physics, exam_date=today + timedelta(days=4), notes="Bring calculator!")
        Exam.objects.create(user=user, subject=cs, exam_date=today + timedelta(days=10))
        Exam.objects.create(user=user, subject=math, exam_date=today + timedelta(days=15))

        # Re-fetch subjects after creation
        subjects = Subject.objects.filter(user=user)
        messages.success(request, "🚀 Demo mode active: Sample study data has been automatically loaded!")

    all_topics = Topic.objects.filter(subject__user=user)
    total_topics = all_topics.count()
    completed_topics = all_topics.filter(is_completed=True).count()
    pending_topics = total_topics - completed_topics

    # Calculate overall progress percentage
    progress_percent = 0
    if total_topics > 0:
        progress_percent = round((completed_topics / total_topics) * 100)

    # ── Exam Information ───────────────────────────
    nearest_exam = get_nearest_exam(user)
    all_exams = Exam.objects.filter(user=user, exam_date__gte=timezone.now().date()).order_by('exam_date')

    # ── Today's Study Plan ─────────────────────────
    todays_plan = get_todays_plan(user)

    # If no plan for today, auto-generate it
    if not todays_plan.exists():
        count = generate_study_plan(user)
        if count > 0:
            todays_plan = get_todays_plan(user)
            messages.info(request, f"📅 Study timetable generated with {count} study sessions!")

    # ── Subject Progress for Cards ─────────────────
    subject_progress = []
    for subject in subjects:
        subject_progress.append({
            'subject': subject,
            'progress': subject.get_progress(),
            'total_topics': subject.topics.count(),
            'completed': subject.topics.filter(is_completed=True).count(),
        })

    context = {
        'total_subjects': Subject.objects.filter(user=user).count(),
        'total_topics': total_topics,
        'completed_topics': completed_topics,
        'pending_topics': pending_topics,
        'progress_percent': progress_percent,
        'nearest_exam': nearest_exam,
        'all_exams': all_exams,
        'todays_plan': todays_plan,
        'subject_progress': subject_progress,
        'today': timezone.now().date(),
    }

    return render(request, 'planner/dashboard.html', context)


# ═══════════════════════════════════════════════════
# SUBJECT VIEWS — CRUD operations for subjects
# ═══════════════════════════════════════════════════

@login_required
def subject_list_view(request):
    """Display all subjects for the logged-in user."""
    subjects = Subject.objects.filter(user=request.user)

    # Add progress info to each subject
    subject_data = []
    for subject in subjects:
        try:
            exam = subject.exam
            days_left = exam.days_remaining()
        except Exam.DoesNotExist:
            exam = None
            days_left = None

        subject_data.append({
            'subject': subject,
            'progress': subject.get_progress(),
            'total_topics': subject.topics.count(),
            'completed': subject.topics.filter(is_completed=True).count(),
            'exam': exam,
            'days_left': days_left,
        })

    return render(request, 'planner/subjects.html', {'subject_data': subject_data})


@login_required
def subject_add_view(request):
    """Add a new subject."""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)  # Don't save yet
            subject.user = request.user          # Link to current user
            subject.save()
            messages.success(request, f"Subject '{subject.name}' added successfully!")
            return redirect('subject_list')
        else:
            messages.error(request, "Please check the form fields.")
    else:
        form = SubjectForm()

    return render(request, 'planner/subject_form.html', {
        'form': form,
        'title': 'Add Subject',
        'button_text': 'Add Subject',
    })


@login_required
def subject_edit_view(request, pk):
    """Edit an existing subject — user can only edit THEIR subjects."""
    # get_object_or_404 returns 404 if not found instead of crashing
    subject = get_object_or_404(Subject, pk=pk, user=request.user)

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, f"Subject '{subject.name}' updated!")
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)

    return render(request, 'planner/subject_form.html', {
        'form': form,
        'title': f'Edit Subject: {subject.name}',
        'button_text': 'Save Changes',
        'subject': subject,
    })


@login_required
def subject_delete_view(request, pk):
    """Delete a subject and all its associated topics."""
    subject = get_object_or_404(Subject, pk=pk, user=request.user)

    if request.method == 'POST':
        name = subject.name
        subject.delete()  # Also deletes related topics (CASCADE)
        messages.success(request, f"Subject '{name}' deleted.")
        return redirect('subject_list')

    # Show confirmation page
    return render(request, 'planner/confirm_delete.html', {
        'item': subject,
        'item_type': 'Subject',
        'cancel_url': 'subject_list',
    })


# ═══════════════════════════════════════════════════
# TOPIC VIEWS — CRUD operations for topics
# ═══════════════════════════════════════════════════

@login_required
def topic_list_view(request, subject_pk):
    """Display all topics for a specific subject."""
    subject = get_object_or_404(Subject, pk=subject_pk, user=request.user)
    topics = subject.topics.all()

    return render(request, 'planner/topics.html', {
        'subject': subject,
        'topics': topics,
        'progress': subject.get_progress(),
    })


@login_required
def topic_add_view(request, subject_pk):
    """Add a topic to a specific subject."""
    subject = get_object_or_404(Subject, pk=subject_pk, user=request.user)

    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.subject = subject  # Link to subject
            topic.save()
            messages.success(request, f"Topic '{topic.name}' added to {subject.name}!")
            return redirect('topic_list', subject_pk=subject.pk)
    else:
        form = TopicForm()

    return render(request, 'planner/topic_form.html', {
        'form': form,
        'subject': subject,
        'title': f'Add Topic to {subject.name}',
        'button_text': 'Add Topic',
    })


@login_required
def topic_edit_view(request, pk):
    """Edit an existing topic."""
    topic = get_object_or_404(Topic, pk=pk, subject__user=request.user)

    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, f"Topic '{topic.name}' updated!")
            return redirect('topic_list', subject_pk=topic.subject.pk)
    else:
        form = TopicForm(instance=topic)

    return render(request, 'planner/topic_form.html', {
        'form': form,
        'subject': topic.subject,
        'title': f'Edit Topic: {topic.name}',
        'button_text': 'Save Changes',
    })


@login_required
def topic_delete_view(request, pk):
    """Delete a topic."""
    topic = get_object_or_404(Topic, pk=pk, subject__user=request.user)

    if request.method == 'POST':
        subject_pk = topic.subject.pk
        name = topic.name
        topic.delete()
        messages.success(request, f"Topic '{name}' deleted.")
        return redirect('topic_list', subject_pk=subject_pk)

    return render(request, 'planner/confirm_delete.html', {
        'item': topic,
        'item_type': 'Topic',
        'cancel_url': None,
        'subject_pk': topic.subject.pk,
    })


@login_required
@require_POST
def topic_toggle_view(request, pk):
    """
    Toggle topic completion status via AJAX.
    Called when user clicks the checkbox in topic list.
    Returns JSON response for JavaScript to update UI.
    """
    topic = get_object_or_404(Topic, pk=pk, subject__user=request.user)

    # Toggle the completion status
    if topic.is_completed:
        topic.is_completed = False
        topic.completed_at = None
        topic.save()
        status = 'incomplete'
    else:
        topic.mark_complete()
        status = 'complete'

    # Recalculate subject progress
    progress = topic.subject.get_progress()

    # Return JSON for JavaScript to consume
    return JsonResponse({
        'success': True,
        'status': status,
        'is_completed': topic.is_completed,
        'progress': progress,
        'topic_name': topic.name,
    })


# ═══════════════════════════════════════════════════
# EXAM VIEWS — Manage exam dates
# ═══════════════════════════════════════════════════

@login_required
def exam_list_view(request):
    """Show all exams for the user."""
    today = timezone.now().date()
    upcoming_exams = Exam.objects.filter(user=request.user, exam_date__gte=today).order_by('exam_date')
    past_exams = Exam.objects.filter(user=request.user, exam_date__lt=today).order_by('-exam_date')

    return render(request, 'planner/exams.html', {
        'upcoming_exams': upcoming_exams,
        'past_exams': past_exams,
        'today': today,
    })


@login_required
def exam_add_view(request):
    """Add an exam date for a subject."""
    if request.method == 'POST':
        form = ExamForm(request.user, request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.user = request.user
            exam.save()
            messages.success(request, f"Exam for '{exam.subject.name}' scheduled on {exam.exam_date}!")
            # Auto-regenerate timetable when new exam is added
            generate_study_plan(request.user)
            return redirect('exam_list')
        else:
            messages.error(request, "Please check the form.")
    else:
        form = ExamForm(request.user)

    return render(request, 'planner/exam_form.html', {
        'form': form,
        'title': 'Add Exam Date',
        'button_text': 'Schedule Exam',
    })


@login_required
def exam_edit_view(request, pk):
    """Edit an exam date."""
    exam = get_object_or_404(Exam, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ExamForm(request.user, request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam date updated!")
            generate_study_plan(request.user)  # Regenerate plan
            return redirect('exam_list')
    else:
        form = ExamForm(request.user, instance=exam)

    return render(request, 'planner/exam_form.html', {
        'form': form,
        'title': f'Edit Exam: {exam.subject.name}',
        'button_text': 'Update Exam',
    })


@login_required
def exam_delete_view(request, pk):
    """Delete an exam entry."""
    exam = get_object_or_404(Exam, pk=pk, user=request.user)

    if request.method == 'POST':
        name = exam.subject.name
        exam.delete()
        messages.success(request, f"Exam for '{name}' removed.")
        return redirect('exam_list')

    return render(request, 'planner/confirm_delete.html', {
        'item': exam,
        'item_type': 'Exam',
        'cancel_url': 'exam_list',
    })


# ═══════════════════════════════════════════════════
# TIMETABLE VIEW — Show full generated plan
# ═══════════════════════════════════════════════════

@login_required
def timetable_view(request):
    """
    Show the full auto-generated study timetable.
    Also allows manual regeneration.
    """
    user = request.user
    today = timezone.now().date()

    # Handle regenerate request
    if request.method == 'POST':
        count = generate_study_plan(user)
        messages.success(request, f"Timetable regenerated! {count} study sessions planned.")
        return redirect('timetable')

    # Fetch plans for next 14 days, grouped by date
    plan_entries = StudyPlan.objects.filter(
        user=user,
        plan_date__gte=today,
        plan_date__lte=today + timedelta(days=14)
    ).select_related('topic__subject').order_by('plan_date', 'topic__subject__name')

    # Group plans by date for display
    grouped_plans = defaultdict(list)
    for entry in plan_entries:
        grouped_plans[entry.plan_date].append(entry)

    # Convert to sorted list of (date, tasks) tuples
    timetable_data = sorted(grouped_plans.items())

    return render(request, 'planner/timetable.html', {
        'timetable_data': timetable_data,
        'today': today,
        'total_sessions': plan_entries.count(),
    })


@login_required
@require_POST
def plan_toggle_view(request, pk):
    """Toggle a study plan task as done/undone via AJAX."""
    plan = get_object_or_404(StudyPlan, pk=pk, user=request.user)
    plan.is_done = not plan.is_done
    plan.save()

    return JsonResponse({
        'success': True,
        'is_done': plan.is_done,
    })


# ═══════════════════════════════════════════════════
# PROGRESS VIEW — Detailed progress analytics
# ═══════════════════════════════════════════════════

@login_required
def progress_view(request):
    """Show detailed progress analytics per subject."""
    user = request.user
    subjects = Subject.objects.filter(user=user)

    progress_data = []
    for subject in subjects:
        total = subject.topics.count()
        completed = subject.topics.filter(is_completed=True).count()
        pending = total - completed

        # Breakdown by difficulty
        easy_total = subject.topics.filter(difficulty='easy').count()
        easy_done = subject.topics.filter(difficulty='easy', is_completed=True).count()
        medium_total = subject.topics.filter(difficulty='medium').count()
        medium_done = subject.topics.filter(difficulty='medium', is_completed=True).count()
        hard_total = subject.topics.filter(difficulty='hard').count()
        hard_done = subject.topics.filter(difficulty='hard', is_completed=True).count()

        try:
            exam = subject.exam
            days_left = exam.days_remaining()
        except Exam.DoesNotExist:
            exam = None
            days_left = None

        progress_data.append({
            'subject': subject,
            'total': total,
            'completed': completed,
            'pending': pending,
            'percent': subject.get_progress(),
            'easy_total': easy_total, 'easy_done': easy_done,
            'medium_total': medium_total, 'medium_done': medium_done,
            'hard_total': hard_total, 'hard_done': hard_done,
            'exam': exam,
            'days_left': days_left,
        })

    # Overall stats
    all_topics = Topic.objects.filter(subject__user=user)
    overall_total = all_topics.count()
    overall_completed = all_topics.filter(is_completed=True).count()
    overall_percent = round((overall_completed / overall_total) * 100) if overall_total > 0 else 0

    return render(request, 'planner/progress.html', {
        'progress_data': progress_data,
        'overall_total': overall_total,
        'overall_completed': overall_completed,
        'overall_percent': overall_percent,
    })
