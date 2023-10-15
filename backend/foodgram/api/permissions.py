from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Позволяет редактировать рецепты только их авторам.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class AllowAnyForCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create' \
                or request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


# class IsUserOrReadOnly(permissions.BasePermission):
#     """
#     Позволяет редактировать свой собственный профиль,
#      но предотвращает редактирование других пользователей.
#     """
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj == request.user