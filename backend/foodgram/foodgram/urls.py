from django.contrib import admin
from django.urls import path, include
# from recipes.views import CustomTokenView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
