"""
AIStudyPlanner - WSGI Configuration
=====================================
Standard Django WSGI entry point for development server.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aistudyplanner.settings')
application = get_wsgi_application()
