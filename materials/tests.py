from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import CustomUser


# Create your tests here.
class OwnerMixin(APITestCase):
    """Базовый класс для тестов,
    авторизирует пользователя - владельца курсов и уроков."""

    @classmethod
    def setUpTestData(cls):
        # В тестах users тест создание пользователя успешен
        super().setUpTestData()
        cls.user = CustomUser.objects.create_user(
            username="owner", email="owner@example.com", password="ownerpassword"
        )

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        self.courses_list_url = reverse("materials:courses-list")
        self.lesson_create_url = reverse("materials:lesson_create")


class CourseCreateTestCase(OwnerMixin):
    def setUp(self):
        super().setUp()
        self.data = {
            "title": "Test Course",
            "description": "Test Course Description",
            "owner": self.user.pk,
            "price": 100.00,
        }

    def test_course_post_by_owner(self):
        """Создание курса"""
        response = self.client.post(self.courses_list_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CourseMixin(OwnerMixin):
    """Миксин класс для тестов, добавляет созданный курс."""

    def setUp(self):
        # В тестах materials тест создание курса успешен
        super().setUp()
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Course Description",
            owner=self.user,
            price=100.00,
        )
        self.course_detail_url = reverse("materials:courses-detail", kwargs={"pk": self.course.pk})


class LessonCreateTestCase(CourseMixin):
    def setUp(self):
        super().setUp()
        self.data = {
            "title": "Test Lesson",
            "description": "This is a test lesson",
            "course": self.course.pk,
            "video_link": "https://www.youtube.com/?app=desktop&gl=PL&hl=pl",
        }

    def test_lesson_post_by_owner(self):
        """Создание урока с валидатором ссылки"""
        response = self.client.post(self.lesson_create_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LessonMixin(CourseMixin):
    """Миксин класс для тестов, добавляет созданные уроки к созданному курсу."""

    def setUp(self):
        # В тестах materials тест создание урока успешен
        super().setUp()
        self.lesson = Lesson.objects.create(
            title="Test Lesson",
            description="Test Lesson",
            owner=self.user,
            course=self.course,
            price=100.00,
        )
        self.lesson2 = Lesson.objects.create(
            title="Test Lesson 2",
            description="Test Lesson",
            owner=self.user,
            course=self.course,
            price=100.00,
        )
        self.lesson_list_url = reverse("materials:lesson_list")
        self.lesson_detail_url = reverse("materials:lesson_detail", kwargs={"pk": self.lesson.pk})
        self.lesson_patch_url = reverse("materials:lesson_update", kwargs={"pk": self.lesson.pk})
        self.lesson_put_url = reverse("materials:lesson_update", kwargs={"pk": self.lesson2.pk})
        self.lesson_delete_url = reverse("materials:lesson_delete", kwargs={"pk": self.lesson2.pk})


class LessonRUDTestCase(LessonMixin):
    def setUp(self):
        super().setUp()

    def test_lesson_list_by_owner(self):
        """Просмотр списка уроков с пагинатором"""
        response = self.client.get(self.lesson_list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_lesson_detail_by_owner(self):
        """Просмотр деталей урока"""
        response = self.client.get(self.lesson_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Lesson")

    def test_lesson_patch_by_owner(self):
        """Изменение урока"""
        data_patch = {"title": "Patched Lesson"}
        response = self.client.patch(self.lesson_patch_url, data_patch, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Patched Lesson")

    def test_lesson_put_by_owner(self):
        """Замена урока"""
        data_put = {
            "title": "Lesson for delete",
            "description": "Wrong Lesson",
            "course": self.course.pk,
        }
        response = self.client.put(self.lesson_put_url, data_put, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson2.refresh_from_db()
        self.assertEqual(self.lesson2.title, "Lesson for delete")

    def test_lesson_delete_by_owner(self):
        """Удаление урока"""
        response = self.client.delete(self.lesson_delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson2.pk).exists())


class CourseRUDTestCase(LessonMixin):
    def setUp(self):
        super().setUp()
        self.course2 = Course.objects.create(
            title="Test Course 2",
            description="Test Course Description",
            owner=self.user,
            price=100.00,
        )
        self.course_detail_url2 = reverse("materials:courses-detail", kwargs={"pk": self.course2.pk})

    def test_course_list_by_owner(self):
        """Просмотр списка курсов с пагинатором"""
        response = self.client.get(self.courses_list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_course_detail_by_owner(self):
        """Просмотр деталей курса с подсчётом уроков"""
        response = self.client.get(self.course_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Course")
        self.assertEqual(response.data["lesson_count"], 2)

    def test_course_patch_by_owner(self):
        """Изменение курса"""
        data_patch = {"title": "Patched Course"}
        response = self.client.patch(self.course_detail_url, data_patch, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Patched Course")

    def test_course_put_by_owner(self):
        """Замена курса"""
        data_put = {
            "title": "Course for delete",
            "description": "Wrong Course",
            "price": 100.00,
        }
        response = self.client.put(self.course_detail_url2, data_put, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course2.refresh_from_db()
        self.assertEqual(self.course2.title, "Course for delete")

    def test_course_delete_by_owner(self):
        """Удаление курса"""
        response = self.client.delete(self.course_detail_url2, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course2.pk).exists())

    def test_course_lesson_delete_by_owner(self):
        """Удаление курса c уроками"""
        response = self.client.delete(self.course_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())
        self.assertFalse(Lesson.objects.filter(pk=self.lesson2.pk).exists())


class UserTestCase(LessonMixin):
    """Класс тестов для обычного пользователя и чужих объектов"""

    def setUp(self):
        super().setUp()
        revizor = CustomUser.objects.create_user(
            username="revizor", email="revizor@example.com", password="revizorpassword"
        )
        self.client.force_authenticate(user=revizor)

    def test_lesson_list_by_user(self):
        """Просмотр списка уроков с пагинатором для обычного пользователя"""
        response = self.client.get(self.lesson_list_url, format="json")
        self.assertEqual(response.data, {"count": 0, "next": None, "previous": None, "results": []})

    def test_lesson_detail_by_user(self):
        """Просмотр деталей урока для обычного пользователя"""
        response = self.client.get(self.lesson_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_patch_by_user(self):
        """Изменение урока для обычного пользователя"""
        data_patch = {"title": "Hacked Lesson"}
        response = self.client.patch(self.lesson_patch_url, data_patch, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.lesson.refresh_from_db()
        self.assertNotEqual(self.lesson.title, "Hacked Lesson")

    def test_lesson_put_by_user(self):
        """Замена урока для обычного пользователя"""
        data_put = {
            "title": "Lesson for delete",
            "description": "Wrong Lesson",
            "course": self.course.pk,
            "price": 100.00,
        }
        response = self.client.put(self.lesson_put_url, data_put, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.lesson2.refresh_from_db()
        self.assertNotEqual(self.lesson2.title, "Lesson for delete")

    def test_lesson_delete_by_user(self):
        """Удаление урока для обычного пользователя"""
        response = self.client.delete(self.lesson_delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(pk=self.lesson2.pk).exists())

    def test_course_list_by_user(self):
        """Просмотр списка курсов с пагинатором для обычного пользователя"""
        response = self.client.get(self.courses_list_url, format="json")
        self.assertEqual(response.data, {"count": 0, "next": None, "previous": None, "results": []})

    def test_course_detail_by_user(self):
        """Просмотр деталей курса с подсчётом уроков для обычного пользователя"""
        response = self.client.get(self.course_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_patch_by_user(self):
        """Изменение курса для обычного пользователя"""
        data_patch = {"title": "Hacked Course"}
        response = self.client.patch(self.course_detail_url, data_patch, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.course.refresh_from_db()
        self.assertNotEqual(self.course.title, "Hacked Course")

    def test_course_put_by_user(self):
        """Замена курса для обычного пользователя"""
        data_put = {"title": "Course for delete", "description": "Wrong Course"}
        response = self.client.put(self.course_detail_url, data_put, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.course.refresh_from_db()
        self.assertNotEqual(self.course.title, "Course for delete")

    def test_course_delete_by_user(self):
        """Удаление курса для обычного пользователя"""
        response = self.client.delete(self.course_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Course.objects.filter(pk=self.course.pk).exists())


class ModerTestCase(LessonMixin):
    """Класс тестов для модератора"""

    def setUp(self):
        super().setUp()
        moder = CustomUser.objects.create_user(username="moder", email="moder@example.com", password="moderpassword")
        moder_group, created = Group.objects.get_or_create(name="Модераторы")
        moder.groups.add(moder_group)
        self.client.force_authenticate(user=moder)

    def test_course_post_by_moder(self):
        """Создание курса для модератора"""
        self.data = {
            "title": "Moder Course",
            "description": "Test Course Description",
            "owner": self.user.pk,
            "price": 100.00,
        }
        response = self.client.post(self.courses_list_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_post_by_moder(self):
        """Создание урока для модератора"""
        self.data = {
            "title": "Moder Lesson",
            "description": "This is a test lesson",
            "course": self.course.pk,
            "price": 100.00,
        }
        response = self.client.post(self.lesson_create_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_list_by_moder(self):
        """Просмотр списка уроков с пагинатором для модератора"""
        response = self.client.get(self.lesson_list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_lesson_detail_by_moder(self):
        """Просмотр деталей урока для модератора"""
        response = self.client.get(self.lesson_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Lesson")

    def test_lesson_patch_by_moder(self):
        """Изменение урока для модератора"""
        data_patch = {"title": "Patched Lesson"}
        response = self.client.patch(self.lesson_patch_url, data_patch, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Patched Lesson")

    def test_lesson_put_by_moder(self):
        """Замена урока для модератора"""
        data_put = {
            "title": "Lesson for delete",
            "description": "Wrong Lesson",
            "course": self.course.pk,
            "price": 100.00,
        }
        response = self.client.put(self.lesson_put_url, data_put, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson2.refresh_from_db()
        self.assertEqual(self.lesson2.title, "Lesson for delete")

    def test_lesson_delete_by_moder(self):
        """Удаление урока для модератора"""
        response = self.client.delete(self.lesson_delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(pk=self.lesson2.pk).exists())

    def test_course_list_by_moder(self):
        """Просмотр списка курсов с пагинатором для модератора"""
        response = self.client.get(self.courses_list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_course_detail_by_moder(self):
        """Просмотр деталей курса с подсчётом уроков для модератора"""
        response = self.client.get(self.course_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Course")
        self.assertEqual(response.data["lesson_count"], 2)

    def test_course_patch_by_moder(self):
        """Изменение курса для модератора"""
        data_patch = {"title": "Patched Course"}
        response = self.client.patch(self.course_detail_url, data_patch, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Patched Course")

    def test_course_put_by_moder(self):
        """Замена курса для модератора"""
        data_put = {
            "title": "Course for delete",
            "description": "Wrong Course",
            "price": 100.00,
        }
        response = self.client.put(self.course_detail_url, data_put, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Course for delete")

    def test_course_delete_by_moder(self):
        """Удаление курса для модератора"""
        response = self.client.delete(self.course_detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Course.objects.filter(pk=self.course.pk).exists())


class AnonimTestCase(CourseMixin):
    """Класс для тестов не авторизованных пользователей"""

    def setUp(self):
        super().setUp()
        self.client.logout()

    def test_course_post_by_guest(self):
        """Создание курса анонимом"""
        self.data = {
            "title": "Guest Course",
            "description": "Test Course Description",
            "owner": self.user.pk,
            "price": 100.00,
        }
        response = self.client.post(self.courses_list_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_post_by_guest(self):
        """Создание урока анонимом"""
        self.data = {
            "title": "Guest Lesson",
            "description": "This is a test lesson",
            "course": self.course.pk,
            "price": 100.00,
        }
        response = self.client.post(self.lesson_create_url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
