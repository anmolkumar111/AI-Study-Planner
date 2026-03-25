"""
AIStudyPlanner - Timetable Generator
======================================
This module contains the core AI logic for generating
a personalized daily study plan.

Algorithm:
1. Fetch all incomplete topics for the user
2. Sort subjects by exam urgency (nearest exam first)
3. Distribute topics across available days before the exam
4. Allocate daily study hours (max 6h/day)
5. Save generated plan to StudyPlan model

This is the "AI" part of the project — smart scheduling!
"""

from django.utils import timezone
from datetime import timedelta, date
from .models import Subject, Topic, Exam, StudyPlan


def generate_study_plan(user):
    """
    Main function to generate a personalized study timetable.

    Args:
        user: The logged-in Django User object

    Returns:
        int: Number of study plan entries created
    """

    # Step 1: Clear old (future) plan entries for fresh generation
    today = timezone.now().date()
    StudyPlan.objects.filter(user=user, plan_date__gte=today, is_done=False).delete()

    # Step 2: Fetch all subjects with upcoming exams
    subjects_with_exams = []
    for subject in Subject.objects.filter(user=user):
        try:
            exam = subject.exam
            days_left = (exam.exam_date - today).days
            if days_left >= 0:  # Only future exams
                pending_topics = subject.get_pending_topics()
                if pending_topics:  # Only if there are topics to study
                    subjects_with_exams.append({
                        'subject': subject,
                        'exam': exam,
                        'days_left': days_left,
                        'topics': pending_topics,
                    })
        except Exam.DoesNotExist:
            # Subject has no exam date — skip for now
            pass

    # Step 3: Also include subjects WITHOUT exam dates (lower priority)
    subjects_without_exams = []
    for subject in Subject.objects.filter(user=user):
        try:
            subject.exam  # Check if exam exists
        except Exam.DoesNotExist:
            pending_topics = subject.get_pending_topics()
            if pending_topics:
                subjects_without_exams.append({
                    'subject': subject,
                    'exam': None,
                    'days_left': 999,  # Far in future (low priority)
                    'topics': pending_topics,
                })

    # Sort subjects by exam urgency — nearest exam first
    all_subjects = sorted(
        subjects_with_exams + subjects_without_exams,
        key=lambda x: x['days_left']
    )

    if not all_subjects:
        return 0  # Nothing to plan

    # Step 4: Build a day-by-day schedule
    MAX_HOURS_PER_DAY = 6.0   # Max study hours per day
    plan_entries = []
    created_count = 0

    # Create a schedule spanning the next 30 days
    schedule = {}  # {date: hours_used}
    for i in range(30):
        schedule_date = today + timedelta(days=i)
        schedule[schedule_date] = 0.0  # Start with 0 hours used

    # Step 5: Assign topics to days based on priority
    for subject_data in all_subjects:
        topics = subject_data['topics']
        exam_days_left = subject_data['days_left']

        # Determine the date range for this subject's study window
        # Study only on days BEFORE the exam
        study_window = min(exam_days_left, 30) if exam_days_left < 999 else 30

        for topic in topics:
            hours_needed = float(topic.estimated_hours)
            hours_remaining = hours_needed

            # Walk through days and assign hours
            for i in range(study_window):
                if hours_remaining <= 0:
                    break

                current_date = today + timedelta(days=i)
                hours_available = MAX_HOURS_PER_DAY - schedule[current_date]

                if hours_available <= 0:
                    continue  # Day is full, try next day

                # Assign as many hours as possible on this day
                hours_to_assign = min(hours_remaining, hours_available, 3.0)  # Max 3h per topic per day
                schedule[current_date] += hours_to_assign
                hours_remaining -= hours_to_assign

                # Queue this plan entry for saving
                plan_entries.append({
                    'topic': topic,
                    'plan_date': current_date,
                    'suggested_hours': round(hours_to_assign, 1),
                })

    # Step 6: Save all plan entries to the database (bulk create)
    for entry in plan_entries:
        obj, created = StudyPlan.objects.get_or_create(
            user=user,
            plan_date=entry['plan_date'],
            topic=entry['topic'],
            defaults={'suggested_hours': entry['suggested_hours']}
        )
        if created:
            created_count += 1

    return created_count


def get_todays_plan(user):
    """
    Fetch the study plan for today only.

    Args:
        user: Logged-in User object

    Returns:
        QuerySet of today's StudyPlan entries
    """
    today = timezone.now().date()
    return StudyPlan.objects.filter(
        user=user,
        plan_date=today
    ).select_related('topic__subject').order_by('is_done', 'topic__subject__name')


def get_nearest_exam(user):
    """
    Find the nearest upcoming exam for the user.

    Args:
        user: Logged-in User object

    Returns:
        Exam object or None
    """
    today = timezone.now().date()
    return Exam.objects.filter(
        user=user,
        exam_date__gte=today
    ).order_by('exam_date').first()
