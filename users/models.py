from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models


# Create your models here.
class CustomUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Поле Email обязательно для заполнения')
        if not username:
            raise ValueError('Поле Username обязательно для заполнения')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=25, unique=True, verbose_name="Никнейм")
    email = models.EmailField(max_length=50, unique=True, verbose_name="Почта")
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True, verbose_name="Телефон")
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="Город")
    avatar = models.ImageField(upload_to='avatars/%Y/%m', blank=True, null=True, verbose_name="Аватар")
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Фамилия")

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Статус персонала")
    is_superuser = models.BooleanField(default=False, verbose_name="Статус суперпользователя")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class Payment(models.Model):
    class MethodChoices(models.TextChoices):
        CASH = "CASH", "Наличные"
        TRANSFER = "TRANSFER", "Перевод"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments', verbose_name="Пользователь")
    course = models.ForeignKey('materials.Course', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Курс")
    lesson = models.ForeignKey('materials.Lesson', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Урок")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    method = models.CharField(choices=MethodChoices.choices, max_length=20, verbose_name="Метод оплаты")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        paid_item = self.course if self.course else self.lesson
        return f"Платеж от {self.user} за {paid_item}"

    def clean(self):
        super().clean()
        if not self.course and not self.lesson:
            raise ValidationError("Выберите либо курс, либо урок, за который производится оплата.")
        if self.course and self.lesson:
            raise ValidationError("Платеж не может быть одновременно и за курс, и за урок. Выберите что-то одно.")
