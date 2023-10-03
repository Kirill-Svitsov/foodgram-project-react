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
        if view.action == 'create':
            return True
        return request.user and request.user.is_authenticated


# class CustomIngredientPermission(permissions.BasePermission):
#
#     def has_permission(self, request, view):
#         if request.method == 'GET':
#             return True
#         return request.user and request.user.is_superuser
