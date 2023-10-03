from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import *

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'users/me', CustomUserViewSet, basename='current-user')
router.register(r'users/set_password', CustomUserViewSet, basename='set_password')
router.register(r'shopping-list', ShoppingListViewSet, basename='shopping-list')


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken"))
]
