from rest_framework import serializers

from materials.models import Course


class CoursePkValidator:
    """Валидатор проверяет, что курс существует."""
    def __init__(self, field):
        self.field = field

    def __call__(self, attrs):
        course_id = attrs.get(self.field)
        if not Course.objects.filter(pk=course_id).exists():
            raise serializers.ValidationError("Курс с таким id не найден.")
        return course_id
