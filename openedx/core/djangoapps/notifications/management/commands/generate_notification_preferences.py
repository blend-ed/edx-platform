"""
Management command for creating Notification Preferences for users in course.
"""

import logging

from django.core.management.base import BaseCommand

from openedx.core.djangoapps.notifications.tasks import create_notification_preferences_for_courses

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Invoke with:

        python manage.py [lms|cms] generate_notification_preferences [course_id] [course_id] ...
    """
    help = (
        "Back-fill missing notification preferences. This will queue a celery task to"
        "create notification preferences for all active enrollments in the courses provided."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'course_ids',
            help='course_ids seperated by space for which to create Notification Preferences.',
            nargs='*'
        )

    def handle(self, *args, **options):
        course_ids = options['course_ids']
        create_notification_preferences_for_courses.delay(course_ids)
