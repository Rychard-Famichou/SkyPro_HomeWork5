from rest_framework import viewsets, generics

from materials.models import Course, Lesson
from materials.serailizers import CourseSerializer, LessonSerializer
from users.permissions import IsOwner, IsModerator


# Create your views here.
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsOwner]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.detail:
            return Course.objects.all()
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve', 'update', 'partial_update']:
            return [(IsOwner | IsModerator)()]
        return super().get_permissions()


class LessonBaseView(generics.GenericAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        if self.request.user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class LessonCreateAPIView(LessonBaseView, generics.CreateAPIView):

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(LessonBaseView, generics.ListAPIView):
    permission_classes = [IsOwner | IsModerator]


class LessonRetrieveAPIView(LessonBaseView, generics.RetrieveAPIView):
    permission_classes = [IsOwner | IsModerator]


class LessonUpdateAPIView(LessonBaseView, generics.UpdateAPIView):
    permission_classes = [IsOwner | IsModerator]


class LessonDestroyAPIView(LessonBaseView, generics.DestroyAPIView):
    pass
