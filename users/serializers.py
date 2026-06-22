from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from materials.validators import CourseOrLessonValidator
from users.models import CustomUser, Payment, Subscription
from users.validators import CoursePkValidator


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)

    def validate(self, attrs):
        attrs[self.username_field] = attrs.get('email')
        return super().validate(attrs)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('owner', 'course', 'lesson', 'amount', 'date', 'method')
        read_only_fields = ['owner']
        validators = [
            CourseOrLessonValidator()
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

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
