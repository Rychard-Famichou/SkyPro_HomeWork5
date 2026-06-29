from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from materials.models import Course
from users.models import Subscription


@shared_task
def send_course_update_email_task(course_id):
    """Фоновая задача для сбора подписчиков и отправки писем."""
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return f"Курс с ID {course_id} не найден."

    emails = list(Subscription.objects.filter(course=course).values_list('owner__email', flat=True))

    if not emails:
        return f"Нет подписчиков для курса '{course.title}'."

    for email in emails:
        send_mail(
            subject="Обновления",
            message=f"Курс '{course.title}' был обновлён",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email]
        )

    return f"Успешно отправлено {len(emails)} писем для курса '{course.title}'."
