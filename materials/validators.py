import re
from urllib.parse import urlparse

from django.core.validators import RegexValidator
from rest_framework import serializers


class CourseOrLessonValidator:
    """Валидатор проверяет, что выбрано строго что-то одно: либо курс, либо урок."""

    def __call__(self, attrs):
        course = attrs.get("course")
        lesson = attrs.get("lesson")

        if not course and not lesson:
            raise serializers.ValidationError("Выберите либо курс, либо урок, за который производится оплата.")
        if course and lesson:
            raise serializers.ValidationError(
                "Платеж не может быть одновременно и за курс, и за урок. " "Выберите что-то одно."
            )


class LessonVideoUrlValidator:
    """Валидатор проверяет, что ссылка на видео действительно Youtube.com"""

    def __init__(self, field):
        self.field = field

    def __call__(self, attrs):
        url = attrs.get(self.field)

        if not url:
            return attrs

        youtube_regex = re.compile(r"^(https?://)?(www\.)?(youtube\.com)/.+$", re.IGNORECASE)

        parsed_url = urlparse(url)

        if not parsed_url.netloc or not youtube_regex.match(url):
            raise serializers.ValidationError(
                {self.field: f"Ссылка в поле" f" '{self.field}' должна вести на youtube.com"}
            )

        return url


youtube_validator = RegexValidator(
    regex=r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$",
    message="Введите корректную ссылку на видеоролик YouTube.",
)
