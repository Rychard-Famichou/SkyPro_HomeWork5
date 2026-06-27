from django.conf import settings
from django.db import models

from materials.services import check_update_time
from materials.validators import youtube_validator


# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=30, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена курса")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")
    preview_image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name="Превью")
    updated = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = 'Курсы'

    def save(self, *args, **kwargs):
        should_send_mail = False

        if self.pk:
            old_course = Course.objects.filter(pk=self.pk).values('updated').first()
            if old_course:
                should_send_mail = check_update_time(old_course['updated'])

        super().save(*args, **kwargs)

        if should_send_mail:
            from .tasks import send_course_update_email_task
            send_course_update_email_task.delay(self.pk)


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.course:
            course = self.course
            course.save(update_fields=['updated'])

    def delete(self, *args, **kwargs):
        course = self.course
        super().delete(*args, **kwargs)
        if course:
            course.save(update_fields=['updated'])
