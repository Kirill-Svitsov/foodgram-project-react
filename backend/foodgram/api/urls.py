from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet, IngredientViewSet,
    RecipeViewSet, TagViewSet
)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
