from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'owner', None) == request.user

class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
