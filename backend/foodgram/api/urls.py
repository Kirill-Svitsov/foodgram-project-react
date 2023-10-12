from rest_framework.routers import DefaultRouter
from django.urls import include, path
from api.views import (
    CustomUserViewSet, RecipeViewSet, IngredientViewSet,
    TagViewSet, ShoppingListViewSet
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'users', CustomUserViewSet, basename='users')
router.register(
    r'shopping-list',
    ShoppingListViewSet,
    basename='shopping-list'
)


urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken"))
]
