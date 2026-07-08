from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Установка переменной окружения для настроек проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создание экземпляра объекта Celery
app = Celery("config")

# Загрузка настроек из файла Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# # ПРИНУДИТЕЛЬНОЕ ОТКЛЮЧЕНИЕ КОМАНДЫ 'HELLO' (RESP3) ДЛЯ CELERY
# app.conf.broker_transport_options = {
#     'protocol': 2,
#     'global_keyprefix': 'celery:'
# }
# app.conf.result_backend_transport_options = {
#     'protocol': 2
# }
# app.conf.redis_backend_transport_options = {
#     'protocol': 2
# }

# Автоматическое обнаружение и регистрация задач из файлов tasks.py в приложениях Django
app.autodiscover_tasks()
