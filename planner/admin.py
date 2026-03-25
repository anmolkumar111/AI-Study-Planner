"""
AIStudyPlanner - Django Admin Configuration
============================================
Register models to appear in Django's admin panel at /admin/
This allows easy data management during development.
"""

from django.contrib import admin
from .models import Subject, Topic, Exam, StudyPlan


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['user']
    search_fields = ['name']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'difficulty', 'estimated_hours', 'is_completed']
    list_filter = ['difficulty', 'is_completed']
    search_fields = ['name']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['subject', 'user', 'exam_date']
    list_filter = ['exam_date']


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_date', 'topic', 'suggested_hours', 'is_done']
    list_filter = ['plan_date', 'is_done']
