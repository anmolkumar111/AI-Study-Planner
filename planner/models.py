"""
AIStudyPlanner - Django Models
================================
This file defines the database structure (tables).
Each class = one database table.

Relationships:
  User (Django built-in)
    └── Subject (user's subjects)
         └── Topic  (topics within a subject)
         └── Exam   (exam date for the subject)
    └── StudyPlan (auto-generated daily plan)
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ─────────────────────────────────────────────────────────────
# SUBJECT MODEL
# Each student can have multiple subjects (e.g., Maths, AI)
# ─────────────────────────────────────────────────────────────
class Subject(models.Model):
    # Link to the logged-in user (many subjects per user)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')

    # Subject name, e.g., "Artificial Intelligence"
    name = models.CharField(max_length=100)

    # Short description of the subject (optional)
    description = models.TextField(blank=True, null=True)

    # When was this subject added?
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']  # Sort alphabetically

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def get_progress(self):
        """Calculate completion percentage for this subject."""
        total = self.topics.count()
        if total == 0:
            return 0
        completed = self.topics.filter(is_completed=True).count()
        return round((completed / total) * 100)

    def get_pending_topics(self):
        """Return topics not yet completed, ordered by difficulty."""
        difficulty_order = {'hard': 1, 'medium': 2, 'easy': 3}
        topics = list(self.topics.filter(is_completed=False))
        # Sort: hard topics first (higher priority)
        topics.sort(key=lambda t: difficulty_order.get(t.difficulty, 2))
        return topics


# ─────────────────────────────────────────────────────────────
# TOPIC MODEL
# Each subject can have multiple syllabus topics
# ─────────────────────────────────────────────────────────────
class Topic(models.Model):
    # Difficulty choices for study prioritization
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    # Link topic to its subject
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')

    # Topic name, e.g., "Neural Networks"
    name = models.CharField(max_length=200)

    # How hard is this topic?
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )

    # Estimated hours needed to study this topic
    estimated_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0
    )

    # Has the student completed this topic?
    is_completed = models.BooleanField(default=False)

    # When was this topic completed?
    completed_at = models.DateTimeField(blank=True, null=True)

    # When was topic added?
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_completed', 'difficulty']

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.name} [{self.difficulty}]"

    def mark_complete(self):
        """Mark this topic as completed and record the time."""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()


# ─────────────────────────────────────────────────────────────
# EXAM MODEL
# Each subject can have one exam date
# ─────────────────────────────────────────────────────────────
class Exam(models.Model):
    # Link exam to both user AND subject
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exams')
    subject = models.OneToOneField(
        Subject,
        on_delete=models.CASCADE,
        related_name='exam'
    )

    # The date of the exam
    exam_date = models.DateField()

    # Optional notes about the exam (syllabus coverage, etc.)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['exam_date']

    def __str__(self):
        return f"{self.subject.name} exam on {self.exam_date}"

    def days_remaining(self):
        """Calculate how many days until the exam."""
        today = timezone.now().date()
        delta = self.exam_date - today
        return delta.days

    def is_upcoming(self):
        """Return True if exam is in the future."""
        return self.days_remaining() >= 0

    def urgency_label(self):
        """Return urgency level based on days remaining."""
        days = self.days_remaining()
        if days < 0:
            return 'past'
        elif days <= 3:
            return 'critical'
        elif days <= 7:
            return 'urgent'
        elif days <= 14:
            return 'soon'
        else:
            return 'normal'


# ─────────────────────────────────────────────────────────────
# STUDY PLAN MODEL
# Auto-generated daily study tasks
# ─────────────────────────────────────────────────────────────
class StudyPlan(models.Model):
    # Link plan to user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')

    # The date this plan is for
    plan_date = models.DateField()

    # The topic to study on this day
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='study_plans')

    # Suggested hours for that day (portion of estimated_hours)
    suggested_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)

    # Has user marked this plan task as done?
    is_done = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['plan_date', 'topic__subject__name']
        unique_together = ['user', 'plan_date', 'topic']  # No duplicates

    def __str__(self):
        return f"{self.plan_date} → {self.topic.name} ({self.suggested_hours}h)"
