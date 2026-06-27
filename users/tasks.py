from celery import shared_task

from users.models import CustomUser
from users.services import check_active_days


@shared_task(name='users.tasks.toggle_active')
def toggle_active():
    users = CustomUser.objects.filter(is_active=True)
    for user in users:
        if check_active_days(user.last_login):
            user.is_active = False
            user.save(update_fields=['is_active'])
