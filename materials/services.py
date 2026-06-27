from datetime import timedelta

from django.utils import timezone


def check_update_time(updated_time):
    """Проверяет, прошло ли более 4 часов с момента последнего обновления."""
    if not updated_time:
        return True
    return timezone.now() - updated_time >= timedelta(hours=4)
