from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from materials.validators import CourseOrLessonValidator
from users.models import CustomUser, Payment, Subscription
from users.validators import CoursePkValidator


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(label="Почта")
    password = serializers.CharField(write_only=True, label="Пароль")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)

    def validate(self, attrs):
        attrs[self.username_field] = attrs.get('email')
        return super().validate(attrs)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('status', 'owner', 'course', 'lesson', 'amount', 'date', 'method', 'stripe_session_id', 'link')
        read_only_fields = ['owner', 'amount', 'stripe_session_id', 'link', 'date']
        validators = [
            CourseOrLessonValidator()
        ]

    def create(self, validated_data):
        course = validated_data.get('course')
        lesson = validated_data.get('lesson')

        if course:
            validated_data['amount'] = course.price
        elif lesson:
            validated_data['amount'] = lesson.price

        return super().create(validated_data)


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, label="Пароль")
    payments = PaymentSerializer(many=True, read_only=True, label="Платежи")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'payments', 'first_name', 'last_name', 'phone', 'city', 'avatar')

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'phone', 'city', 'avatar']


class SubscriptionSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField()

    class Meta:
        model = Subscription
        fields = ['course_id']
        validators = [
            CoursePkValidator(field="course_id"),
        ]
