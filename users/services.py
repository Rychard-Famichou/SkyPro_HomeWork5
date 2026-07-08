from datetime import timedelta
from functools import wraps

import stripe
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import APIException, ValidationError

stripe.api_key = settings.STRIPE_SECRET_KEY


def check_stripe_error(func):
    """Декоратор, который ловит ошибки сервиса Stripe"""

    @wraps(func)
    def _wrapped_view(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except stripe.error.InvalidRequestError as e:
            raise ValidationError(
                {"stripe_error": f"Некорректные данные: {e.user_message}"}
            )
        except stripe.error.StripeError as e:
            raise APIException(f"Ошибка платежного шлюза Stripe: {e.user_message}")

    return _wrapped_view


@check_stripe_error
def create_stripe_product(name):
    product = stripe.Product.create(name=name)
    return product.id


@check_stripe_error
def create_stripe_price(product_id, amount):
    unit_amount = int(amount * 100)
    price = stripe.Price.create(
        currency="usd",
        unit_amount=unit_amount,
        product=product_id,
    )
    return price.id


@check_stripe_error
def create_stripe_checkout_session(price_id):
    session = stripe.checkout.Session.create(
        success_url="https://example.com/success",
        line_items=[{"price": price_id, "quantity": 1}],
        mode="payment",
        payment_method_types=["card"],
    )
    return session


@check_stripe_error
def retrieve_stripe_checkout_session(session_id):
    session = stripe.checkout.Session.retrieve(
        session_id,
    )
    status = session["payment_status"]
    return status


def check_active_days(last_login):
    """Проверяет, прошло ли более 31 дня с последнего входа."""
    if not last_login:
        return True
    return timezone.now() - last_login >= timedelta(days=31)
