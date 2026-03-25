"""
AIStudyPlanner - Project URL Configuration
==========================================
This file defines the top-level URL routing.
All 'planner' app URLs are included under the root path.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin panel (optional, useful for debugging)
    path('admin/', admin.site.urls),

    # Include all URLs from the 'planner' app
    path('', include('planner.urls')),
]
