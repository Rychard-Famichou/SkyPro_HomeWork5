from rest_framework import viewsets, generics
from rest_framework.exceptions import NotAuthenticated

from materials.models import Course, Lesson
from materials.paginators import CoursePaginator, LessonPaginator
from materials.serailizers import CourseSerializer, LessonSerializer
from users.permissions import IsOwner, IsModerator, IsNotModerator


# Create your views here.
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise NotAuthenticated("Пользователь не авторизован.")
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.detail:
            return Course.objects.all()
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            return [IsNotModerator()]
        if self.action == 'destroy':
            return [IsNotModerator(), IsOwner()]
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            return [(IsOwner | IsModerator)()]
        return super().get_permissions()


class LessonBaseView(generics.GenericAPIView):
    """ Базовый класс для генериков урока """
    serializer_class = LessonSerializer
    permission_classes = [IsOwner]
    queryset = Lesson.objects.all()


class LessonCreateAPIView(LessonBaseView, generics.CreateAPIView):
    permission_classes = [IsNotModerator]

    def perform_create(self, serializer):
        if self.request.user.is_anonymous:
            raise NotAuthenticated("Пользователь не авторизован.")
        serializer.save(owner=self.request.user)


class LessonListAPIView(LessonBaseView, generics.ListAPIView):
    pagination_class = LessonPaginator
    permission_classes = [IsOwner | IsModerator]

    def get_queryset(self):
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveAPIView(LessonBaseView, generics.RetrieveAPIView):
    permission_classes = [IsOwner | IsModerator]


class LessonUpdateAPIView(LessonBaseView, generics.UpdateAPIView):
    permission_classes = [IsOwner | IsModerator]


class LessonDestroyAPIView(LessonBaseView, generics.DestroyAPIView):
    pass
