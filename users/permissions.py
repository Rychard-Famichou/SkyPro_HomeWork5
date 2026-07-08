from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Разрешает Модераторам смотреть и менять объекты"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Модераторы").exists()


class IsNotModerator(BasePermission):
    """Разрешает доступ всем, кроме пользователей из группы 'Модераторы'
     создавать и удалять объекты"""

    def has_permission(self, request, view):
        return not request.user.groups.filter(name="Модераторы").exists()


class IsOwner(BasePermission):
    """Разрешает все CRUD действия для владельцев"""

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner", None) == request.user


class IsSelf(BasePermission):
    """Проверка профиля пользователя"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user
