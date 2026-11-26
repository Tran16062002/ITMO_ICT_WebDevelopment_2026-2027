from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),

    # Djoser: регистрация, токены, текущий пользователь
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    # Браузерный интерфейс DRF (кнопка Log in)
    path('api-auth/', include('rest_framework.urls')),

    # API приложения
    path('api/', include('library_app.urls')),
]
