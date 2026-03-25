"""
AIStudyPlanner - manage.py
===========================
Django's command-line utility for administrative tasks.
Usage: python manage.py runserver
"""

import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aistudyplanner.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed by running:\n"
            "  pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
