from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tag')
urlpatterns = router.urls
