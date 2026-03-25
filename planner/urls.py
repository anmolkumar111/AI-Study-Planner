"""
AIStudyPlanner - URL Patterns (App-level)
==========================================
Maps URL paths to view functions.

Structure:
  /                → redirect to dashboard
  /register/       → signup page
  /login/          → login page
  /logout/         → logout
  /dashboard/      → main dashboard
  /subjects/       → list of subjects
  /subjects/add/   → add subject
  /subjects/<pk>/edit/   → edit subject
  /subjects/<pk>/delete/ → delete subject
  /subjects/<pk>/topics/ → list topics
  ... and more
"""

from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # ── Root redirect ──────────────────────────────────────────
    path('', lambda r: redirect('dashboard'), name='home'),

    # ── Authentication ─────────────────────────────────────────
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # ── Dashboard ──────────────────────────────────────────────
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # ── Subjects ───────────────────────────────────────────────
    path('subjects/',              views.subject_list_view,   name='subject_list'),
    path('subjects/add/',          views.subject_add_view,    name='subject_add'),
    path('subjects/<int:pk>/edit/',   views.subject_edit_view,   name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete_view, name='subject_delete'),

    # ── Topics (nested under subjects) ─────────────────────────
    path('subjects/<int:subject_pk>/topics/',        views.topic_list_view,   name='topic_list'),
    path('subjects/<int:subject_pk>/topics/add/',    views.topic_add_view,    name='topic_add'),
    path('topics/<int:pk>/edit/',                    views.topic_edit_view,   name='topic_edit'),
    path('topics/<int:pk>/delete/',                  views.topic_delete_view, name='topic_delete'),
    path('topics/<int:pk>/toggle/',                  views.topic_toggle_view, name='topic_toggle'),  # AJAX

    # ── Exams ──────────────────────────────────────────────────
    path('exams/',              views.exam_list_view,   name='exam_list'),
    path('exams/add/',          views.exam_add_view,    name='exam_add'),
    path('exams/<int:pk>/edit/',   views.exam_edit_view,   name='exam_edit'),
    path('exams/<int:pk>/delete/', views.exam_delete_view, name='exam_delete'),

    # ── Timetable ──────────────────────────────────────────────
    path('timetable/', views.timetable_view, name='timetable'),
    path('plans/<int:pk>/toggle/', views.plan_toggle_view, name='plan_toggle'),  # AJAX

    # ── Progress ───────────────────────────────────────────────
    path('progress/', views.progress_view, name='progress'),
]
