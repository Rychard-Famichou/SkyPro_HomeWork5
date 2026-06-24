from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=30, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена курса")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")
    preview_image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name="Превью")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = 'Курсы'


youtube_validator = RegexValidator(
    regex=r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$',
    message='Введите корректную ссылку на видеоролик YouTube.'
)


class Lesson(models.Model):
    title = models.CharField(max_length=30, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена урока")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")
    preview_image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name="Превью")
    video_link = models.URLField(
        blank=True,
        null=True,
        validators=[youtube_validator],
        verbose_name="Ссылка на YouTube",
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="Курс")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = 'Уроки'
