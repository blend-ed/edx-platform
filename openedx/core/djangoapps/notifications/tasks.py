"""
This file contains celery tasks for notifications.
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from edx_django_utils.monitoring import set_code_owner_attribute

from common.djangoapps.student.models import CourseEnrollment
from openedx.core.djangoapps.notifications.models import NotificationPreference, CONFIG_VERSION, \
    NOTIFICATION_PREFERENCE_CONFIG

logger = get_task_logger(__name__)


@shared_task(bind=True, ignore_result=True)
@set_code_owner_attribute
@transaction.atomic
def create_notification_preferences_for_courses(self, course_ids):
    """
    This task creates Notification Preferences for users in courses.
    """
    logger.info('Running task create_notification_preferences')
    newly_created = 0
    outdated = 0
    for course_id in course_ids:
        enrollments = CourseEnrollment.objects.filter(course_id=course_id, is_active=True)
        logger.info(f'Found {enrollments.count()} enrollments for course {course_id}')
        logger.info(f'Creating Notification Preferences for course {course_id}')
        for enrollment in enrollments:
            notification_preference, created = NotificationPreference.objects.get_or_create(
                user=enrollment.user, course_id=course_id
            )
            if created:
                newly_created += 1
            if notification_preference.config_version != CONFIG_VERSION:
                outdated += 1
                notification_preference.notification_preference_config = NOTIFICATION_PREFERENCE_CONFIG
                notification_preference.config_version = CONFIG_VERSION
                notification_preference.save()

        logger.info(
            f'NotificationPreference back-fill completed for course {course_id}.\n'
            f'Newly created preferences: {newly_created}.\n'
            f'Outdated preferences updated: {outdated}'
        )
    logger.info(
        f'Completed task create_notification_preferences'
    )
