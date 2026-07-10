from unittest.mock import patch

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.tests import LessonMixin
from users.models import CustomUser, Payment


# Create your tests here.
class AnonimCreateUserTestCase(APITestCase):
    """Класс тестов для не авторизованного пользователя"""

    def setUp(self):
        self.data = {
            "username": "test",
            "email": "test@example.com",
            "password": "testpassword",
        }
        self.user_create_url = reverse("users:user_create")

    def test_user_create(self):
        """Тест создания пользователя"""
        response = self.client.post(self.user_create_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OwnerPaymentCreateTestCase(LessonMixin):

    def setUp(self):
        super().setUp()
        self.data = {
            "owner": self.user.pk,
            "course": self.course.pk,
            "method": "TRANSFER",
        }
        self.payment_create_url = reverse("users:payment_create")

    @patch('users.views.create_stripe_product')
    @patch('users.views.create_stripe_price')
    @patch('users.views.create_stripe_checkout_session')
    def test_payment_create(self, mock_checkout=None, mock_product=None, mock_price=None):
        """Тест создание платежа с мокированием Stripe"""
        class MockSession:
            id = 'test_session_id'
            url = 'https://test-stripe-link.com'

        mock_checkout.return_value = MockSession()
        mock_product.return_value = 'test_product_id'
        mock_price.return_value = 'test_price_id'

        response = self.client.post(self.payment_create_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OwnerSubscribeTestCase(LessonMixin):

    def setUp(self):
        super().setUp()
        self.data = {"course_id": self.course.pk}
        self.subscription_toggle_url = reverse("users:subscription_toggle")

    def test_subscription_toggle_create(self):
        """Тест создания/удаления подписки"""
        response = self.client.post(self.subscription_toggle_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.subscription_toggle_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaymentMixin(LessonMixin):

    def setUp(self):
        super().setUp()
        self.payment = Payment.objects.create(owner=self.user, course=self.course, amount=100.00, method="TRANSFER")
        self.user_detail_url = reverse("users:user_detail", kwargs={"pk": self.user.pk})
        self.user_patch_url = reverse("users:user_update", kwargs={"pk": self.user.pk})
        self.user_delete_url = reverse("users:user_delete", kwargs={"pk": self.user.pk})


class OwnerTestCase(PaymentMixin):
    """Класс для тестов пользователя-владельца курсов и уроков."""

    def setUp(self):
        super().setUp()

    def test_user_detail_by_owner(self):
        """Тест просмотр деталей пользователя"""
        response = self.client.get(self.user_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("payments", response.data)

    def test_user_patch_by_owner(self):
        """Тест изменения никнейма"""
        self.data = {"username": "test"}
        response = self.client.patch(self.user_patch_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "test")

    # def test_user_delete_by_owner(self):
    #     """ Тест удаления пользователя """
    #     response = self.client.delete(self.user_delete_url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())


class UserTestCase(PaymentMixin):
    """Класс для тестов обычного пользователя."""

    def setUp(self):
        super().setUp()
        self.owner_id = self.user.pk
        revizor = CustomUser.objects.create_user(
            username="revizor", email="revizor@example.com", password="revizorpassword"
        )
        self.client.force_authenticate(user=revizor)

    def test_user_detail_by_user(self):
        """Тест просмотр деталей пользователя для обычного пользователя"""
        response = self.client.get(self.user_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("payments", response.data)

    def test_user_patch_by_user(self):
        """Тест изменения никнейма для обычного пользователя"""
        self.data = {"username": "test"}
        response = self.client.patch(self.user_patch_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_by_user(self):
        """Тест удаления пользователя для обычного пользователя"""
        response = self.client.delete(self.user_delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CustomUser.objects.filter(pk=self.owner_id).exists())


class ModerTestCase(PaymentMixin):
    """Класс для тестов модератора"""

    def setUp(self):
        super().setUp()
        self.owner_id = self.user.pk
        moder = CustomUser.objects.create_user(username="moder", email="moder@example.com", password="moderpassword")
        moder_group, created = Group.objects.get_or_create(name="Модераторы")
        moder.groups.add(moder_group)
        self.client.force_authenticate(user=moder)

    def test_user_patch_by_moder(self):
        """Тест изменения никнейма для модератора"""
        self.data = {"username": "test"}
        response = self.client.patch(self.user_patch_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_by_moder(self):
        """Тест просмотр деталей пользователя для модератора"""
        response = self.client.get(self.user_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("payments", response.data)

    def test_user_delete_by_moder(self):
        """Тест удаления пользователя для модератора"""
        response = self.client.delete(self.user_delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CustomUser.objects.filter(pk=self.owner_id).exists())
