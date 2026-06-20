from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import CustomUser, Payment


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
        fields = ('user', 'course', 'lesson', 'amount', 'date', 'method')
        read_only_fields = ['user']

    def validate(self, attrs):
        course = attrs.get('course', self.instance.course if self.instance else None)
        lesson = attrs.get('lesson', self.instance.lesson if self.instance else None)

        if not course and not lesson:
            raise serializers.ValidationError(
                "Выберите либо курс, либо урок, за который производится оплата."
            )
        if course and lesson:
            raise serializers.ValidationError(
                "Платеж не может быть одновременно и за курс, и за урок. Выберите что-то одно."
            )

        return attrs


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
