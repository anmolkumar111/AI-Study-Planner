"""
AIStudyPlanner - Project URL Configuration
==========================================
This file defines the top-level URL routing.
All 'planner' app URLs are included under the root path.
"""

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    # Django admin panel (optional, useful for debugging)
    path('admin/', admin.site.urls),

    # Include all URLs from the 'planner' app
    path('', include('planner.urls')),

    # Manually serve static files (for Vercel deployment troubleshooting)
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0]}),
]
