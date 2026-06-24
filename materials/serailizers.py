from rest_framework import serializers

from materials.models import Course, Lesson
from materials.validators import LessonVideoUrlValidator
from users.models import Subscription


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ['owner']
        validators = [
            LessonVideoUrlValidator(field="video_link"),
        ]


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    subscription = serializers.BooleanField(read_only=True)

    class Meta:
        model = Course
        fields = ('title', 'description', 'owner', 'subscription', 'preview_image', 'lesson_count', 'lessons')
        read_only_fields = ['owner', 'subscription']

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def get_subscription(self, obj):
        owner_pk = self.request.user.pk
        if not Subscription.objects.filter(owner=owner_pk,course=obj.pk).exists():
            return False
        return True
