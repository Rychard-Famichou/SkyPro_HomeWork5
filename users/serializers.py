from django.db.models import Model
from rest_framework import serializers

from users.models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('user', 'course', 'lesson', 'amount', 'date', 'method')


class CustomUserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'payments', 'phone', 'city', 'first_name', 'last_name', 'avatar')
